"""
Dynamic Question Selection Engine for Instant Mechanic.
Selects the single most diagnostic, highest-value unanswered question from Neon PostgreSQL,
evaluated dynamically against conversation facts and active candidate issues.
Eliminates hardcoded question scripts and redundant questions.
"""
from typing import Dict, Any, List, Optional
from chatbot.models import DiagnosticQuestion, DiagnosticOption
from chatbot.logic.condition_evaluator import evaluate_condition, get_nested_fact
from chatbot.logic.candidate_engine import evaluate_candidates


def select_next_question(
    state: Dict[str, Any],
    facts_dict: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Evaluates available diagnostic questions against current conversation state.
    Returns:
      - question_dict: {
            "key": "...",
            "question": "...",
            "category": "...",
            "target_fact_key": "...",
            "options": [{"value": "...", "label": "...", "aliases": [...]}]
        } or None if no further questions are needed.
    """
    if facts_dict is None:
        from chatbot.logic.state_tracker import state_to_facts_dict
        facts_dict = state_to_facts_dict(state)

    asked_keys = set(state.get("asked_questions", []))

    # Evaluate current candidates to see how close we are to diagnosis
    candidates, clear_sep, top_cand = evaluate_candidates(facts_dict)

    # If we already have strong separation and high confidence, don't ask redundant questions
    if clear_sep and top_cand and top_cand["score"] >= 80.0:
        return None

    # Fetch active questions from Neon PostgreSQL
    questions = DiagnosticQuestion.objects.filter(active=True).prefetch_related('options').order_by('-priority', 'id')

    if not questions.exists():
        return None

    candidate_questions = []

    for q in questions:
        # 1. Skip if already asked
        if q.key in asked_keys:
            continue

        # 2. Skip if the target fact has already been populated in state
        target_val = get_nested_fact(facts_dict, q.target_fact_key) if q.target_fact_key else None
        if target_val is not None and target_val != "" and target_val != []:
            continue

        # 3. Check declarative relevance rule
        if q.relevance_rule:
            if not evaluate_condition(q.relevance_rule, facts_dict):
                continue

        # 4. Calculate dynamic score/information gain
        priority_score = float(q.priority)

        # Safety-critical questions get an immediate priority boost
        if q.safety_critical:
            priority_score += 50.0

        # Information Gain: Check how many candidate issues rely on this question's target fact
        if q.target_fact_key and candidates:
            top_candidates = candidates[:3]
            for cand in top_candidates:
                priority_score += cand["score"] * 0.2

        candidate_questions.append((priority_score, q))

    if not candidate_questions:
        return None

    # Sort questions by dynamic priority descending
    candidate_questions.sort(key=lambda item: item[0], reverse=True)
    best_q = candidate_questions[0][1]

    # Format options for QuickReplies
    options_list = []
    for opt in best_q.options.filter(active=True).order_by('order', 'id'):
        options_list.append({
            "value": opt.value,
            "label": opt.label,
            "aliases": opt.aliases or []
        })

    return {
        "key": best_q.key,
        "question": best_q.question_text,
        "category": best_q.category,
        "target_fact_key": best_q.target_fact_key,
        "options": options_list
    }

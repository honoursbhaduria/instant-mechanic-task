"""
Data-driven Candidate Engine for Instant Mechanic.
Queries DiagnosticIssue and DiagnosticCriterion from Neon PostgreSQL and computes
issue plausibility scores dynamically using the declarative Condition Evaluator.
"""
from typing import Dict, Any, List, Tuple, Optional
from chatbot.models import DiagnosticIssue
from chatbot.logic.condition_evaluator import evaluate_single_rule


def evaluate_candidates(facts: Dict[str, Any], min_score: float = 15.0) -> Tuple[List[Dict[str, Any]], bool, Optional[Dict[str, Any]]]:
    """
    Evaluates all active DiagnosticIssues from Neon PostgreSQL against the conversation facts.
    Returns:
      - candidates: sorted list of candidate issues with normalized confidence scores (0-100)
      - clear_separation: boolean indicating if top candidate has high confidence and strong separation
      - top_candidate: the leading candidate issue or None
    """
    issues = DiagnosticIssue.objects.filter(active=True).prefetch_related('criteria', 'system')

    scored_candidates = []

    for issue in issues:
        criteria = issue.criteria.all()
        if not criteria:
            continue

        positive_weight_total = 0.0
        positive_earned = 0.0
        negative_penalty = 0.0
        matched_criteria = []

        for crit in criteria:
            if crit.polarity == 'positive':
                positive_weight_total += crit.weight

            rule = {
                "field": crit.field,
                "operator": crit.operator,
                "expected_value": crit.expected_value
            }
            if evaluate_single_rule(rule, facts):
                matched_criteria.append(crit.description or f"{crit.field} {crit.operator} {crit.expected_value}")
                if crit.polarity == 'positive':
                    positive_earned += crit.weight
                elif crit.polarity == 'negative':
                    negative_penalty += crit.weight

        if positive_weight_total <= 0:
            continue

        # Net score after negative deductions
        net_score = max(0.0, positive_earned - negative_penalty)
        normalized_score = round(min(100.0, (net_score / positive_weight_total) * 100.0), 1)

        if normalized_score >= min_score:
            scored_candidates.append({
                "id": issue.slug,
                "slug": issue.slug,
                "issue": issue.name,
                "name": issue.name,
                "system": issue.system.slug if issue.system else "general",
                "system_name": issue.system.name if issue.system else "General",
                "score": normalized_score,
                "confidence": normalized_score,
                "severity": issue.severity,
                "service": issue.service,
                "recommendation": issue.recommendation,
                "safety_warning": issue.safety_warning,
                "reasoning": issue.reasoning_template,
                "matched_criteria": matched_criteria,
            })

    # Fallback to local mechanical rules if DB has no issues (e.g. before initial seed or during test runner)
    if not scored_candidates and not issues.exists():
        from chatbot.logic.mechanical_rules import evaluate_rules, is_case_clear
        rule_cands = evaluate_rules(facts)
        is_clear, top_cand = is_case_clear(rule_cands)
        return rule_cands, is_clear, top_cand

    # Sort descending by score
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)

    top_candidate = scored_candidates[0] if scored_candidates else None
    second_candidate = scored_candidates[1] if len(scored_candidates) > 1 else None

    clear_separation = False
    if top_candidate:
        top_score = top_candidate["score"]
        is_percentage = top_score > 1.0
        thresh = 75.0 if is_percentage else 0.75
        diff_thresh = 20.0 if is_percentage else 0.20

        if top_score >= thresh:
            if second_candidate is None:
                clear_separation = True
            elif (top_score - second_candidate["score"]) >= diff_thresh:
                clear_separation = True

    return scored_candidates, clear_separation, top_candidate

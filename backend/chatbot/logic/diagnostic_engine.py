"""
Automotive Diagnostic Engine for Instant Mechanic.
Orchestrates diagnosis pipeline:
1. Duplicate diagnosis & caching check (0 AI calls).
2. Deterministic mechanical rule evaluation.
3. Decision: Clear case -> local rule result (0 AI calls).
             Ambiguous/complex case -> Gemini reasoning (1 AI call).
4. Robust fallback on Gemini rate-limit/failure.
5. Persistent Diagnosis record creation and cost tracking.
"""
from typing import Dict, Any, Tuple, Optional
from decimal import Decimal
from chatbot.models import Conversation, Diagnosis
from .mechanical_rules import evaluate_rules, is_case_clear
from .gemini_service import call_gemini_diagnostic_reasoning
from .state_tracker import compute_case_fingerprint, update_conversation_state, get_initial_state


def perform_diagnosis(
    conversation: Conversation,
    media_info: Optional[str] = None,
    force_reevaluate: bool = False
) -> Tuple[Diagnosis, bool]:
    """
    Executes diagnosis for conversation.
    Returns: (diagnosis_model_instance, is_duplicate_or_cached)
    """
    state = conversation.state or {}

    # If state was uninitialized (e.g. direct ORM creation in legacy tests), populate from user messages
    if not state or not state.get("problem", {}).get("symptom") or not state.get("problem", {}).get("noise_type"):
        if not state:
            state = get_initial_state()
        for msg in conversation.messages.filter(role='user'):
            state = update_conversation_state(state, msg.content)
        if conversation.vehicle_info and not state.get("vehicle", {}).get("model"):
            state = update_conversation_state(state, conversation.vehicle_info)
        conversation.state = state

    fingerprint = state.get("fingerprint") or compute_case_fingerprint(state)

    # 1. Duplicate Diagnosis / Cache Guard (Section 28 & 29)
    if not force_reevaluate and not state.get("is_stale_diagnosis", False):
        existing_diag = conversation.diagnoses.first()
        if existing_diag and (existing_diag.fingerprint == fingerprint or not fingerprint):
            return existing_diag, True

    # 2. Evaluate candidate mechanical issues dynamically from knowledge base
    candidates = []
    is_clear = False
    top_candidate = None
    try:
        from chatbot.logic.candidate_engine import evaluate_candidates
        from chatbot.logic.state_tracker import state_to_facts_dict
        facts_dict = state_to_facts_dict(state)
        candidates, is_clear, top_candidate = evaluate_candidates(facts_dict)
    except Exception:
        candidates = []

    if not candidates:
        candidates = evaluate_rules(state)
        is_clear, top_candidate = is_case_clear(candidates)

    vehicle_str = ""
    v_make = state.get("vehicle", {}).get("make", "")
    v_model = state.get("vehicle", {}).get("model", "")
    v_year = state.get("vehicle", {}).get("year", "")
    parts = [str(p) for p in [v_year, v_make, v_model] if p]
    if parts:
        vehicle_str = " ".join(parts)
    elif conversation.vehicle_info:
        vehicle_str = conversation.vehicle_info

    diag_data: Dict[str, Any] = {}
    source = "rules"

    # 3. Decision: Clear vs Ambiguous Case
    if is_clear and top_candidate:
        # Clear deterministic diagnosis
        source = "rules"
        diag_data = {
            "diagnosis": top_candidate["issue"],
            "severity": top_candidate["severity"],
            "confidence": "high",
            "service": top_candidate["service"],
            "recommendation": top_candidate["service"],
            "reasoning": top_candidate["reasoning"],
            "safety_warning": top_candidate["safety_warning"]
        }
    else:
        # Ambiguous or complex case: Call Gemini with compact structured context
        compact_context = {
            "vehicle": {
                "make": v_make,
                "model": v_model,
                "year": v_year
            },
            "problem": state.get("problem", {}),
            "conditions": state.get("conditions", {}),
            "observations": state.get("observations", {}),
            "candidate_issues": [c["issue"] for c in candidates[:4]]
        }

        ai_result, usage_metrics = call_gemini_diagnostic_reasoning(compact_context, media_info)

        # Update conversation Gemini usage counters
        if usage_metrics["calls"] > 0:
            conversation.gemini_calls += usage_metrics["calls"]
            conversation.input_tokens += usage_metrics["input_tokens"]
            conversation.output_tokens += usage_metrics["output_tokens"]
            conversation.estimated_cost += Decimal(str(usage_metrics["estimated_cost"]))

            # Log to AIUsageLog
            try:
                from chatbot.models import AIUsageLog
                AIUsageLog.objects.create(
                    conversation=conversation,
                    model="gemini-2.5-flash",
                    prompt_tokens=usage_metrics["input_tokens"],
                    candidate_tokens=usage_metrics["output_tokens"],
                    total_tokens=usage_metrics["input_tokens"] + usage_metrics["output_tokens"],
                    latency_ms=0,
                    status="success" if ai_result else "fallback"
                )
            except Exception:
                pass

        if ai_result:
            source = "gemini"
            diag_data = {
                "diagnosis": ai_result["possible_issue"],
                "severity": ai_result["severity"],
                "confidence": ai_result["confidence"],
                "service": ai_result["recommended_service"],
                "recommendation": ai_result["recommended_service"],
                "reasoning": ai_result["reasoning"],
                "safety_warning": ai_result["safety_warning"]
            }
        else:
            # Fallback to top rule candidate or generic automotive inspection
            source = "fallback"
            if top_candidate:
                diag_data = {
                    "diagnosis": top_candidate["issue"],
                    "severity": top_candidate["severity"],
                    "confidence": "medium",
                    "service": top_candidate["service"],
                    "recommendation": top_candidate["service"],
                    "reasoning": top_candidate["reasoning"],
                    "safety_warning": top_candidate["safety_warning"]
                }
            else:
                diag_data = {
                    "diagnosis": f"Unspecified Mechanical Component Wear on {vehicle_str or 'vehicle'}",
                    "severity": "medium",
                    "confidence": "medium",
                    "service": "Comprehensive 40-Point Diagnostic Inspection",
                    "recommendation": "Comprehensive 40-Point Diagnostic Inspection",
                    "reasoning": "Reported symptoms require hands-on physical inspection of steering, suspension, and drivetrain components.",
                    "safety_warning": "Have vehicle checked by a certified technician prior to highway driving."
                }

    # 4. Save Diagnosis in database
    symptoms_summary = f"{state.get('problem', {}).get('symptom', '')} {state.get('problem', {}).get('noise_type', '')}".strip()
    if not symptoms_summary:
        symptoms_summary = "Vehicle operational anomaly"

    diagnosis = Diagnosis.objects.create(
        conversation=conversation,
        symptoms=symptoms_summary,
        diagnosis=diag_data["diagnosis"],
        severity=diag_data["severity"],
        confidence=diag_data.get("confidence", "medium"),
        recommendation=diag_data["recommendation"],
        service=diag_data["service"],
        reasoning=diag_data["reasoning"],
        safety_warning=diag_data["safety_warning"],
        vehicle=vehicle_str,
        source=source,
        fingerprint=fingerprint
    )

    # 5. Update Conversation state
    state["diagnostic_status"] = "diagnosed"
    state["is_stale_diagnosis"] = False
    state["fingerprint"] = fingerprint
    conversation.state = state
    conversation.save()

    return diagnosis, False

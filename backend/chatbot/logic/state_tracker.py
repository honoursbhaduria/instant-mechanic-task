"""
Structured Conversation State Tracker for Instant Mechanic.
Maintains persisted JSON-compatible state per conversation, handles
delta updates from extracted facts, tracks answered fields, and detects
material changes that invalidate previous diagnoses.
"""
import hashlib
import json
from typing import Dict, Any, List, Optional

from .fact_extractor import extract_facts
from .symptom_classifier import classify_symptom
from .mechanical_rules import evaluate_rules


def get_initial_state() -> Dict[str, Any]:
    """Generates the initial structured conversation state schema."""
    return {
        "vehicle": {
            "make": "",
            "model": "",
            "year": None
        },
        "problem": {
            "system": "",
            "symptom": "",
            "noise_type": "",
            "primary_category": ""
        },
        "conditions": {
            "speed": "",
            "turning": None,
            "direction": "",
            "braking": None,
            "acceleration": None,
            "engine_state": "",
            "road_condition": ""
        },
        "observations": {
            "increases_on_sharp_turn": None,
            "vibration": None,
            "warning_light": None,
            "starter_state": "",
            "smoke_color": "",
            "location": "",
            "confirmed_last_question": None
        },
        "media": [],
        "candidate_issues": [],
        "asked_questions": [],
        "answered_fields": [],
        "diagnostic_status": "collecting",  # collecting, ready, diagnosing, diagnosed, booked
        "question_count": 0,
        "is_stale_diagnosis": False,
        "fingerprint": ""
    }


def compute_case_fingerprint(state: Dict[str, Any]) -> str:
    """Produces a deterministic hash of the automotive diagnostic evidence."""
    signature = {
        "veh": state.get("vehicle", {}),
        "prob": {k: v for k, v in state.get("problem", {}).items() if k != "primary_category"},
        "cond": state.get("conditions", {}),
        "obs": {k: v for k, v in state.get("observations", {}).items() if k != "confirmed_last_question"}
    }
    raw = json.dumps(signature, sort_keys=True)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]


def merge_state_updates(state: Dict[str, Any], delta: Dict[str, Any], last_question_field: Optional[str] = None) -> Dict[str, Any]:
    """
    Merges newly extracted facts into the existing state without overwriting
    established facts with empty values.
    """
    # 1. Update Vehicle
    veh_delta = delta.get("vehicle", {})
    if veh_delta.get("make"):
        state["vehicle"]["make"] = veh_delta["make"]
    if veh_delta.get("model"):
        state["vehicle"]["model"] = veh_delta["model"]
    if veh_delta.get("year"):
        state["vehicle"]["year"] = veh_delta["year"]

    # 2. Update Problem
    prob_delta = delta.get("problem", {})
    if prob_delta.get("system") and not state["problem"].get("system"):
        state["problem"]["system"] = prob_delta["system"]
    if prob_delta.get("symptom") and not state["problem"].get("symptom"):
        state["problem"]["symptom"] = prob_delta["symptom"]
    if prob_delta.get("noise_type"):
        state["problem"]["noise_type"] = prob_delta["noise_type"]

    # 3. Update Conditions
    cond_delta = delta.get("conditions", {})
    if cond_delta.get("speed"):
        state["conditions"]["speed"] = cond_delta["speed"]
    if cond_delta.get("turning") is not None:
        state["conditions"]["turning"] = cond_delta["turning"]
    if cond_delta.get("direction"):
        state["conditions"]["direction"] = cond_delta["direction"]
    if cond_delta.get("braking") is not None:
        state["conditions"]["braking"] = cond_delta["braking"]
    if cond_delta.get("acceleration") is not None:
        state["conditions"]["acceleration"] = cond_delta["acceleration"]
    if cond_delta.get("engine_state"):
        state["conditions"]["engine_state"] = cond_delta["engine_state"]
    if cond_delta.get("road_condition"):
        state["conditions"]["road_condition"] = cond_delta["road_condition"]

    # 4. Update Observations
    obs_delta = delta.get("observations", {})
    if obs_delta.get("increases_on_sharp_turn") is not None:
        state["observations"]["increases_on_sharp_turn"] = obs_delta["increases_on_sharp_turn"]
    if obs_delta.get("vibration") is not None:
        state["observations"]["vibration"] = obs_delta["vibration"]
    if obs_delta.get("warning_light") is not None:
        state["observations"]["warning_light"] = obs_delta["warning_light"]
    if obs_delta.get("starter_state"):
        state["observations"]["starter_state"] = obs_delta["starter_state"]
    if obs_delta.get("smoke_color"):
        state["observations"]["smoke_color"] = obs_delta["smoke_color"]
    if obs_delta.get("temperature_state"):
        state["observations"]["temperature_state"] = obs_delta["temperature_state"]
    if obs_delta.get("location"):
        state["observations"]["location"] = obs_delta["location"]

    # Contextual interpretation if user answered a specific prompt with confirmation/negation:
    confirmed = obs_delta.get("confirmed_last_question")
    if last_question_field and confirmed is not None:
        if last_question_field == "sharp_or_normal_turn":
            state["observations"]["increases_on_sharp_turn"] = confirmed
        elif last_question_field == "vibration":
            state["observations"]["vibration"] = confirmed
        elif last_question_field == "speed" and confirmed:
            if not state["conditions"].get("speed"):
                state["conditions"]["speed"] = "low"
        elif last_question_field == "when_occurs" and confirmed:
            if state["problem"].get("primary_category") == "steering_noise":
                state["conditions"]["turning"] = True
            elif state["problem"].get("primary_category") == "brake_noise":
                state["conditions"]["braking"] = True

    return state


def update_conversation_state(
    current_state: Optional[Dict[str, Any]],
    user_text: str,
    last_question_field: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main state progression pipeline:
    1. Loads or initializes state.
    2. Runs deterministic fact extraction on user message.
    3. Merges facts into state.
    4. Categorizes symptom domain.
    5. Calculates mechanical rule candidates.
    6. Refreshes answered fields and case fingerprint.
    """
    if not current_state or not isinstance(current_state, dict) or "problem" not in current_state:
        state = get_initial_state()
    else:
        state = current_state

    old_fingerprint = state.get("fingerprint") or ""

    # Extract facts from current message
    facts = extract_facts(user_text, state)

    # Merge facts
    state = merge_state_updates(state, facts, last_question_field)

    # Classify symptom
    cat = classify_symptom(user_text, state)
    if cat:
        state["problem"]["primary_category"] = cat
        if not state["problem"].get("symptom"):
            state["problem"]["symptom"] = cat

    # Evaluate candidate mechanical issues dynamically from knowledge base
    try:
        from chatbot.logic.candidate_engine import evaluate_candidates
        facts_dict = state_to_facts_dict(state)
        eval_result = evaluate_candidates(facts_dict)
        if isinstance(eval_result, tuple):
            candidates = eval_result[0]
        elif isinstance(eval_result, list):
            candidates = eval_result
        else:
            candidates = []
    except Exception:
        candidates = evaluate_rules(state)

    if not isinstance(candidates, list):
        candidates = []

    state["candidate_issues"] = [
        {"issue": c.get("issue", c.get("name", "")), "score": c.get("score", 0.0)}
        for c in candidates[:4] if isinstance(c, dict)
    ]

    # Calculate answered fields list
    answered = []
    if state["vehicle"].get("model") or state["vehicle"].get("make"):
        answered.append("vehicle")
    if state["problem"].get("noise_type"):
        answered.append("noise_type")
    if state["problem"].get("symptom"):
        answered.append("symptom")
    if state["conditions"].get("turning") is not None or state["conditions"].get("braking") is not None:
        answered.append("when_occurs")
    if state["conditions"].get("speed"):
        answered.append("speed")
    if state["conditions"].get("direction"):
        answered.append("turning_direction")
    if state["observations"].get("increases_on_sharp_turn") is not None:
        answered.append("sharp_or_normal_turn")
    if state["observations"].get("location"):
        answered.append("front_or_rear")
    if state["observations"].get("vibration") is not None:
        answered.append("vibration")
    if state["observations"].get("starter_state"):
        answered.append("crank_or_no_crank")
    if state["conditions"].get("road_condition"):
        answered.append("road_condition")
    if state["observations"].get("warning_light") is not None and state["observations"].get("warning_light") is not False:
        answered.append("which_light")

    state["answered_fields"] = answered

    # Update fingerprint and detect state invalidation
    new_fingerprint = compute_case_fingerprint(state)
    if state.get("diagnostic_status") == "diagnosed" and old_fingerprint and old_fingerprint != new_fingerprint:
        # User supplied new meaningful evidence after previous diagnosis
        state["is_stale_diagnosis"] = True
        state["diagnostic_status"] = "ready"

    state["fingerprint"] = new_fingerprint
    return state


def state_to_facts_dict(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms hierarchical conversation state into a normalized facts dictionary
    compatible with declarative condition evaluation and diagnostic criteria.
    """
    facts: Dict[str, Any] = {}
    veh = state.get("vehicle", {}) or {}
    prob = state.get("problem", {}) or {}
    cond = state.get("conditions", {}) or {}
    obs = state.get("observations", {}) or {}

    # Vehicle facts
    if veh.get("make"):
        facts["vehicle.make"] = veh["make"]
        facts["vehicle_make"] = veh["make"]
    if veh.get("model"):
        facts["vehicle.model"] = veh["model"]
        facts["vehicle_model"] = veh["model"]
    if veh.get("year"):
        facts["vehicle.year"] = veh["year"]
        facts["vehicle_year"] = veh["year"]

    # Problem facts
    if prob.get("system"):
        facts["system.slug"] = prob["system"]
    if prob.get("noise_type"):
        facts["noise_type"] = prob["noise_type"]
        facts["problem.noise_type"] = prob["noise_type"]
        if prob.get("primary_category") in ["starting_problem", "battery_problem"]:
            facts["symptom.slug"] = "starting_problem"
        else:
            facts["symptom.slug"] = f"{prob['noise_type']}_noise"
    elif prob.get("symptom"):
        facts["symptom.slug"] = prob["symptom"]

    # Category fallbacks for system and symptom
    cat = prob.get("primary_category")
    category_to_system = {
        "overheating": "cooling",
        "starting_problem": "electrical",
        "battery_problem": "electrical",
        "ac_problem": "air_conditioning",
        "steering_noise": "steering",
        "brake_noise": "braking",
        "suspension_noise": "suspension",
        "engine_noise": "engine",
        "coolant_leak": "cooling",
        "oil_leak": "engine",
        "vibration": "wheels_tyres",
        "smoke": "exhaust",
    }
    if not facts.get("system.slug") and cat in category_to_system:
        facts["system.slug"] = category_to_system[cat]
    if not facts.get("symptom.slug") and cat:
        facts["symptom.slug"] = cat

    # Operating condition
    if cond.get("turning") is True:
        facts["condition.operating"] = "turning"
        facts["condition.turning"] = True
    elif cond.get("braking") is True:
        facts["condition.operating"] = "braking"
        facts["condition.braking"] = True
    elif cond.get("acceleration") is True:
        facts["condition.operating"] = "accelerating"
    elif cond.get("engine_state"):
        facts["condition.operating"] = cond["engine_state"]

    if cond.get("speed"):
        facts["condition.speed"] = cond["speed"]
    if cond.get("direction"):
        facts["condition.direction"] = cond["direction"]
    if cond.get("road_condition"):
        facts["condition.road_condition"] = cond["road_condition"]

    # Observations
    if obs.get("increases_on_sharp_turn") is not None:
        facts["observation.sharp_turn_effect"] = "yes" if obs["increases_on_sharp_turn"] else "no"
    if obs.get("location"):
        facts["observation.location"] = obs["location"]
    if obs.get("starter_state"):
        facts["observation.starter_state"] = obs["starter_state"]
    if obs.get("temperature_state"):
        facts["observation.temperature_state"] = obs["temperature_state"]
    if obs.get("smoke_color"):
        facts["observation.smoke_color"] = obs["smoke_color"]
    if obs.get("vibration") is not None:
        facts["observation.vibration"] = "yes" if obs["vibration"] else "none"

    # Structured sub-objects for dot-notation resolution
    facts["vehicle"] = veh
    facts["problem"] = prob
    facts["conditions"] = cond
    facts["condition"] = {
        "speed": cond.get("speed"),
        "direction": cond.get("direction"),
        "road_condition": cond.get("road_condition"),
        "operating": facts.get("condition.operating"),
    }
    facts["observations"] = obs
    facts["observation"] = {
        "sharp_turn_effect": facts.get("observation.sharp_turn_effect"),
        "location": obs.get("location"),
        "starter_state": obs.get("starter_state"),
        "temperature_state": obs.get("temperature_state"),
        "smoke_color": obs.get("smoke_color"),
        "vibration": facts.get("observation.vibration"),
    }
    facts["symptom"] = {"slug": facts.get("symptom.slug")}
    facts["system"] = {"slug": facts.get("system.slug")}

    return facts


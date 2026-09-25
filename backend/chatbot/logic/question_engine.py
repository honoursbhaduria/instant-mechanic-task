"""
Deterministic Symptom-Specific Question Engine for Instant Mechanic.
Selects the single highest-value unanswered diagnostic question,
supports dynamic symptom branching, and NEVER asks for known facts.
"""
from typing import Dict, Any, List, Tuple, Optional

SYMPTOM_FLOWS = {
    "steering_noise": [
        "noise_type",
        "when_occurs",
        "speed",
        "turning_direction",
        "sharp_or_normal_turn",
        "steering_vibration",
        "vehicle"
    ],
    "brake_noise": [
        "noise_type",
        "when_occurs",
        "speed",
        "braking_intensity",
        "front_or_rear",
        "vibration",
        "vehicle"
    ],
    "engine_noise": [
        "noise_type",
        "cold_or_hot",
        "engine_state",
        "acceleration",
        "oil_warning",
        "vehicle"
    ],
    "suspension_noise": [
        "noise_type",
        "road_condition",
        "speed",
        "front_or_rear",
        "vibration",
        "vehicle"
    ],
    "starting_problem": [
        "crank_or_no_crank",
        "starter_sound",
        "battery_symptoms",
        "cold_or_hot",
        "vehicle"
    ],
    "overheating": [
        "temperature_warning",
        "coolant_level",
        "steam_or_leak",
        "traffic_or_highway",
        "vehicle"
    ],
    "ac_problem": [
        "cooling_level",
        "blower_working",
        "cooling_while_driving",
        "vehicle"
    ],
    "transmission_problem": [
        "slipping_or_jerking",
        "gear_engagement",
        "speed",
        "vehicle"
    ],
    "vibration": [
        "speed",
        "braking_or_cruising",
        "vibration_location",
        "vehicle"
    ],
    "smoke": [
        "smoke_color",
        "engine_state",
        "oil_coolant_drop",
        "vehicle"
    ],
    "warning_light": [
        "which_light",
        "steady_or_flashing",
        "engine_behavior",
        "vehicle"
    ],
    "oil_leak": [
        "fluid_color",
        "leak_location",
        "oil_warning",
        "vehicle"
    ],
    "coolant_leak": [
        "fluid_color",
        "steam_or_leak",
        "temperature_warning",
        "vehicle"
    ],
    "tyre_problem": [
        "pulling_or_wobble",
        "speed",
        "tyre_pressure_check",
        "vehicle"
    ]
}

QUESTION_PRIORITY = {
    "vehicle": 95,
    "symptom": 100,
    "when_occurs": 90,
    "noise_type": 90,
    "crank_or_no_crank": 90,
    "smoke_color": 90,
    "which_light": 90,
    "turning_direction": 85,
    "speed": 80,
    "sharp_or_normal_turn": 80,
    "road_condition": 75,
    "front_or_rear": 75,
    "braking_intensity": 75,
    "cold_or_hot": 70,
    "vibration": 70,
    "temperature_warning": 75,
    "cooling_level": 80,
    "recent_service": 40
}

QUESTION_TEMPLATES = {
    "vehicle": {
        "text": "What car are you driving? Please give me the make, model, and approximate year.",
        "quick_replies": ["Hyundai Creta", "Maruti Swift", "Honda City", "Tata Nexon", "Mahindra Thar"]
    },
    "noise_type": {
        "text": "What kind of noise is it — clicking, grinding, squealing, knocking, humming, or rattling?",
        "quick_replies": ["Clicking", "Grinding", "Squealing", "Knocking", "Rattling", "Humming"]
    },
    "when_occurs": {
        "text": "When does it happen — while turning, braking, accelerating, or even when driving straight?",
        "quick_replies": ["While turning", "While braking", "While accelerating", "Driving straight"]
    },
    "speed": {
        "text": "At what speed is it most noticeable — low speed (e.g. parking/U-turns), city speeds, or highway cruising?",
        "quick_replies": ["Low speed (parking)", "City speeds (40-60 km/h)", "Highway (80+ km/h)", "All speeds"]
    },
    "turning_direction": {
        "text": "Does it happen mainly when turning left, turning right, or on both sides?",
        "quick_replies": ["Left turn", "Right turn", "Both sides"]
    },
    "sharp_or_normal_turn": {
        "text": "Does the clicking become louder when you turn the steering wheel more sharply?",
        "quick_replies": ["Yes, much louder", "No, stays the same", "Only on full lock"]
    },
    "front_or_rear": {
        "text": "Does the sound seem to come from the front or the rear of the vehicle?",
        "quick_replies": ["Front", "Rear", "Not sure"]
    },
    "braking_intensity": {
        "text": "Does the noise occur under light brake pressure, hard braking, or every time you stop?",
        "quick_replies": ["Light braking", "Hard braking", "Every stop"]
    },
    "vibration": {
        "text": "Do you also feel any vibration or pulsing through the steering wheel or brake pedal?",
        "quick_replies": ["Yes, through steering", "Yes, through pedal", "No vibration"]
    },
    "road_condition": {
        "text": "Does it happen mainly over speed bumps and rough potholes, or even on smooth paved roads?",
        "quick_replies": ["Over bumps/potholes", "On smooth roads too", "Only on speed breakers"]
    },
    "crank_or_no_crank": {
        "text": "When you turn the key or push Start, does the engine crank (turn over), click rapidly, or is it completely silent?",
        "quick_replies": ["Cranks but won't start", "Rapid clicking sound", "Completely silent", "Dash lights dim"]
    },
    "starter_sound": {
        "text": "Do you hear a loud starter click or grinding, or does the starter motor spin freely without catching?",
        "quick_replies": ["Rapid clicking", "Single click", "Spins without catching", "No sound"]
    },
    "temperature_warning": {
        "text": "Has the temperature gauge climbed into the red, or did a high-temperature warning light illuminate?",
        "quick_replies": ["Gauge in red", "Red temperature light", "Normal temperature", "Steam from bonnet"]
    },
    "steam_or_leak": {
        "text": "Did you see steam escaping from under the bonnet, or notice any puddle beneath the radiator?",
        "quick_replies": ["Steam from bonnet", "Puddle under car", "Sweet syrupy smell", "Neither"]
    },
    "cold_or_hot": {
        "text": "Does this happen only on a cold engine in the morning, or after the car has warmed up?",
        "quick_replies": ["Cold engine (morning)", "Warm engine (after driving)", "All the time"]
    },
    "cooling_level": {
        "text": "Is the AC blowing warm ambient air, or is the airflow completely stopped?",
        "quick_replies": ["Blowing warm air", "Airflow stopped (fan off)", "Weak cooling", "Cooling cuts off"]
    },
    "smoke_color": {
        "text": "What color is the smoke from the exhaust — thick white/steam, dark black, or bluish grey?",
        "quick_replies": ["White smoke/steam", "Thick black smoke", "Blue/grey smoke"]
    },
    "which_light": {
        "text": "Which warning light is displayed on the dashboard — Check Engine, Battery, ABS, or Oil Pressure?",
        "quick_replies": ["Check Engine", "Battery / Alternator", "ABS Warning", "Engine Oil Light"]
    },
    "slipping_or_jerking": {
        "text": "Does the transmission slip (engine RPM revs up without car accelerating) or does it jerk when shifting gears?",
        "quick_replies": ["Engine revs / slipping", "Harsh jerking on gear change", "Delay engaging Drive/Reverse"]
    }
}


def is_field_answered(field: str, state: Dict[str, Any]) -> bool:
    """Checks whether a specific diagnostic parameter has already been extracted."""
    veh = state.get("vehicle", {})
    prob = state.get("problem", {})
    cond = state.get("conditions", {})
    obs = state.get("observations", {})

    if field == "vehicle":
        return bool(veh.get("model") or veh.get("make"))
    if field == "noise_type":
        return bool(prob.get("noise_type"))
    if field == "when_occurs":
        return cond.get("turning") is not None or cond.get("braking") is not None or cond.get("acceleration") is not None
    if field == "speed":
        return bool(cond.get("speed"))
    if field == "turning_direction":
        return bool(cond.get("direction"))
    if field == "sharp_or_normal_turn":
        return obs.get("increases_on_sharp_turn") is not None
    if field == "front_or_rear":
        return bool(obs.get("location"))
    if field == "vibration":
        return obs.get("vibration") is not None
    if field == "road_condition":
        return bool(cond.get("road_condition"))
    if field == "crank_or_no_crank" or field == "starter_sound":
        return bool(obs.get("starter_state"))
    if field == "cold_or_hot":
        return bool(cond.get("engine_state"))
    if field == "temperature_warning":
        return obs.get("warning_light") == "temperature" or cond.get("engine_state") == "hot"
    if field == "smoke_color":
        return bool(obs.get("smoke_color"))
    if field == "which_light":
        return obs.get("warning_light") is not None and obs.get("warning_light") is not False
    if field == "braking_intensity":
        return cond.get("braking") is True and bool(cond.get("speed"))
    return False


def evaluate_evidence_sufficiency(state: Dict[str, Any], turn_count: int, latest_message: str) -> bool:
    """
    Evaluates whether sufficient clinical diagnostic evidence exists to run diagnosis.
    Returns True when diagnosis can proceed.
    """
    clean = latest_message.lower().strip()
    explicit_diag = [
        "run diagnosis", "ready to diagnose", "diagnose now", "start diagnosis",
        "give me the diagnosis", "what is the diagnosis", "tell me what's wrong"
    ]
    if any(k in clean for k in explicit_diag) and (state.get("problem", {}).get("primary_category") or state.get("problem", {}).get("symptom")):
        return True

    prob = state.get("problem", {})
    category = prob.get("primary_category") or ""
    cond = state.get("conditions", {})
    obs = state.get("observations", {})
    veh = state.get("vehicle", {})

    has_vehicle = bool(veh.get("model") or veh.get("make"))

    # Evidence score calculation
    evidence_points = 0
    if has_vehicle: evidence_points += 1
    if prob.get("noise_type") or prob.get("symptom"): evidence_points += 1
    if cond.get("turning") is not None or cond.get("braking") is not None: evidence_points += 1
    if cond.get("speed"): evidence_points += 1
    if cond.get("direction"): evidence_points += 1
    if obs.get("increases_on_sharp_turn") is not None: evidence_points += 1
    if obs.get("starter_state"): evidence_points += 2
    if obs.get("warning_light"): evidence_points += 1
    if obs.get("smoke_color"): evidence_points += 2
    if obs.get("location"): evidence_points += 1

    # Specific symptom sufficiency gates:
    if category == "steering_noise":
        # Need noise + turning + (speed or sharp turn effect or direction)
        if (prob.get("noise_type") and
            cond.get("turning") is True and
            (cond.get("direction") or obs.get("increases_on_sharp_turn") is not None or cond.get("speed"))):
            return True

    if category == "brake_noise":
        if prob.get("noise_type") and (cond.get("braking") is True or obs.get("location")):
            return True

    if category == "starting_problem":
        if obs.get("starter_state"):
            return True

    if category == "suspension_noise":
        if prob.get("noise_type") and (cond.get("road_condition") or obs.get("location")):
            return True

    # General threshold: 4 evidence points, or 3 points with >= 3 turns
    if evidence_points >= 4:
        return True
    if evidence_points >= 3 and turn_count >= 3:
        return True

    return False


def get_next_question(state: Dict[str, Any], turn_count: int, latest_message: str) -> Tuple[str, List[str], Optional[str], bool]:
    """
    Selects the next targeted diagnostic question using dynamic Neon PostgreSQL knowledge
    evaluation with fallback to template flows.
    Returns: (question_text, quick_replies, next_field_key, can_diagnose)
    """
    # 1. Check if user explicitly asked to diagnose or sufficiency gate tripped
    if evaluate_evidence_sufficiency(state, turn_count, latest_message):
        state["diagnostic_status"] = "ready"
        veh_str = f" for your {state['vehicle']['make']} {state['vehicle']['model']}".strip() if state.get("vehicle", {}).get("model") else ""
        return (
            f"I have enough information to assess the problem{veh_str}. Click 'Run Diagnosis' below to analyze the root cause and view recommended service solutions.",
            ["Run Diagnosis"],
            None,
            True
        )

    # 2. Try dynamic database question selection from Neon PostgreSQL
    try:
        from chatbot.logic.question_selector import select_next_question
        dynamic_q = select_next_question(state)
        if dynamic_q:
            q_key = dynamic_q["key"]
            state.setdefault("asked_questions", [])
            if q_key not in state["asked_questions"]:
                state["asked_questions"].append(q_key)
            state["diagnostic_status"] = "collecting"
            quick_replies = [opt["label"] for opt in dynamic_q.get("options", [])]
            return (
                dynamic_q["question"],
                quick_replies,
                q_key,
                False
            )
    except Exception:
        pass

    # 3. If dynamic DB questions are exhausted or empty, check vehicle info
    if not is_field_answered("vehicle", state):
        tmpl = QUESTION_TEMPLATES["vehicle"]
        state["diagnostic_status"] = "collecting"
        return (
            tmpl["text"],
            tmpl["quick_replies"],
            "vehicle",
            False
        )

    # 4. Fallback: Determine symptom flow
    prob = state.get("problem", {})
    primary_category = prob.get("primary_category") or "steering_noise"
    flow = SYMPTOM_FLOWS.get(primary_category, SYMPTOM_FLOWS["steering_noise"])

    # Sort unanswered fields by priority
    unanswered_candidates = []
    for field in flow:
        if not is_field_answered(field, state):
            priority = QUESTION_PRIORITY.get(field, 50)
            unanswered_candidates.append((priority, field))

    unanswered_candidates.sort(key=lambda x: x[0], reverse=True)

    if unanswered_candidates:
        selected_field = unanswered_candidates[0][1]
        tmpl = QUESTION_TEMPLATES.get(selected_field, QUESTION_TEMPLATES["vehicle"])
        state["diagnostic_status"] = "collecting"
        return (
            tmpl["text"],
            tmpl["quick_replies"],
            selected_field,
            False
        )

    # All fields answered: transition to ready
    state["diagnostic_status"] = "ready"
    veh_str = f" for your {state['vehicle']['make']} {state['vehicle']['model']}".strip() if state.get("vehicle", {}).get("model") else ""
    return (
        f"I have enough information to assess the problem{veh_str}. Click 'Run Diagnosis' below to analyze the root cause and view recommended service solutions.",
        ["Run Diagnosis"],
        None,
        True
    )

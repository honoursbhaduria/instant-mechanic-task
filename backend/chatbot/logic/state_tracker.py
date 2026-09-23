"""
State tracker and intelligent follow-up questionnaire logic for Instant Mechanic.
Checks for missing diagnostic information (Vehicle, Symptoms, Conditions) using
traditional backend logic to minimize AI API overhead.
"""
import re
from .validator import extract_vehicle_info, is_car_related

# Known condition triggers
CONDITION_KEYWORDS = {
    'turning', 'turn', 'left', 'right', 'straight', 'steering',
    'braking', 'brake', 'stopping', 'pedal',
    'accelerating', 'acceleration', 'gas', 'throttle', 'speeding up',
    'high speed', 'low speed', 'highway', 'slow', 'km/h', 'mph', 'rpm',
    'idle', 'idling', 'parked', 'neutral', 'traffic',
    'morning', 'cold', 'hot', 'winter', 'summer', 'rain', 'start', 'starting',
    'bumps', 'potholes', 'rough road', 'uphill', 'downhill',
    'ac on', 'air conditioner on', 'lights on', 'all the time', 'constant', 'intermittent'
}

# Known symptom categories
SYMPTOM_PATTERNS = {
    'clicking_turn': [r'click', r'clicking', r'tick', r'ticking', r'turn', r'steering'],
    'brake_noise': [r'brake', r'brakes', r'squeal', r'squeak', r'grind', r'grinding', r'stopping'],
    'no_start': [r'won\'?t start', r'not starting', r'doesn\'?t start', r'dead', r'no start', r'crank', r'clicking sound from starter'],
    'overheating': [r'overheat', r'heating', r'temperature', r'smoke', r'steam', r'coolant', r'hot engine'],
    'vibration': [r'vibrat', r'shak', r'wobbl', r'shudder', r'judder'],
    'check_engine': [r'check engine', r'cel', r'warning light', r'engine light', r'code'],
    'transmission': [r'gear', r'slip', r'slipping', r'clutch', r'shift', r'hesitat', r'delay'],
    'leak': [r'leak', r'leaking', r'puddle', r'fluid', r'oil drop'],
}


def analyze_conversation_state(messages, current_vehicle=""):
    """
    Analyze user messages to determine:
    1. Detected vehicle info
    2. Collected symptoms
    3. Collected operating conditions
    4. Whether follow-up is needed or sufficient info is ready for diagnosis
    """
    user_texts = [m.content for m in messages if m.role == 'user']
    full_user_context = " ".join(user_texts).lower()

    # 1. Vehicle info
    vehicle = current_vehicle
    if not vehicle:
        for text in user_texts:
            v = extract_vehicle_info(text)
            if v:
                vehicle = v
                break

    # 2. Symptoms identified
    detected_symptoms = []
    tokens = set(re.findall(r'\b\w+\b', full_user_context))
    for category, patterns in SYMPTOM_PATTERNS.items():
        matched = False
        for p in patterns:
            if re.search(r'\b' + p, full_user_context):
                matched = True
                break
        if matched:
            detected_symptoms.append(category)

    # 3. Operating conditions identified
    detected_conditions = []
    for cond in CONDITION_KEYWORDS:
        if re.search(r'\b' + re.escape(cond) + r'\b', full_user_context):
            detected_conditions.append(cond)

    return {
        "vehicle": vehicle,
        "symptoms": detected_symptoms,
        "conditions": detected_conditions,
        "turn_count": len(user_texts),
        "full_context": full_user_context,
    }


def generate_followup_question(state, latest_message):
    """
    Generates targeted follow-up question based on missing information.
    Returns (reply_text, needs_more_info)
    """
    latest_lower = latest_message.lower()
    turn_count = state["turn_count"]
    vehicle = state["vehicle"]
    conditions = state["conditions"]
    symptoms = state["symptoms"]

    # If the user explicitly asks for diagnosis or if enough turns/details exist
    explicit_diag_triggers = ["diagnose", "diagnosis", "what's wrong", "what is wrong", "tell me what", "book", "cost", "repair"]
    if any(trigger in latest_lower for trigger in explicit_diag_triggers):
        return (
            "I have gathered your symptoms. Click 'Run Diagnosis' or review the diagnosis below to inspect the components and schedule a certified mechanic.",
            False
        )

    # If already had 2 or more user turns and provided symptoms + conditions:
    if turn_count >= 2 and (len(conditions) >= 1 or len(symptoms) >= 1):
        veh_str = f" for your {vehicle}" if vehicle else ""
        return (
            f"Thank you for those details! Based on your observations{veh_str}, I have enough information to run a complete diagnostic assessment. "
            "You can now review the diagnosis and proceed to book a mechanic service.",
            False
        )

    # Specific targeted follow-ups:
    # 1. Clicking / Turning noise
    if 'clicking_turn' in symptoms:
        if not any(c in conditions for c in ['low speed', 'high speed', 'straight', 'slow', 'fast']):
            return (
                "When do you notice the clicking noise — only while turning at low speed (such as parking or tight turns), or also at higher speeds or while driving straight?",
                True
            )

    # 2. Brake noise
    if 'brake_noise' in symptoms:
        if not any(c in conditions for c in ['morning', 'cold', 'stopping', 'pedal', 'all the time']):
            return (
                "Does the brake squealing or grinding happen every time you press the pedal, or mostly during the first few stops in the morning? Do you also feel any vibration through the pedal?",
                True
            )

    # 3. Won't start / No start
    if 'no_start' in symptoms:
        if not any(c in conditions for c in ['crank', 'clicking', 'silence', 'lights']):
            return (
                "When you turn the key or press the start button, what happens exactly? Does the engine crank (turn over) slowly, do you hear rapid clicking, or is there complete silence with dash lights dimming?",
                True
            )

    # 4. Overheating / smoke
    if 'overheating' in symptoms:
        if not any(c in conditions for c in ['smoke', 'steam', 'temperature', 'red', 'puddle']):
            return (
                "Is the temperature gauge reading into the red? Did you see steam escaping from under the hood, or notice any sweet syrupy smell or coolant puddles beneath the car?",
                True
            )

    # 5. Vibration / shaking
    if 'vibration' in symptoms:
        if not any(c in conditions for c in ['highway', 'braking', 'low speed', 'high speed', 'accelerating', 'speed']):
            return (
                "At what speed is the vibration most noticeable? Does it happen specifically when you apply the brakes, or when cruising at highway speeds (around 80–100 km/h)?",
                True
            )

    # 6. Check engine light
    if 'check_engine' in symptoms:
        return (
            "Is the Check Engine Light steadily illuminated or is it blinking/flashing? Are you noticing any engine hesitation, jerking, or unusual exhaust smell?",
            True
        )

    # If conditions missing generally
    if not conditions:
        return (
            "Could you describe when this happens most noticeably — for example, while accelerating, braking, turning, idling, or driving at specific speeds?",
            True
        )

    # If vehicle info is missing
    if not vehicle and turn_count <= 2:
        return (
            "Understood. What is the make, model, and year of your car? Knowing your specific vehicle helps narrow down common issues and OEM technical service bulletins.",
            True
        )

    # Default ready state
    return (
        "Got it! I have recorded your symptom and operating conditions. Click 'Run Diagnosis' to analyze the root cause and view recommended repair services.",
        False
    )

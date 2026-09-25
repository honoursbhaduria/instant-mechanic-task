"""
Deterministic Automotive Fact Extractor for Instant Mechanic.
Extracts vehicle specifications, mechanical systems, symptoms, noise types,
operating conditions, and physical observations from natural English & Hinglish input
WITHOUT calling Gemini AI.
"""
import re
from typing import Dict, Any, Optional

from .validator import POPULAR_MAKES, POPULAR_MODELS

# Synonym normalizations for acoustic noise descriptions
NOISE_SYNONYMS = {
    "clicking": [
        "clicking", "click", "clicks", "ticking", "tick", "ticks",
        "tik tik", "tik-tik", "tak tak", "tak-tak", "clack", "clacking", "chatter"
    ],
    "squealing": [
        "squealing", "squeal", "squeals", "squeaking", "squeak", "squeaks",
        "screech", "screeching", "screeches", "cheekh", "high pitched"
    ],
    "grinding": [
        "grinding", "grind", "grinds", "ghisaawat", "ghisna", "metal on metal",
        "metal scratching", "rasping"
    ],
    "knocking": [
        "knocking", "knock", "knocks", "thak thak", "thak-thak", "khat khat",
        "khat-khat", "pinging", "detonation", "rod knock"
    ],
    "humming": [
        "humming", "hum", "hums", "droning", "drone", "drones", "whirring",
        "whir", "whine", "whining", "gunjana", "buzzing"
    ],
    "rattling": [
        "rattling", "rattle", "rattles", "khad khad", "khad-khad", "loose metal",
        "vibrating metal"
    ],
    "clunking": [
        "clunking", "clunk", "clunks", "thump", "thumping", "thud", "thudding",
        "dhab dhab", "dhab-dhab", "pop", "popping"
    ],
    "hissing": [
        "hissing", "hiss", "air leak sound", "steam sound"
    ],
    "roaring": [
        "roaring", "roar", "loud exhaust", "rumbling"
    ]
}

# Speed categorization
SPEED_MAP = {
    "low": [
        "low speed", "low-speed", "slow", "slowly", "parking", "park",
        "u-turn", "uturn", "crawling", "first gear", "10 km", "20 km", "dheere", "dhime"
    ],
    "city": [
        "city", "traffic", "medium speed", "normal speed", "30 km", "40 km", "50 km", "60 km", "bheed"
    ],
    "highway": [
        "highway", "high speed", "high-speed", "fast", "expressway", "cruising",
        "70 km", "80 km", "90 km", "100 km", "110 km", "120 km", "tez"
    ],
    "idle": [
        "idle", "idling", "parked", "neutral", "stationary", "standing",
        "khadi gaadi", "khadi", "without moving"
    ],
    "all": [
        "all speeds", "all speed", "har speed", "any speed", "constant"
    ]
}

# Automotive systems
SYSTEM_KEYWORDS = {
    "brakes": ["brake", "brakes", "braking", "break", "breaks", "rotor", "pad", "pads", "caliper", "pedal", "stopping"],
    "steering": ["steering", "steer", "turn", "turning", "steering wheel", "rack", "tie rod", "power steering", "modna"],
    "engine": ["engine", "motor", "cylinder", "spark plug", "rpm", "idle", "misfire", "sputter", "oil", "dipstick"],
    "suspension": ["suspension", "shock", "shocker", "strut", "struts", "bushing", "bushings", "sway bar", "spring", "bump", "pothole", "khadde"],
    "battery_starter": ["battery", "starter", "alternator", "crank", "cranking", "start", "starting", "ignition", "no start"],
    "transmission": ["gear", "gearbox", "clutch", "transmission", "slip", "slipping", "shift", "shifting", "reverse"],
    "cooling": ["radiator", "coolant", "overheating", "overheat", "temperature", "temp", "steam", "fan", "thermostat", "garam"],
    "ac": ["ac", "a/c", "air conditioner", "air conditioning", "cooling", "chilling", "blower", "compressor", "heater"],
    "exhaust": ["exhaust", "silencer", "muffler", "tailpipe", "smoke", "catalytic", "fumes"],
    "tyres": ["tyre", "tire", "tyres", "tires", "wheel", "wheels", "puncture", "flat", "alignment", "tread", "balancing"],
    "fuel": ["fuel", "petrol", "diesel", "gas", "mileage", "fuel pump", "injector", "average"]
}


def normalize_noise_type(text: str) -> str:
    """Detect and normalize noise description to standard identifier."""
    clean = text.lower()
    for norm, synonyms in NOISE_SYNONYMS.items():
        for syn in synonyms:
            if re.search(r'\b' + re.escape(syn) + r'\b', clean):
                return norm
    return ""


def detect_vehicle(text: str) -> Dict[str, Any]:
    """Detect make, model, and year from text."""
    clean = text.lower()
    res = {"make": "", "model": "", "year": None}

    # Year (1990 - 2026)
    ym = re.search(r'\b(19\d\d|20[0-2]\d)\b', clean)
    if ym:
        res["year"] = int(ym.group(1))

    # Make
    for make in POPULAR_MAKES:
        if re.search(r'\b' + re.escape(make) + r'\b', clean):
            res["make"] = make.capitalize()
            break

    # Model
    for model in POPULAR_MODELS:
        if re.search(r'\b' + re.escape(model) + r'\b', clean):
            res["model"] = model.capitalize()
            # If make is not explicitly mentioned, infer common make for well-known models
            if not res["make"]:
                inferred = infer_make_from_model(model)
                if inferred:
                    res["make"] = inferred
            break

    return res


def infer_make_from_model(model: str) -> str:
    """Infers manufacturer for popular known vehicle models."""
    m = model.lower()
    hyundai_models = {"creta", "venue", "i20", "i10", "verna", "tucson", "santro", "alcazar", "aura"}
    maruti_models = {"swift", "baleno", "brezza", "dzire", "ertiga", "wagonr", "alto", "celerio", "ignis", "ciaz", "fronx", "grand vitara", "jimny"}
    tata_models = {"nexon", "harrier", "safari", "punch", "tiago", "tigor", "curvv", "altroz"}
    mahindra_models = {"thar", "scorpio", "xuv700", "xuv300", "bolero", "xuv400"}
    toyota_models = {"innova", "fortuner", "corolla", "camry", "hyryder", "glanza", "yaris", "hilux"}
    honda_models = {"city", "civic", "amaze", "elevate", "jazz", "accord", "wr-v"}
    kia_models = {"seltos", "sonet", "carens", "carnival", "ev6"}
    vw_models = {"polo", "vento", "taigun", "virtus", "passat", "tiguan"}
    skoda_models = {"kushaq", "slavia", "octavia", "superb", "rapid", "kodiaq"}
    renault_models = {"duster", "kwid", "triber", "kiger"}

    if m in hyundai_models: return "Hyundai"
    if m in maruti_models: return "Maruti Suzuki"
    if m in tata_models: return "Tata"
    if m in mahindra_models: return "Mahindra"
    if m in toyota_models: return "Toyota"
    if m in honda_models: return "Honda"
    if m in kia_models: return "Kia"
    if m in vw_models: return "Volkswagen"
    if m in skoda_models: return "Skoda"
    if m in renault_models: return "Renault"
    return ""


def extract_facts(text: str, current_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Deterministically parses user input to extract automotive facts.
    Returns structured delta updates.
    """
    clean = text.lower().strip()
    extracted: Dict[str, Any] = {
        "vehicle": {},
        "problem": {},
        "conditions": {},
        "observations": {}
    }

    # 1. Vehicle info
    veh = detect_vehicle(clean)
    if veh["make"] or veh["model"] or veh["year"]:
        extracted["vehicle"] = {k: v for k, v in veh.items() if v}

    # 2. Noise identification
    noise = normalize_noise_type(clean)
    if noise:
        extracted["problem"]["noise_type"] = noise
        extracted["problem"]["symptom"] = "noise"

    # 3. Automotive system keywords
    matched_systems = []
    for sys_name, keywords in SYSTEM_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', clean):
                matched_systems.append(sys_name)
                break
    if matched_systems:
        extracted["problem"]["system"] = matched_systems[0]

    # 4. Conditions: Speed
    for speed_cat, triggers in SPEED_MAP.items():
        for trig in triggers:
            if re.search(r'\b' + re.escape(trig) + r'\b', clean):
                extracted["conditions"]["speed"] = speed_cat
                break
        if "speed" in extracted["conditions"]:
            break

    # 5. Conditions: Turning & Direction
    turning_positives = ["turn", "turning", "turn lete", "modte", "modne", "steer", "steering turn"]
    turning_negatives = ["straight", "seedha", "no turn", "without turning"]
    is_key_turn = bool(re.search(r'\b(turning\s+(the\s+)?key|key\s+turn|turn\s+(the\s+)?key|turn\s+on\s+ignition)\b', clean))
    if not is_key_turn:
        if any(re.search(r'\b' + re.escape(p) + r'\b', clean) for p in turning_positives):
            extracted["conditions"]["turning"] = True
        elif any(re.search(r'\b' + re.escape(n) + r'\b', clean) for n in turning_negatives):
            extracted["conditions"]["turning"] = False

    if re.search(r'\b(left|bayein|bayen|ulte|left-turn|left turn)\b', clean):
        extracted["conditions"]["direction"] = "left"
        extracted["conditions"]["turning"] = True
    elif re.search(r'\b(right|daayein|dayen|seedhe|right-turn|right turn)\b', clean):
        extracted["conditions"]["direction"] = "right"
        extracted["conditions"]["turning"] = True
    elif re.search(r'\b(both|dono|either)\b', clean):
        extracted["conditions"]["direction"] = "both"
        extracted["conditions"]["turning"] = True
    elif re.search(r'\b(straight|seedha)\b', clean):
        extracted["conditions"]["direction"] = "straight"
        extracted["conditions"]["turning"] = False

    # 6. Conditions: Braking
    braking_positives = ["brake", "braking", "stopping", "pedal press", "brake lagane", "rukne", "break lagate", "breaks"]
    if any(re.search(r'\b' + re.escape(p) + r'\b', clean) for p in braking_positives):
        extracted["conditions"]["braking"] = True

    # 7. Conditions: Acceleration
    accel_positives = ["accelerat", "speeding up", "gas", "race", "throttle", "dabane par", "pick up", "pickup"]
    if any(re.search(r'\b' + re.escape(p) + r'\b', clean) for p in accel_positives):
        extracted["conditions"]["acceleration"] = True

    # 8. Observations: Sharper turn effect
    sharper_indicators = [
        "sharper", "sharp", "sharp turn", "zyada", "increases", "louder",
        "full lock", "sharp left", "sharp right", "gets louder", "more noticeable"
    ]
    if any(re.search(r'\b' + re.escape(s) + r'\b', clean) for s in sharper_indicators):
        extracted["observations"]["increases_on_sharp_turn"] = True

    # 9. Observations: Vibration / Shaking
    if re.search(r'\b(vibration|vibrating|vibrate|shaking|shake|judder|wobble|wobbling|hilna|kaanpna|shudder)\b', clean):
        extracted["observations"]["vibration"] = True
    elif re.search(r'\b(no vibration|smooth|koi vibration nahi)\b', clean):
        extracted["observations"]["vibration"] = False

    # 10. Observations: Warning lights
    if re.search(r'\b(check engine|cel|engine light)\b', clean):
        extracted["observations"]["warning_light"] = "check_engine"
    elif re.search(r'\b(battery light|charging light)\b', clean):
        extracted["observations"]["warning_light"] = "battery"
    elif re.search(r'\b(oil light|low oil pressure)\b', clean):
        extracted["observations"]["warning_light"] = "oil"
    elif re.search(r'\b(abs light|abs warning)\b', clean):
        extracted["observations"]["warning_light"] = "abs"
    elif re.search(r'\b(temp light|temperature light|hot engine light)\b', clean):
        extracted["observations"]["warning_light"] = "temperature"
    elif re.search(r'\b(warning light|dash light|meter light)\b', clean):
        extracted["observations"]["warning_light"] = True
    elif re.search(r'\b(no light|no warning|koi light nahi)\b', clean):
        extracted["observations"]["warning_light"] = False

    # 11. Location: Front vs Rear
    if re.search(r'\b(front|aage|samne|bonnet|hood)\b', clean):
        extracted["observations"]["location"] = "front"
    elif re.search(r'\b(rear|back|peeche|boot|trunk|exhaust)\b', clean):
        extracted["observations"]["location"] = "rear"

    # 12. Starter sound / Crank state
    if re.search(r'\b(crank|cranking|turns over|turn over|starter spins)\b', clean):
        extracted["observations"]["starter_state"] = "cranks"
    elif re.search(r'\b(rapid\s*clicking|rapid\s*click|clicking\s*sound|starter\s*clicks|clicks\s*rapidly)\b', clean):
        extracted["observations"]["starter_state"] = "clicking"
    elif re.search(r'\b(no crank|silent|silence|dead|completely dead|kuch nahi ho raha)\b', clean):
        extracted["observations"]["starter_state"] = "silent"

    # 13. Temperature / Cold vs Hot
    if re.search(r'\b(cold|morning|first start|thandi|shuru mein)\b', clean):
        extracted["conditions"]["engine_state"] = "cold"
    elif re.search(r'\b(hot|after driving|garam|highway run|heat)\b', clean):
        extracted["conditions"]["engine_state"] = "hot"

    # 13b. Temperature Gauge & Steam Observations
    if re.search(r'\b(steam|steaming|boiling|smoke from bonnet|smoke from hood)\b', clean):
        extracted["observations"]["temperature_state"] = "steam"
    elif re.search(r'\b(red|gauge in red|in the red|high temp|high temperature|temperature red|overheating)\b', clean):
        extracted["observations"]["temperature_state"] = "red"
    elif re.search(r'\b(normal temp|normal temperature)\b', clean):
        extracted["observations"]["temperature_state"] = "normal"

    # 14. Road conditions (bumps, potholes)
    if re.search(r'\b(bump|bumps|speed breaker|rough road|pothole|potholes|khadde|bad road)\b', clean):
        extracted["conditions"]["road_condition"] = "bumps"

    # 15. Smoke color
    if re.search(r'\b(white smoke|safed dhuwan|white steam)\b', clean):
        extracted["observations"]["smoke_color"] = "white"
    elif re.search(r'\b(black smoke|kala dhuwan)\b', clean):
        extracted["observations"]["smoke_color"] = "black"
    elif re.search(r'\b(blue smoke|neela dhuwan)\b', clean):
        extracted["observations"]["smoke_color"] = "blue"
    elif re.search(r'\b(smoke|dhuwan|fumes)\b', clean):
        extracted["observations"]["smoke_color"] = "visible"

    # 16. General affirmation / negation handling when previous question is known
    # If the user simply answered "yes" / "haan" or "no" / "nahi", record that observation
    if re.match(r'^\s*(yes|haan|ha|yes\s+it\s+does|mostly|yep|definitely|always)\b', clean):
        extracted["observations"]["confirmed_last_question"] = True
    elif re.match(r'^\s*(no|nahi|na|nope|not\s+really|never)\b', clean):
        extracted["observations"]["confirmed_last_question"] = False

    return extracted

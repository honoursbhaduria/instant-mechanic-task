"""
Deterministic Automotive Symptom Classifier for Instant Mechanic.
Categorizes user complaints into discrete mechanical diagnostic domains
WITHOUT calling Gemini AI.
"""
import re
from typing import Dict, Any, Optional

CLASSIFIER_RULES = [
    # 1. Brake noise
    {
        "category": "brake_noise",
        "patterns": [
            r"\b(brake|brakes|braking|break|stopping)\b.*?\b(squeal|squeak|grind|screech|noise|awaaz|sound)\b",
            r"\b(squeal|squeak|grind|screech)\b.*?\b(brake|brakes|braking|break|stopping|pedal)\b",
            r"\b(brake|break)\s+(noise|awaaz|sound|pad|rotor)\b"
        ],
        "keywords": ["brake", "braking", "break", "rotor", "pad"]
    },
    # 2. Steering noise (e.g. CV joint, rack, steering pump)
    {
        "category": "steering_noise",
        "patterns": [
            r"\b(turn|turning|steer|steering)\b.*?\b(click|clicking|tick|ticking|pop|noise|awaaz|sound|clack)\b",
            r"\b(click|clicking|tick|ticking|clack)\b.*?\b(turn|turning|steer|steering)\b",
            r"\b(steering)\s*(noise|whine|groan|creak|sound)\b"
        ],
        "keywords": ["steering", "turning", "turn", "steer"]
    },
    # 3. Suspension noise
    {
        "category": "suspension_noise",
        "patterns": [
            r"\b(bump|bumps|pothole|potholes|rough\s+road|speed\s*breaker|khadde)\b.*?\b(clunk|thud|thump|rattle|noise|sound|awaaz|knock)\b",
            r"\b(suspension|shock|shocker|strut|bushing|sway\s*bar)\s*(noise|sound|awaaz|clunk|squeak)\b",
            r"\b(clunk|thump|thud)\b.*?\b(bump|pothole|speed\s*breaker)\b"
        ],
        "keywords": ["suspension", "shock", "shocker", "strut", "bushing", "bump", "pothole"]
    },
    # 4. Engine noise
    {
        "category": "engine_noise",
        "patterns": [
            r"\b(engine|motor)\b.*?\b(knock|knocking|ticking|rattling|whining|noise|sound|awaaz|thak\s*thak|khat\s*khat)\b",
            r"\b(knock|knocking|ticking|tap)\b.*?\b(idle|rpm|acceleration|cold\s+start|engine)\b",
            r"\b(lifter|piston|valve|timing\s+chain|drive\s+belt)\s*(noise|sound|tick|rattle)\b"
        ],
        "keywords": ["engine", "motor", "rpm", "idle", "cylinder", "spark"]
    },
    # 5. Starting problem
    {
        "category": "starting_problem",
        "patterns": [
            r"\b(won'?t\s+start|not\s+starting|doesn'?t\s+start|start\s+nahi|band\s+pad)\b",
            r"\b(crank|cranks|cranking)\b.*?\b(no\s+start|won'?t\s+fire|doesn'?t\s+catch)\b",
            r"\b(dead|silent)\s+when\s+(turn|start|key|button)\b",
            r"\b(starter\s+motor|starter\s+clicks)\b"
        ],
        "keywords": ["start", "crank", "starter", "starting"]
    },
    # 6. Battery problem
    {
        "category": "battery_problem",
        "patterns": [
            r"\b(battery|jump\s*start|battery\s+dead|battery\s+down)\b",
            r"\b(dim\s*lights?|dash\s*flickering)\b.*?\b(start|crank)\b",
            r"\b(rapid\s*clicking)\s*(from\s*dashboard|when\s*starting)\b"
        ],
        "keywords": ["battery", "alternator", "jumpstart", "jump start"]
    },
    # 7. Overheating
    {
        "category": "overheating",
        "patterns": [
            r"\b(overheat|overheating|garam|hot\s+engine|engine\s+hot)\b",
            r"\b(temp|temperature)\s*(gauge)?\s*(high|red|spik(ed|ing)|rising)\b",
            r"\b(steam\s+from\s+(hood|bonnet|radiator))\b",
            r"\b(radiator\s+boil|coolant\s+overflow)\b"
        ],
        "keywords": ["overheat", "overheating", "temperature", "steam", "radiator"]
    },
    # 8. Coolant leak
    {
        "category": "coolant_leak",
        "patterns": [
            r"\b(coolant|antifreeze|radiator\s+water)\b.*?\b(leak|leaking|drop|puddle|low|empty)\b",
            r"\b(green|orange|pink|sweet\s+smelling)\s+(fluid|puddle|leak)\b"
        ],
        "keywords": ["coolant", "antifreeze", "radiator"]
    },
    # 9. Oil leak
    {
        "category": "oil_leak",
        "patterns": [
            r"\b(engine\s+oil|oil)\b.*?\b(leak|leaking|drip|dripping|puddle|drop|tapak)\b",
            r"\b(black|brown|amber)\s+(oil\s+puddle|fluid\s+leak)\b",
            r"\b(oil\s+level\s+dropping|burning\s+oil\s+smell)\b"
        ],
        "keywords": ["oil", "dipstick", "oil leak"]
    },
    # 10. AC problem
    {
        "category": "ac_problem",
        "patterns": [
            r"\b(ac|a/c|air\s*condition(er|ing)?)\b.*?\b(not\s+cooling|warm\s+air|blower|fan|smell|cooling\s+nahi|weak)\b",
            r"\b(no\s+cooling|no\s+cold\s+air|hot\s+air\s+from\s+ac)\b",
            r"\b(ac\s+compressor|refrigerant|freon)\b"
        ],
        "keywords": ["ac", "air condition", "cooling", "blower", "compressor"]
    },
    # 11. Clutch problem
    {
        "category": "clutch_problem",
        "patterns": [
            r"\b(clutch)\b.*?\b(slip|slipping|hard|stiff|spongy|smell|burning|not\s+engaging)\b",
            r"\b(clutch\s+pedal|clutch\s+plate)\b",
            r"\b(burning\s+clutch\s+smell)\b"
        ],
        "keywords": ["clutch"]
    },
    # 12. Transmission problem
    {
        "category": "transmission_problem",
        "patterns": [
            r"\b(gear|gearbox|transmission)\b.*?\b(slip|slipping|stuck|not\s+shifting|hard\s+shift|delay|jerk)\b",
            r"\b(revs\s+up\s+without\s+speed|rpm\s+high\s+car\s+slow)\b",
            r"\b(transmission\s+fluid|gear\s+oil)\b"
        ],
        "keywords": ["transmission", "gear", "gearbox", "shift"]
    },
    # 13. Tyre problem
    {
        "category": "tyre_problem",
        "patterns": [
            r"\b(tyre|tire|tyres|tires|wheel)\b.*?\b(puncture|flat|air|pressure|low|uneven\s+wear|burst)\b",
            r"\b(car\s+pulling\s+to\s+(left|right)|wheel\s+alignment)\b",
            r"\b(tpms|tyre\s+pressure\s+warning)\b"
        ],
        "keywords": ["tyre", "tire", "puncture", "alignment", "tread"]
    },
    # 14. Warning light
    {
        "category": "warning_light",
        "patterns": [
            r"\b(check\s+engine|cel|warning\s+light|dashboard\s+light|abs\s+light|airbag\s+light|engine\s+light)\b",
            r"\b(light\s+on\s+(dash|dashboard|meter|cluster))\b",
            r"\b(obd|dtc|fault\s+code)\b"
        ],
        "keywords": ["warning light", "check engine", "cel", "abs light", "dashboard light"]
    },
    # 15. Poor acceleration / Lack of power
    {
        "category": "poor_acceleration",
        "patterns": [
            r"\b(poor\s+acceleration|loss\s+of\s+power|sluggish|no\s+pickup|car\s+not\s+pulling|hesitation|hesitating|bogs\s+down)\b",
            r"\b(car\s+struggles\s+to\s+accelerate|slow\s+pickup|accelerator\s+dabane\s+par\s+bhi)\b"
        ],
        "keywords": ["acceleration", "pickup", "sluggish", "hesitation", "power"]
    },
    # 16. Vibration / Shaking
    {
        "category": "vibration",
        "patterns": [
            r"\b(vibrat(ion|ing)|shak(e|ing)|wobbl(e|ing)|shudder|judder|hilna|kaanpna)\b.*?\b(highway|speed|braking|steering|idle)\b",
            r"\b(steering\s+wheel\s+(vibrates|shakes)|car\s+shaking)\b"
        ],
        "keywords": ["vibration", "shaking", "wobble", "judder"]
    },
    # 17. Smoke
    {
        "category": "smoke",
        "patterns": [
            r"\b(white|black|blue|heavy)\s+smoke\b",
            r"\b(smoke|dhuwan|dhuan)\b.*?\b(exhaust|tailpipe|silencer|bonnet|engine)\b"
        ],
        "keywords": ["smoke", "dhuwan", "dhuan", "fumes"]
    },
    # 18. Fuel problem
    {
        "category": "fuel_problem",
        "patterns": [
            r"\b(fuel\s+pump|fuel\s+filter|fuel\s+injector|poor\s+mileage|high\s+fuel\s+consumption)\b",
            r"\b(petrol\s+smell|diesel\s+smell|fuel\s+cut\s+off)\b"
        ],
        "keywords": ["fuel", "mileage", "fuel pump", "injector"]
    },
    # 19. Electrical problem
    {
        "category": "electrical_problem",
        "patterns": [
            r"\b(fuse|headlight|tail\s*light|horn|power\s*window|wiper|central\s*lock|flicker|wiring|relay)\b",
            r"\b(electrical\s+issue|short\s+circuit|battery\s+draining)\b"
        ],
        "keywords": ["fuse", "horn", "headlight", "window", "electrical", "wiring"]
    }
]


def classify_symptom(text: str, current_state: Optional[Dict[str, Any]] = None) -> str:
    """
    Deterministically classifies text + current state into a standard symptom category.
    Returns standard category string or empty string if undetermined.
    """
    clean = text.lower().strip()

    # Check rule patterns first
    for rule in CLASSIFIER_RULES:
        for pat in rule["patterns"]:
            if re.search(pat, clean):
                return rule["category"]

    # Check keyword density
    tokens = set(re.findall(r'\b\w+\b', clean))
    best_category = ""
    max_matches = 0

    for rule in CLASSIFIER_RULES:
        matches = sum(1 for kw in rule["keywords"] if kw in clean or kw in tokens)
        if matches > max_matches:
            max_matches = matches
            best_category = rule["category"]

    if max_matches >= 1:
        return best_category

    # Fallback to existing state context if available
    if current_state:
        existing_problem = current_state.get("problem", {})
        if existing_problem.get("primary_category"):
            return existing_problem["primary_category"]
        if existing_problem.get("system") == "steering" and existing_problem.get("noise_type"):
            return "steering_noise"
        if existing_problem.get("system") == "brakes" and existing_problem.get("noise_type"):
            return "brake_noise"
        if existing_problem.get("system") == "suspension":
            return "suspension_noise"

    return ""

"""
Query validation and domain boundary checker for Instant Mechanic.
Ensures we use traditional backend logic to filter off-topic queries and greetings
WITHOUT incurring unnecessary AI API calls.
"""
import re
from .vehicle_service import is_known_vehicle_make_or_model, COMMON_MAKES

# Comprehensive list of automotive keywords, components, symptoms, fluids, and terms
CAR_KEYWORDS = {
    # Vehicle parts & systems
    'car', 'cars', 'vehicle', 'auto', 'automobile', 'motor', 'engine', 'transmission',
    'gear', 'gearbox', 'clutch', 'brake', 'brakes', 'braking', 'rotor', 'pad', 'caliper',
    'accelerator', 'throttle', 'exhaust', 'muffler', 'catalytic', 'converter', 'radiator',
    'coolant', 'oil', 'filter', 'battery', 'alternator', 'starter', 'spark', 'plug',
    'suspension', 'shock', 'strut', 'spring', 'tire', 'tires', 'tyre', 'tyres', 'wheel',
    'wheels', 'rim', 'axle', 'cv', 'joint', 'bearing', 'steering', 'power steering',
    'chassis', 'fuel', 'pump', 'injector', 'turbo', 'supercharger', 'manifold', 'gasket',
    'head gasket', 'timing belt', 'serpentine belt', 'fan', 'ac', 'air conditioner',
    'compressor', 'windshield', 'wiper', 'fuse', 'headlight', 'tail light', 'indicator',
    'odometer', 'speedometer', 'dashboard', 'hood', 'bonnet', 'trunk', 'boot',

    # Symptoms & mechanical sensations
    'clicking', 'ticking', 'squeak', 'squeaking', 'squeal', 'squealing', 'rattle',
    'rattling', 'grinding', 'knocking', 'humming', 'whining', 'buzzing', 'clunk', 'clunking',
    'vibration', 'vibrating', 'shaking', 'judder', 'hesitation', 'hesitating', 'stalling',
    'stall', 'misfire', 'misfiring', 'overheating', 'smoke', 'steam', 'leaking', 'leak',
    'puddle', 'smell', 'burning', 'odor', 'slipping', 'pulling', 'wobble', 'wobbly',
    'sluggish', 'crank', 'cranking', 'jerking', 'loss of power',

    # Dash warning lights & diagnostics
    'check engine', 'check engine light', 'cel', 'abs', 'airbag', 'tpms', 'traction',
    'battery light', 'oil light', 'temperature light', 'obd', 'code', 'error code',
    'dtc', 'warning light',

    # Maintenance & service terms
    'mechanic', 'repair', 'service', 'maintenance', 'tune up', 'alignment', 'wheel alignment',
    'balancing', 'inspection', 'diagnostic', 'mileage', 'gas mileage', 'fuel economy',
    'breakdown', 'towing', 'jump start', 'puncture', 'flat tyre', 'flat tire',

    # Body, collision & exterior components
    'bumper', 'bumpers', 'fender', 'fenders', 'dent', 'dented', 'dents', 'scratch', 'scratched',
    'scratches', 'collision', 'crash', 'crashed', 'hit', 'accident', 'corner', 'curb', 'kerb',
    'road', 'drive', 'driving', 'drivable', 'fixed', 'repair', 'repairs', 'fixing', 'bodywork',
    'paint', 'panel', 'panels', 'quarter panel', 'door', 'windshield', 'side mirror', 'splitter',
    'diffuser', 'undercarriage', 'undercar', 'subframe', 'chassis', 'airbag', 'airbags',

    # Hinglish & colloquial vehicle terms
    'gaadi', 'gadi', 'awaaz', 'awaz', 'dhuwan', 'dhuan', 'tel', 'hawa', 'pahiya',
    'chal rahi', 'band pad', 'start nahi', 'garam', 'tik tik', 'tik-tik', 'tak tak',
    'parking', 'turn', 'turning', 'modne', 'bayein', 'daayein'
}

# Major car manufacturers and popular models
POPULAR_MAKES = [
    'hyundai', 'maruti', 'suzuki', 'tata', 'mahindra', 'toyota', 'honda', 'ford',
    'chevrolet', 'kia', 'volkswagen', 'skoda', 'renault', 'nissan', 'bmw', 'mercedes',
    'audi', 'jeep', 'mg', 'volvo', 'porsche', 'lexus', 'tesla', 'subaru', 'mazda',
    'mitsubishi', 'fiat', 'land rover', 'range rover', 'jaguar', 'bugatti', 'bugati',
    'ferrari', 'lamborghini', 'lambo', 'mclaren', 'bentley', 'rolls-royce', 'rolls royce',
    'aston martin', 'maserati', 'lotus', 'alfa romeo', 'cadillac', 'dodge', 'chrysler',
    'gmc', 'buick', 'acura', 'infiniti', 'genesis', 'mini', 'hundai', 'chevy', 'mercdes',
    'bimmer', 'beemer'
]

POPULAR_MODELS = [
    'creta', 'venue', 'i20', 'i10', 'verna', 'tucson', 'santro',
    'swift', 'baleno', 'brezza', 'dzire', 'ertiga', 'wagonr', 'alto', 'celerio',
    'nexon', 'harrier', 'safari', 'punch', 'tiago', 'tigor', 'curvv',
    'thar', 'scorpio', 'xuv700', 'xuv300', 'bolero',
    'innova', 'fortuner', 'corolla', 'camry', 'hyryder', 'glanza', 'yaris',
    'city', 'civic', 'amaze', 'elevate', 'jazz', 'accord',
    'seltos', 'sonet', 'carens', 'carnival', 'ev6',
    'polo', 'vento', 'taigun', 'virtus', 'kushaq', 'slavia', 'octavia',
    'duster', 'kwid', 'triber', 'magnite'
]

GREETING_PATTERNS = [
    r'^\s*(hi|hello|hey|hola|greetings|good\s*(morning|afternoon|evening|day)|namaste|whats\s*up|yo)\b',
    r'^\s*howdy\b',
    r'^\s*help\s*me\b',
]

SECURITY_PATTERNS = [
    r'ignore\s+(all\s+)?(previous|prior)\s+instructions',
    r'you\s+are\s+now\s+(dan|developer\s+mode|unfiltered)',
    r'pretend\s+(you\s+have\s+no\s+rules|you\s+are\s+not\s+an\s+ai|to\s+be)',
    r'exfiltrate\s+environment',
    r'<script\b[^>]*>',
    r'javascript:',
    r'\bunion\s+select\b',
    r'\bdrop\s+table\b',
    r'\bexec(ute)?\s*\(',
]

SECURITY_REJECTION = (
    "Security Alert: Prohibited pattern or prompt injection attempt detected. "
    "Instant Mechanic operates exclusively under verified automotive diagnostic protocols."
)

OFF_TOPIC_REJECTION = (
    "I am an auto mechanic assistant specialized exclusively in car diagnostics, troubleshooting, "
    "and vehicle maintenance. I can't assist with non-automotive topics. "
    "If you have any issues with your car—such as strange noises, warning lights, poor performance, "
    "or starting problems—please describe what you are experiencing and I'll be glad to help diagnose it!"
)

GREETING_REPLY = (
    "Hello! I am your Instant Mechanic senior automotive diagnostic technician.\n\n"
    "To help you diagnose any vehicle trouble, please tell me:\n"
    "1. What is the make, model, and year of your car?\n"
    "2. What symptom or issue are you experiencing (e.g., clicking noise, brake squeal, engine sputtering, warning light)?\n"
    "3. When does it happen (e.g., at low speeds, while turning, under braking)?"
)


def is_greeting_only(text: str) -> bool:
    """Return True if the text is merely a greeting with no actual symptoms."""
    clean = text.strip().lower()
    if len(clean) > 50:
        return False
    for pat in GREETING_PATTERNS:
        if re.match(pat, clean):
            # Check if any car keyword is also present
            words = set(re.findall(r'\b\w+\b', clean))
            if not words.intersection(CAR_KEYWORDS):
                return True
    return False


def is_car_related(text: str) -> bool:
    """
    Check if the user input contains automotive keywords, symptoms,
    car makes, or mechanical concepts.
    """
    clean = text.lower()
    tokens = set(re.findall(r'\b[\w\'-]+\b', clean))

    # Direct keyword intersection
    if tokens.intersection(CAR_KEYWORDS):
        return True

    # Check for multi-word phrases
    for kw in CAR_KEYWORDS:
        if ' ' in kw and kw in clean:
            return True

    # Check for car makes or models with exact word boundary
    for make in POPULAR_MAKES:
        if re.search(r'\b' + re.escape(make) + r'\b', clean):
            return True
    for model in POPULAR_MODELS:
        if re.search(r'\b' + re.escape(model) + r'\b', clean):
            return True
    for make in COMMON_MAKES:
        if len(make) >= 3 and re.search(r'\b' + re.escape(make.lower()) + r'\b', clean):
            return True
    for token in tokens:
        if is_known_vehicle_make_or_model(token):
            return True

    # Check for general automotive patterns
    context_patterns = [
        r'\b(when|while)\s+(i|it)\s+(turn|drive|brake|steer|accelerate|shift|reverse|start|idle)\b',
        r'\b(noise|sound|smell|vibrat|leak|smoke|heat)\b',
        r'\b(gear\s*\d|rpm|\d+\s*(kmph|mph|km/h))\b',
        r'\b(wheel|pedal|steering|dashboard|meter|hood)\b',
        r'\b(my|the)\s+(car|ride|wagon|sedan|suv|hatchback|truck|van)\b',
        r'\b(my|the|our)\s+([a-zA-Z0-9_\'-]+)\s+(got\s+hit|hit|crashed|scratched|dented|damaged|broke|stopped|died|stalled|won\'t\s+start|making\s+noise|leaking)\b',
        r'\b(hit|crashed|bumped|scratched|dented|smashed|damaged)\b',
        r'\b(bumper|fender|headlight|bonnet|hood|windshield|airbag|bodywork|scratch|dent)\b',
        r'\b(how\s+to\s+repair|how\s+to\s+fix|repair\s+my|fix\s+my|can\s+i\s+drive|safe\s+to\s+drive)\b',
    ]
    for pattern in context_patterns:
        if re.search(pattern, clean):
            return True

    # Check if fact extractor detects automotive facts
    from .fact_extractor import extract_facts
    f = extract_facts(text)
    if f.get("problem", {}).get("noise_type") or f.get("problem", {}).get("system") or f.get("vehicle", {}).get("model"):
        return True
    if f.get("conditions", {}).get("turning") is not None or f.get("conditions", {}).get("braking") is not None:
        return True

    return False


def extract_vehicle_info(text: str) -> str:
    """
    Try to detect vehicle make, model, and year from text.
    Example: "2022 Hyundai Creta" or "Swift Dzire 2018"
    """
    clean = text.lower()
    detected_parts = []

    # Detect year (1990 - 2026)
    year_match = re.search(r'\b(19\d\d|20[0-2]\d)\b', clean)
    if year_match:
        detected_parts.append(year_match.group(1))

    # Detect make
    for make in POPULAR_MAKES:
        if re.search(r'\b' + re.escape(make) + r'\b', clean):
            detected_parts.append(make.capitalize())
            break

    # Detect model
    for model in POPULAR_MODELS:
        if re.search(r'\b' + re.escape(model) + r'\b', clean):
            detected_parts.append(model.capitalize())
            break

    if len(detected_parts) >= 2:
        return " ".join(detected_parts)
    elif len(detected_parts) == 1 and detected_parts[0] not in ('19', '20'):
        return detected_parts[0]
    return ""


def is_security_threat(text: str) -> bool:
    """Check for prompt injection, jailbreak attempts, or script/SQL injection."""
    clean = text.lower()
    for pat in SECURITY_PATTERNS:
        if re.search(pat, clean):
            return True
    return False


def get_rejection_reply() -> str:
    return OFF_TOPIC_REJECTION


def get_security_rejection_reply() -> str:
    return SECURITY_REJECTION


def get_greeting_reply() -> str:
    return GREETING_REPLY

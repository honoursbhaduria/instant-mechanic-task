"""
Deterministic conversational intent and fact analyzer for Instant Mechanic diagnostic interviews.
Identifies:
- Drivability inquiries ('can I drive it', 'safe to drive')
- Repair inquiries ('how to get repair', 'how to fix')
- Process confusion/skepticism ('I don't understand', 'how can you know')
- Corrections ('actually', 'correction', 'I meant')
- Multi-fact extraction from answer text
WITHOUT calling Gemini AI.
"""
import re
from typing import Dict, Any, List, Optional


def analyze_answer_intent(text: str) -> Dict[str, Any]:
    """
    Analyzes the user's answer text for conversational side intents,
    clarification requests, or corrections.
    """
    clean = text.lower().strip()

    # Drivability / Safety inquiry
    drivability_patterns = [
        r'\b(can\s+i\s+drive|is\s+it\s+safe\s+to\s+drive|can\s+i\s+still\s+drive|safe\s+to\s+use|can\s+we\s+drive|can\s+i\s+still\s+use|drive\s+it\b|drivable|roadworthy)\b',
        r'\b(safe\s+to\s+drive|okay\s+to\s+drive|ok\s+to\s+drive)\b',
    ]
    is_drivability = any(re.search(p, clean) for p in drivability_patterns)

    # Repair procedure or guidance inquiry
    repair_patterns = [
        r'\b(how\s+to\s+(get\s+)?repair|how\s+to\s+fix|how\s+much\s+to\s+fix|cost\s+to\s+repair|can\s+it\s+be\s+fixed|repair\s+my|fix\s+my)\b',
    ]
    is_repair_inquiry = any(re.search(p, clean) for p in repair_patterns)

    # User confusion / skepticism about diagnosis or premature statements
    confusion_patterns = [
        r'\b(i\s+don\'?t\s+understand|how\s+can\s+you\s+understand|how\s+do\s+you\s+know|what\s+do\s+you\s+mean|how\s+can\s+anyone\s+know|makes\s+no\s+sense|how\s+can\s+yuo\s+understand|dont\s+understand\s+anythign)\b',
    ]
    is_confusion = any(re.search(p, clean) for p in confusion_patterns)

    # User correction of a previous statement
    correction_patterns = [
        r'\b(actually|correction|wait\s+no|i\s+meant|not\s+the|rather\s+than|instead\s+of)\b',
    ]
    is_correction = any(re.search(p, clean) for p in correction_patterns)

    # Check if answer contains descriptive affirmative damage details
    descriptive_damage_patterns = [
        r'\b(impact\s+(was|is|hit)|hit\s+(the|on|at|my)|struck|cracked|broken|dented|hanging|scratched|scraped|loose|detached)\b',
        r'\b(headlights?\s+(are|is|work)|fluids?\s+(are|leak|not|clean)|leaking|radiator\s+is)\b',
        r'\b(yes|no|none|nothing|not\s+really|neither|both|left\s+side|right\s+side|front\s+right|front\s+left)\b',
        r'\b(at\s+\d+\s*(kmph|mph|km/h)|speed\s+was|driving\s+around)\b'
    ]
    has_damage_description = any(re.search(p, clean) for p in descriptive_damage_patterns)

    # Pure side inquiry: asking if drivable or how to repair without providing descriptive damage facts
    is_pure_side_inquiry = (is_drivability or is_repair_inquiry) and not has_damage_description

    return {
        "is_drivability": is_drivability,
        "is_repair_inquiry": is_repair_inquiry,
        "is_confusion": is_confusion,
        "is_correction": is_correction,
        "has_damage_description": has_damage_description,
        "is_pure_side_inquiry": is_pure_side_inquiry
    }


def extract_evidence_facts(text: str) -> List[Dict[str, Any]]:
    """
    Extracts individual positive and negative facts from natural user text
    so multiple facts in a single answer are preserved for Gemini Call #2.
    Example: "Front bumper. Headlights are fine and car still drives normally."
    Produces facts for: impact location, headlights status, drivability status.
    """
    clean = text.lower().strip()
    facts = []

    # Drivability observations
    if re.search(r'\b(drives\s+normally|still\s+drives|car\s+drives\s+fine|drives\s+fine|steers\s+fine|runs\s+fine)\b', clean):
        facts.append({"key": "drivability", "value": "Vehicle reported to drive normally", "confidence": "explicit", "source": "user"})
    elif re.search(r'\b(cannot\s+drive|not\s+drivable|won\'t\s+move|cannot\s+move|disabled|undriveable)\b', clean):
        facts.append({"key": "drivability", "value": "Vehicle reported disabled or undrivable", "confidence": "explicit", "source": "user"})

    # Fluid leak observations
    if re.search(r'\b(no\s+leaks?|no\s+fluid|no\s+puddle|not\s+leaking)\b', clean):
        facts.append({"key": "fluid_leaks", "value": "No fluid leaks observed", "confidence": "explicit", "source": "user"})
    elif re.search(r'\b(coolant\s+leak|oil\s+leak|fluid\s+leak|leaking\s+fluid|puddle\s+under)\b', clean):
        facts.append({"key": "fluid_leaks", "value": "Fluid leak observed by user", "confidence": "explicit", "source": "user"})

    # Lighting / electrical observations
    if re.search(r'\b(headlights?\s+(are\s+)?(fine|working|good)|lights?\s+work)\b', clean):
        facts.append({"key": "headlights", "value": "Headlights functional", "confidence": "explicit", "source": "user"})
    elif re.search(r'\b(broken\s+headlight|shattered\s+light|headlight\s+broken|headlight\s+smashed)\b', clean):
        facts.append({"key": "headlights", "value": "Headlight damaged or broken", "confidence": "explicit", "source": "user"})

    # Warning lights observations
    if re.search(r'\b(no\s+warning\s+lights?|no\s+dash\s+lights?|no\s+cel)\b', clean):
        facts.append({"key": "warning_lights", "value": "No warning lights on dashboard", "confidence": "explicit", "source": "user"})
    elif re.search(r'\b(check\s+engine|airbag\s+light|warning\s+light\s+on)\b', clean):
        facts.append({"key": "warning_lights", "value": "Warning light illuminated on dashboard", "confidence": "explicit", "source": "user"})

    # Physical damage description
    damage_matches = re.findall(r'\b(cracked|broken|dented|hanging|scratched|loose|detached|smashed)\s+(bumper|fender|grille|splitter|hood|panel|wheel|tire)\b', clean)
    for desc, part in damage_matches:
        facts.append({"key": f"damage_{part}", "value": f"{part.capitalize()} is {desc}", "confidence": "explicit", "source": "user"})

    return facts

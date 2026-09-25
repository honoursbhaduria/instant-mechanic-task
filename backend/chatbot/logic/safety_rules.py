"""
Safety-critical automotive boundary detection for Instant Mechanic.
Immediately identifies emergency vehicle conditions (e.g. brake failure, fire,
fuel leaks, severe overheating) and provides safe roadside protocols
WITHOUT waiting for diagnostic question flows or AI calls.
"""
import re

SAFETY_PATTERNS = [
    {
        "id": "brake_failure",
        "patterns": [
            r"brake(s)?\s+(fail(ed|ure)?|not\s+working|went\s+out|stopped\s+working)",
            r"pedal\s+(went|goes|going)?\s*(to\s+the\s+)?floor",
            r"(no|zero)\s+brak(e|ing)",
            r"can('?t|not)\s+stop(\s+the\s+car)?",
            r"break\s+fail",
        ],
        "warning": (
            " CRITICAL BRAKE SAFETY ALERT: If you are currently driving, safely downshift gears, "
            "gradually engage the handbrake/parking brake, steer toward the road shoulder, and turn on your hazard lights. "
            "DO NOT drive the vehicle. Arrange an emergency flatbed tow immediately."
        ),
        "service": "Emergency Brake Hydraulic Inspection & Towing"
    },
    {
        "id": "fuel_leak_fire",
        "patterns": [
            r"\b(fire|burning|flame(s)?|caught\s+fire)\b",
            r"petrol\s+(leak|leaking|smell|puddle|drop)",
            r"fuel\s+(leak|leaking|pouring|puddle)",
            r"diesel\s+(leak|leaking|puddle)",
            r"raw\s+(fuel|gas(oline)?|petrol)\s+smell",
        ],
        "warning": (
            " FIRE & FUEL HAZARD ALERT: Turn off the engine immediately and turn off the ignition. "
            "Do not smoke, use open flames, or restart the car. Evacuate passengers to a safe distance "
            "and contact emergency services or arrange immediate towing."
        ),
        "service": "Fuel System Line & Tank Inspection"
    },
    {
        "id": "severe_overheat",
        "patterns": [
            r"steam\s+(pouring|coming|billowing)\s+out",
            r"(temp|temperature)\s*(gauge)?\s*(is)?\s*in\s+(the\s+)?red",
            r"boiling\s+coolant",
            r"radiator\s+burst",
            r"engine\s+overheat(ing)?\s+smoke",
        ],
        "warning": (
            " SEVERE ENGINE OVERHEATING: Pull over immediately and shut off the engine. "
            "DO NOT open the radiator cap while the engine is hot—pressurized boiling coolant can cause severe burns. "
            "Allow the engine to cool for at least 45 minutes before inspecting fluid levels."
        ),
        "service": "Cooling System Pressure Test & Head Gasket Check"
    },
    {
        "id": "steering_failure",
        "patterns": [
            r"steering\s+(locked|failed|not\s+turning|impossible\s+to\s+turn)",
            r"lost\s+steering",
            r"wheel\s+(came\s+off|loose|about\s+to\s+fall\s+off)",
            r"tie\s+rod\s+snapped",
        ],
        "warning": (
            " STEERING LOSS HAZARD: Pull over safely immediately. Driving with unresponsive steering "
            "or loose wheel hardware poses severe risk of a rollover or collision. Do not drive until inspected."
        ),
        "service": "Steering Rack, Tie Rod & Wheel Hub Inspection"
    },
    {
        "id": "oil_pressure_zero",
        "patterns": [
            r"(oil\s+light|low\s+oil\s+pressure)\s+and\s+(knocking|rattling|ticking)",
            r"zero\s+oil\s+pressure",
            r"red\s+oil\s+can\s+light",
        ],
        "warning": (
            " OIL PRESSURE LOSS: Stop the engine immediately. Operating an engine with zero oil pressure "
            "will cause internal metal seizure and total engine destruction within seconds. Check the oil dipstick."
        ),
        "service": "Engine Lubrication & Oil Pump Diagnostic"
    }
]


def check_safety_critical_condition(text: str) -> dict:
    """
    Evaluates text for immediate safety-critical vehicle hazards.
    Returns:
      {
        "is_safety_critical": True/False,
        "hazard_id": str,
        "warning": str,
        "recommended_service": str
      }
    """
    clean = text.lower().strip()
    for hazard in SAFETY_PATTERNS:
        for pattern in hazard["patterns"]:
            if re.search(pattern, clean):
                return {
                    "is_safety_critical": True,
                    "hazard_id": hazard["id"],
                    "warning": hazard["warning"],
                    "recommended_service": hazard["service"]
                }

    return {
        "is_safety_critical": False,
        "hazard_id": "",
        "warning": "",
        "recommended_service": ""
    }

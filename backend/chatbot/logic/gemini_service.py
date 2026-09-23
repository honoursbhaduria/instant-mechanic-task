"""
Gemini Diagnostic AI Service for Instant Mechanic.
Calls Gemini ONLY when diagnosis reasoning is needed with structured input and JSON output.
Features a fallback rule-based diagnostic engine for offline/rate-limited scenarios.
"""
import os
import json
import re
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Automotive Diagnostic Expert Knowledge Base (Fallback for when Gemini API key is missing, 429, or offline)
RULE_BASED_DIAGNOSTICS = [
    {
        "trigger": lambda text: any(w in text for w in ['click', 'clicking']) and any(w in text for w in ['turn', 'turning', 'steer']),
        "possible_issue": "Worn CV Joint / Constant Velocity Axle Shaft",
        "reasoning": "A rhythmic clicking or popping noise that occurs primarily while turning at low speeds is the classic symptom of a worn outer CV joint. As the steering turns, the increased angle causes the worn bearings inside the CV boot to click under drive torque.",
        "severity": "medium",
        "recommended_service": "CV Joint & Axle Inspection / Replacement",
        "safety_warning": "Do not ignore. If the CV joint fails completely while driving, the axle can separate, resulting in sudden loss of steering and drive power."
    },
    {
        "trigger": lambda text: any(w in text for w in ['squeal', 'squeak', 'grind', 'grinding']) and any(w in text for w in ['brake', 'braking', 'pedal', 'stop']),
        "possible_issue": "Worn Brake Pads & Glazed Brake Rotors",
        "reasoning": "High-pitched squealing under braking indicates the wear indicators (metal tabs) on the brake pads have touched the rotor. If grinding is felt, the pad friction material has worn away completely, causing metal-on-metal friction against the rotor.",
        "severity": "high",
        "recommended_service": "Comprehensive Brake System Inspection (Pads & Rotors)",
        "safety_warning": "Severely degraded brakes increase stopping distances and risk total brake failure. Have the vehicle inspected immediately before highway driving."
    },
    {
        "trigger": lambda text: ('won\'t start' in text or 'not start' in text or 'dead' in text) and ('click' in text or 'crank' in text or 'dim' in text or 'light' in text),
        "possible_issue": "Depleted Car Battery or Failing Alternator",
        "reasoning": "Rapid clicking when attempting to start accompanied by dimming dash lights indicates insufficient electrical amperage. The battery has lost charge or the alternator is no longer recharging it during engine operation.",
        "severity": "medium",
        "recommended_service": "Battery Health & Alternator Charging System Test",
        "safety_warning": "The vehicle may stall unexpectedly if driven with an alternator that fails to supply sufficient electrical power to the engine control unit and fuel injectors."
    },
    {
        "trigger": lambda text: any(w in text for w in ['overheat', 'temperature', 'red', 'steam', 'coolant', 'hot']),
        "possible_issue": "Cooling System Malfunction (Thermostat, Radiator, or Water Pump)",
        "reasoning": "Engine temperature rising into the red zone or steam emanating from the bonnet indicates a coolant loss, stuck thermostat valve, faulty radiator cooling fan, or water pump impeller failure.",
        "severity": "high",
        "recommended_service": "Cooling System Pressure Test & Thermostat Check",
        "safety_warning": "CRITICAL: Do NOT continue driving an overheating engine. Continued driving can warp the engine cylinder head and blow the head gasket, leading to catastrophic engine damage."
    },
    {
        "trigger": lambda text: any(w in text for w in ['vibrat', 'shak', 'wobbl']) and any(w in text for w in ['highway', 'speed', 'steering', '80', '100']),
        "possible_issue": "Unbalanced Wheels or Front Suspension Imbalance",
        "reasoning": "Steering wheel vibration that begins at highway speeds (between 70–110 km/h) is typically caused by wheel weight imbalance, tire tread separation, or worn tie rod ends.",
        "severity": "medium",
        "recommended_service": "4-Wheel High Speed Balancing & Alignment",
        "safety_warning": "Prolonged driving with out-of-balance wheels leads to premature tire wear, uneven tread, and strain on wheel bearings and suspension joints."
    },
    {
        "trigger": lambda text: any(w in text for w in ['humming', 'droning', 'roaring', 'whine']) and any(w in text for w in ['speed', 'wheel', 'bearing']),
        "possible_issue": "Failing Wheel Hub Bearing",
        "reasoning": "A persistent humming or droning roar that gets progressively louder as vehicle speed increases and changes pitch when shifting weight side-to-side points to a worn wheel hub bearing.",
        "severity": "high",
        "recommended_service": "Wheel Hub & Bearing Assembly Inspection",
        "safety_warning": "A completely seized wheel bearing can cause the wheel to lock up or detach from the vehicle at high speeds."
    },
    {
        "trigger": lambda text: any(w in text for w in ['clunk', 'knock', 'thump']) and any(w in text for w in ['bump', 'rough', 'pothole']),
        "possible_issue": "Worn Suspension Struts, Bushings, or Sway Bar Links",
        "reasoning": "Dull thudding or clunking sounds when driving over potholes, speed breakers, or rough roads are caused by play in sway bar end links, worn control arm bushings, or blown shock absorbers.",
        "severity": "medium",
        "recommended_service": "Suspension & Steering Linkage Inspection",
        "safety_warning": "Worn suspension decreases vehicle stability during emergency evasive maneuvers and increases tire braking distance."
    },
    {
        "trigger": lambda text: any(w in text for w in ['slip', 'slipping', 'rev', 'hesitat']) and any(w in text for w in ['gear', 'transmission', 'shift', 'clutch']),
        "possible_issue": "Transmission Slip / Worn Clutch Assembly",
        "reasoning": "When the engine RPM increases noticeably without a proportional increase in vehicle speed, the transmission clutch plates or hydraulic solenoids are failing to hold gear engagement.",
        "severity": "high",
        "recommended_service": "Transmission Fluid Flush & Clutch Diagnostic",
        "safety_warning": "Slipping transmission can leave you stranded in traffic or unable to accelerate when merging or passing."
    },
    {
        "trigger": lambda text: any(w in text for w in ['check engine', 'cel', 'misfir', 'jerk', 'sputter', 'rough idle']),
        "possible_issue": "Engine Misfire (Faulty Ignition Coil / Spark Plug or Sensor)",
        "reasoning": "Rough idle, hesitation, and a Check Engine Light typically reflect an engine cylinder misfire caused by worn spark plugs, degraded ignition coil packs, or a dirty mass airflow sensor.",
        "severity": "medium",
        "recommended_service": "OBD-II Computer Diagnostic Scan & Tune-Up",
        "safety_warning": "If the Check Engine Light begins blinking, unburned fuel is entering the exhaust and can melt the catalytic converter within minutes."
    }
]


def extract_json_from_text(text: str) -> dict:
    """Extract valid JSON from a text that might contain markdown fences or surrounding chatter."""
    # Look for ```json ... ```
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    # Look for raw { ... }
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    return {}


def run_fallback_diagnosis(vehicle: str, symptoms: str, conditions: str) -> dict:
    """
    Expert rule-based automotive diagnostic engine that runs when
    Gemini API is unavailable or quota is exceeded.
    """
    combined_text = f"{vehicle} {symptoms} {conditions}".lower()

    for item in RULE_BASED_DIAGNOSTICS:
        if item["trigger"](combined_text):
            return {
                "possible_issue": item["possible_issue"],
                "reasoning": item["reasoning"],
                "severity": item["severity"],
                "recommended_service": item["recommended_service"],
                "safety_warning": item["safety_warning"],
            }

    # Generic automotive fallback
    veh_name = vehicle if vehicle else "vehicle"
    return {
        "possible_issue": f"Mechanical Component Wear on {veh_name}",
        "reasoning": (
            f"Based on the reported symptoms ('{symptoms}') occurring under conditions ('{conditions}'), "
            "there is an anomaly in the drivetrain, steering, or suspension system that requires physical inspection."
        ),
        "severity": "medium",
        "recommended_service": "Comprehensive 40-Point Vehicle Inspection",
        "safety_warning": "Have a professional technician inspect the vehicle prior to long highway journeys to avoid roadside breakdown."
    }


def diagnose_with_gemini(vehicle: str, symptoms: str, conditions: str, previous_repairs: str = "None", media_info: str = "None") -> dict:
    """
    Calls Gemini API with structured diagnostic data and prompts for strict JSON schema output.
    Falls back gracefully to the rule-based expert engine if API key is not configured or fails.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.environ.get('GEMINI_API_KEY', '')

    if not api_key:
        logger.info("GEMINI_API_KEY not configured. Using rule-based automotive diagnostic engine.")
        return run_fallback_diagnosis(vehicle, symptoms, conditions)

    prompt = f"""
You are a Master Certified Automobile Technician (ASE-certified Master Mechanic) with 25+ years of hands-on garage experience.
Analyze the following structured automotive customer report and diagnose the root cause:

Structured Vehicle Diagnostic Information:
- Vehicle: {vehicle or 'Not specified'}
- Symptoms: {symptoms or 'Not specified'}
- Operating Conditions: {conditions or 'Not specified'}
- Previous Repairs: {previous_repairs}
- Attached Media / Sound Analysis: {media_info}

Instructions:
1. Identify the most probable mechanical/electrical issue.
2. Provide technical reasoning explaining WHY these conditions cause this symptom.
3. Classify severity strictly as "low", "medium", or "high".
4. Recommend a specific, actionable repair or inspection service.
5. Provide a clear safety warning regarding what happens if ignored.

Return ONLY a valid JSON object with EXACTLY this structure (no additional preamble or outside text):
{{
  "possible_issue": "Short summary of the issue",
  "reasoning": "Clear explanation of how and why this happens",
  "severity": "low|medium|high",
  "recommended_service": "Specific service title, e.g. CV Joint Inspection",
  "safety_warning": "Safety implications of continuing to drive"
}}
"""

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        # Use gemini-1.5-flash or gemini-2.5-flash or gemini-pro
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"temperature": 0.2, "response_mime_type": "application/json"}
        )

        response = model.generate_content(prompt)
        text_resp = response.text.strip()
        data = extract_json_from_text(text_resp)

        # Validate that required keys exist
        required_keys = ["possible_issue", "reasoning", "severity", "recommended_service", "safety_warning"]
        if all(k in data for k in required_keys):
            # Normalize severity
            if data["severity"] not in ["low", "medium", "high"]:
                data["severity"] = "medium"
            return data
        else:
            logger.warning(f"Gemini returned incomplete JSON: {text_resp}. Using fallback diagnosis.")
            return run_fallback_diagnosis(vehicle, symptoms, conditions)

    except Exception as e:
        logger.warning(f"Gemini API error during diagnosis: {e}. Falling back to rule-based engine.")
        return run_fallback_diagnosis(vehicle, symptoms, conditions)

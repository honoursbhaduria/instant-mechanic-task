"""
Deterministic Mechanical Rule Engine for Instant Mechanic.
Contains expert knowledge rules covering 40+ common automotive issues,
evaluates candidate plausibility scores, and decides whether a case is
clearly diagnosed locally or requires complex Gemini reasoning.
"""
from typing import Dict, Any, List, Tuple, Optional

RULES = [
    # 1. Outer CV Joint Wear
    {
        "id": "cv_joint",
        "issue": "Possible worn outer CV joint",
        "severity": "medium",
        "service": "CV Joint & Front Axle Shaft Inspection",
        "reasoning": (
            "A repetitive clicking or popping noise during turning—especially at low speeds and becoming "
            "more pronounced on sharper turns—is the classic symptom of a worn outer CV (Constant Velocity) joint. "
            "The internal ball bearings and cage have developed excessive play."
        ),
        "safety_warning": "Avoid prolonged highway driving. A catastrophic CV joint failure can separate the drive axle, causing complete loss of vehicle propulsion and steering control.",
        "matcher": lambda state: (
            (0.35 if state.get("problem", {}).get("noise_type") == "clicking" else 0.0) +
            (0.30 if state.get("conditions", {}).get("turning") is True else 0.0) +
            (0.15 if state.get("conditions", {}).get("speed") == "low" else 0.0) +
            (0.15 if state.get("observations", {}).get("increases_on_sharp_turn") is True else 0.0) +
            (0.05 if state.get("conditions", {}).get("direction") in ["left", "right"] else 0.0)
        )
    },
    # 2. Worn Brake Pads
    {
        "id": "brake_pads",
        "issue": "Possible worn brake pads",
        "severity": "medium",
        "service": "Brake Pad Inspection & Replacement",
        "reasoning": (
            "High-pitched squealing or squeaking upon brake application indicates that the acoustic wear indicator "
            "tabs are contacting the brake rotor, signaling that the friction material has worn down to replacement threshold."
        ),
        "safety_warning": "Worn brake pads increase braking distance. If driven further, they will grind into the rotors, resulting in brake fade and higher repair costs.",
        "matcher": lambda state: (
            (0.45 if state.get("problem", {}).get("noise_type") == "squealing" else 0.0) +
            (0.40 if state.get("conditions", {}).get("braking") is True else 0.0) +
            (0.10 if state.get("observations", {}).get("location") == "front" else 0.05 if state.get("observations", {}).get("location") else 0.0)
        )
    },
    # 3. Warped Brake Rotors
    {
        "id": "warped_rotors",
        "issue": "Possible warped brake rotors",
        "severity": "medium",
        "service": "Brake Rotor Runout Inspection & Resurfacing/Replacement",
        "reasoning": (
            "Pulsation or vibration felt through the brake pedal or steering wheel specifically when braking "
            "from medium-to-high speeds indicates thickness variation or thermal warping in the brake disc rotors."
        ),
        "safety_warning": "Severely warped rotors can reduce contact patch efficiency, increasing emergency stopping distance.",
        "matcher": lambda state: (
            (0.45 if state.get("conditions", {}).get("braking") is True else 0.0) +
            (0.40 if state.get("observations", {}).get("vibration") is True else 0.0) +
            (0.10 if state.get("problem", {}).get("noise_type") in ["grinding", "squealing"] else 0.0)
        )
    },
    # 4. Worn Wheel Hub Bearing
    {
        "id": "wheel_bearing",
        "issue": "Possible failing wheel hub bearing",
        "severity": "high",
        "service": "Wheel Hub & Bearing Assembly Replacement",
        "reasoning": (
            "A persistent low humming, droning, or growling sound that intensifies with vehicle speed and changes "
            "pitch when gently swaying the vehicle side-to-side points to spalling or pitting on wheel bearing races."
        ),
        "safety_warning": "CRITICAL: A completely seized wheel bearing can cause the wheel to lock up or detach from the hub at high speeds.",
        "matcher": lambda state: (
            (0.45 if state.get("problem", {}).get("noise_type") in ["humming", "roaring"] else 0.0) +
            (0.30 if state.get("conditions", {}).get("speed") in ["highway", "city", "all"] else 0.0) +
            (0.15 if state.get("conditions", {}).get("turning") is True or state.get("conditions", {}).get("direction") else 0.0)
        )
    },
    # 5. Low Tyre Pressure / Puncture
    {
        "id": "low_tyre_pressure",
        "issue": "Low tyre pressure or slow puncture",
        "severity": "low",
        "service": "Tyre Pressure & Tread Inspection / Puncture Repair",
        "reasoning": (
            "Vehicle pulling gently to one side or a soft, wallowing feel in the steering at moderate speeds is typically "
            "caused by pressure disparity between front tyres or an embedded nail/screw."
        ),
        "safety_warning": "Underinflated tyres suffer excessive sidewall flex, overheating, and increased risk of a highway blowout.",
        "matcher": lambda state: (
            (0.50 if state.get("problem", {}).get("primary_category") == "tyre_problem" else 0.0) +
            (0.30 if state.get("problem", {}).get("system") == "tyres" else 0.0) +
            (0.15 if state.get("observations", {}).get("warning_light") == "tpms" else 0.0)
        )
    },
    # 6. Wheel Misalignment
    {
        "id": "wheel_alignment",
        "issue": "Possible wheel misalignment",
        "severity": "low",
        "service": "3D Computerized Wheel Alignment",
        "reasoning": (
            "Car pulling consistently to the left or right on a straight, flat road with an off-center steering wheel "
            "indicates improper toe or camber angles, usually from striking potholes or curbs."
        ),
        "safety_warning": "Misalignment causes rapid, uneven tyre tread wear and reduces directional stability in wet road conditions.",
        "matcher": lambda state: (
            (0.40 if state.get("conditions", {}).get("direction") in ["left", "right"] and state.get("conditions", {}).get("turning") is False else 0.0) +
            (0.35 if state.get("problem", {}).get("system") in ["steering", "tyres"] and state.get("problem", {}).get("noise_type") == "" else 0.0) +
            (0.15 if state.get("conditions", {}).get("speed") in ["city", "highway"] else 0.0)
        )
    },
    # 7. Worn Suspension Bushings
    {
        "id": "suspension_bushing",
        "issue": "Possible worn control arm or stabilizer bar bushings",
        "severity": "medium",
        "service": "Suspension Bushing & Linkage Inspection",
        "reasoning": (
            "Creaking or dull squeaking sounds when rolling over speed breakers or uneven pavement at low speeds "
            "signify cracked, dried-out rubber in control arm bushings or stabilizer bar mounts."
        ),
        "safety_warning": "Degraded bushings degrade wheel alignment stability under heavy braking and steering inputs.",
        "matcher": lambda state: (
            (0.40 if state.get("conditions", {}).get("road_condition") == "bumps" else 0.0) +
            (0.30 if state.get("problem", {}).get("noise_type") in ["clunking", "squealing", "rattling"] else 0.0) +
            (0.20 if state.get("problem", {}).get("system") == "suspension" else 0.0)
        )
    },
    # 8. Worn Shock Absorber / Strut
    {
        "id": "shock_absorber",
        "issue": "Possible worn shock absorber or strut leak",
        "severity": "medium",
        "service": "Front/Rear Strut & Shock Absorber Inspection",
        "reasoning": (
            "A distinct clunk or thud over bumps accompanied by excessive vehicle bouncing or nose-dive under braking "
            "indicates blown hydraulic damping fluid in the struts."
        ),
        "safety_warning": "Blown shock absorbers compromise tire contact with the road, significantly increasing wet stopping distances.",
        "matcher": lambda state: (
            (0.45 if state.get("conditions", {}).get("road_condition") == "bumps" else 0.0) +
            (0.35 if state.get("problem", {}).get("noise_type") == "clunking" else 0.0) +
            (0.15 if state.get("problem", {}).get("system") == "suspension" else 0.0)
        )
    },
    # 9. Worn Tie Rod End
    {
        "id": "tie_rod",
        "issue": "Possible worn inner or outer tie rod end",
        "severity": "high",
        "service": "Steering Tie Rod End Inspection & Replacement",
        "reasoning": (
            "Loose steering response, front-end clunking over small road imperfections, and uneven tyre feathering "
            "are common signs of ball-and-socket wear inside tie rod ends."
        ),
        "safety_warning": "HIGH RISK: A separated tie rod end causes total loss of directional steering on that wheel.",
        "matcher": lambda state: (
            (0.35 if state.get("problem", {}).get("system") == "steering" else 0.0) +
            (0.30 if state.get("conditions", {}).get("road_condition") == "bumps" else 0.0) +
            (0.25 if state.get("observations", {}).get("vibration") is True else 0.0)
        )
    },
    # 10. Worn Lower Ball Joint
    {
        "id": "ball_joint",
        "issue": "Possible worn lower suspension ball joint",
        "severity": "high",
        "service": "Lower Ball Joint Inspection & Replacement",
        "reasoning": (
            "A sharp metallic pop or clunk when turning into a driveway or over bumps, accompanied by vague wandering "
            "in the steering, points to excessive vertical play in the lower ball joint."
        ),
        "safety_warning": "CRITICAL SAFETY RISK: Ball joint failure can cause the front steering knuckle to collapse onto the wheel.",
        "matcher": lambda state: (
            (0.35 if state.get("conditions", {}).get("turning") is True and state.get("conditions", {}).get("road_condition") == "bumps" else 0.0) +
            (0.30 if state.get("problem", {}).get("noise_type") == "clunking" else 0.0) +
            (0.20 if state.get("problem", {}).get("system") in ["suspension", "steering"] else 0.0)
        )
    },
    # 11. Depleted / Weak Battery
    {
        "id": "weak_battery",
        "issue": "Depleted or failing 12V automotive battery",
        "severity": "medium",
        "service": "Battery Health & Cranking Amperage (CCA) Test",
        "reasoning": (
            "Rapid clicking sound when attempting ignition with dimming interior/dash lights indicates "
            "insufficient cranking amperage from a dead or sulfated 12V battery."
        ),
        "safety_warning": "The car may fail to restart after short stops, leaving you stranded in traffic.",
        "matcher": lambda state: (
            (0.45 if state.get("observations", {}).get("starter_state") == "clicking" else 0.0) +
            (0.35 if state.get("problem", {}).get("primary_category") in ["starting_problem", "battery_problem"] else 0.0) +
            (0.15 if state.get("observations", {}).get("warning_light") == "battery" else 0.0)
        )
    },
    # 12. Failing Alternator
    {
        "id": "failing_alternator",
        "issue": "Failing alternator charging system",
        "severity": "high",
        "service": "Alternator Voltage Output & Charging Diode Test",
        "reasoning": (
            "Battery warning light illuminated while driving, whining noise from engine bay, or headlights dimming "
            "at stoplights means the alternator is no longer delivering required 13.8–14.4V charging voltage."
        ),
        "safety_warning": "Once the battery reserves deplete, the engine ECU and fuel pump will shut down while driving.",
        "matcher": lambda state: (
            (0.40 if state.get("observations", {}).get("warning_light") == "battery" else 0.0) +
            (0.35 if state.get("problem", {}).get("noise_type") == "humming" and state.get("problem", {}).get("system") == "engine" else 0.0) +
            (0.20 if state.get("problem", {}).get("primary_category") in ["battery_problem", "electrical_problem"] else 0.0)
        )
    },
    # 13. Starter Motor Failure
    {
        "id": "starter_motor",
        "issue": "Faulty starter motor or solenoid",
        "severity": "medium",
        "service": "Starter Motor & Solenoid Electrical Diagnostic",
        "reasoning": (
            "A single loud metallic click with full battery power (bright lights) when turning the key, or starter "
            "motor spinning freely without engaging the engine flywheel indicates a jammed or burned starter solenoid."
        ),
        "safety_warning": "Vehicle cannot be started reliably without jump-starting or towing.",
        "matcher": lambda state: (
            (0.45 if state.get("observations", {}).get("starter_state") in ["silent", "cranks"] and state.get("problem", {}).get("primary_category") == "starting_problem" else 0.0) +
            (0.35 if state.get("problem", {}).get("system") == "battery_starter" else 0.0) +
            (0.15 if state.get("observations", {}).get("warning_light") is False else 0.0)
        )
    },
    # 14. Worn Spark Plugs
    {
        "id": "spark_plugs",
        "issue": "Worn or fouled spark plugs",
        "severity": "medium",
        "service": "Spark Plug Inspection & Tune-Up",
        "reasoning": (
            "Engine sputtering, rough idling, hesitation under acceleration, and reduced fuel economy occur when "
            "the spark plug electrode gap widens with age or gets fouled with carbon."
        ),
        "safety_warning": "Misfiring sends unburned fuel into the catalytic converter, which can cause costly exhaust damage.",
        "matcher": lambda state: (
            (0.35 if state.get("problem", {}).get("primary_category") in ["engine_noise", "poor_acceleration"] else 0.0) +
            (0.30 if state.get("observations", {}).get("vibration") is True else 0.0) +
            (0.25 if state.get("conditions", {}).get("acceleration") is True else 0.0)
        )
    },
    # 15. Failing Ignition Coil
    {
        "id": "ignition_coil",
        "issue": "Failing ignition coil pack",
        "severity": "medium",
        "service": "OBD-II Cylinder Misfire Scan & Coil Pack Replacement",
        "reasoning": (
            "Noticeable engine jerking or shaking under load accompanied by a flashing or steady Check Engine Light "
            "points to internal insulation breakdown in one of the ignition coils."
        ),
        "safety_warning": "Driving with a sustained cylinder misfire can melt catalytic converter internals within miles.",
        "matcher": lambda state: (
            (0.40 if state.get("observations", {}).get("warning_light") == "check_engine" else 0.0) +
            (0.35 if state.get("observations", {}).get("vibration") is True and state.get("conditions", {}).get("acceleration") is True else 0.0) +
            (0.20 if state.get("problem", {}).get("system") == "engine" else 0.0)
        )
    },
    # 16. Failing Fuel Pump
    {
        "id": "fuel_pump",
        "issue": "Weak or failing electric fuel pump",
        "severity": "high",
        "service": "Fuel Rail Pressure Test & Fuel Pump Replacement",
        "reasoning": (
            "High-pitched whining from the rear fuel tank area, engine sputtering at highway speeds, or engine "
            "cranking vigorously without firing indicates low fuel delivery pressure."
        ),
        "safety_warning": "The engine may abruptly die at highway speeds without warning.",
        "matcher": lambda state: (
            (0.40 if state.get("observations", {}).get("location") == "rear" and state.get("problem", {}).get("noise_type") == "humming" else 0.0) +
            (0.35 if state.get("observations", {}).get("starter_state") == "cranks" and state.get("problem", {}).get("primary_category") == "starting_problem" else 0.0) +
            (0.20 if state.get("problem", {}).get("system") == "fuel" else 0.0)
        )
    },
    # 17. Clogged Fuel Injector
    {
        "id": "fuel_injector",
        "issue": "Dirty or clogged fuel injector",
        "severity": "medium",
        "service": "Ultrasonic Fuel Injector Cleaning & Flow Test",
        "reasoning": (
            "Uneven fuel spray pattern creates a lean combustion mixture, causing intermittent hesitation, "
            "poor throttle response, and rough cold-engine idling."
        ),
        "safety_warning": "Lean fuel conditions increase combustion chamber temperatures, risking exhaust valve damage.",
        "matcher": lambda state: (
            (0.35 if state.get("problem", {}).get("primary_category") in ["poor_acceleration", "fuel_problem"] else 0.0) +
            (0.30 if state.get("conditions", {}).get("acceleration") is True else 0.0) +
            (0.20 if state.get("observations", {}).get("vibration") is True else 0.0)
        )
    },
    # 18. Severe Engine Overheating
    {
        "id": "engine_overheating",
        "issue": "Engine overheating condition",
        "severity": "high",
        "service": "Comprehensive Cooling System Pressure & Thermostat Diagnostic",
        "reasoning": (
            "Temperature gauge climbing into the red zone or steam emanating from the bonnet indicates loss of heat "
            "dissipation through the radiator, stuck thermostat, or severe coolant loss."
        ),
        "safety_warning": "STOP IMMEDIATELY: Overheating will warp aluminum cylinder heads and destroy the engine head gasket.",
        "matcher": lambda state: (
            (0.50 if state.get("problem", {}).get("primary_category") == "overheating" else 0.0) +
            (0.30 if state.get("conditions", {}).get("engine_state") == "hot" or state.get("observations", {}).get("warning_light") == "temperature" else 0.0) +
            (0.15 if state.get("problem", {}).get("system") == "cooling" else 0.0)
        )
    },
    # 19. Coolant Leak
    {
        "id": "coolant_leak",
        "issue": "Cooling system external coolant leak",
        "severity": "medium",
        "service": "Radiator & Hose Pressure Decay Test",
        "reasoning": (
            "Puddles of sweet-smelling green/orange/pink liquid beneath the front engine compartment or rapid "
            "coolant reservoir drop indicate cracked radiator tanks, leaky heater core hoses, or degraded water pump seal."
        ),
        "safety_warning": "Loss of coolant will rapidly progress to engine overheating and catastrophic cylinder head failure.",
        "matcher": lambda state: (
            (0.55 if state.get("problem", {}).get("primary_category") == "coolant_leak" else 0.0) +
            (0.30 if state.get("observations", {}).get("location") == "front" else 0.0) +
            (0.15 if state.get("problem", {}).get("system") == "cooling" else 0.0)
        )
    },
    # 20. Radiator Blockage
    {
        "id": "radiator_problem",
        "issue": "Clogged radiator core or bent cooling fins",
        "severity": "medium",
        "service": "Radiator Flush & Thermal Efficiency Inspection",
        "reasoning": (
            "Vehicle overheats primarily during highway cruising or uphill climbs despite full coolant levels, "
            "indicating internal scale buildup blocking core tubes."
        ),
        "safety_warning": "Thermal stress can cause plastic radiator end-tanks to crack open while driving.",
        "matcher": lambda state: (
            (0.40 if state.get("problem", {}).get("primary_category") == "overheating" else 0.0) +
            (0.35 if state.get("conditions", {}).get("speed") == "highway" else 0.0) +
            (0.20 if state.get("problem", {}).get("system") == "cooling" else 0.0)
        )
    },
    # 21. Stuck Thermostat Valve
    {
        "id": "stuck_thermostat",
        "issue": "Thermostat valve stuck closed",
        "severity": "high",
        "service": "Thermostat Replacement & Coolant Bleed",
        "reasoning": (
            "Engine temperature spikes rapidly within 5–10 minutes of starting while the lower radiator hose remains "
            "cold, proving the wax pellet thermostat is failing to open."
        ),
        "safety_warning": "Coolant cannot reach the radiator to shed heat, causing immediate localized engine boil-over.",
        "matcher": lambda state: (
            (0.45 if state.get("problem", {}).get("primary_category") == "overheating" else 0.0) +
            (0.30 if state.get("conditions", {}).get("engine_state") in ["hot", "cold"] else 0.0) +
            (0.20 if state.get("problem", {}).get("system") == "cooling" else 0.0)
        )
    },
    # 22. Cooling Fan Failure
    {
        "id": "cooling_fan",
        "issue": "Radiator electric cooling fan failure",
        "severity": "medium",
        "service": "Radiator Fan Motor & Relay Circuit Test",
        "reasoning": (
            "Temperature rises strictly in slow bumper-to-bumper city traffic or idling, but cools down normally "
            "once cruising on highway, indicating lack of forced fan airflow across the radiator core."
        ),
        "safety_warning": "Severe overheating will occur if trapped in stationary city traffic or drive-thrus.",
        "matcher": lambda state: (
            (0.40 if state.get("problem", {}).get("primary_category") == "overheating" else 0.0) +
            (0.40 if state.get("conditions", {}).get("speed") in ["low", "idle", "city"] else 0.0) +
            (0.15 if state.get("problem", {}).get("system") == "cooling" else 0.0)
        )
    },
    # 23. Water Pump Failure
    {
        "id": "water_pump",
        "issue": "Failing water pump bearing or impeller",
        "severity": "high",
        "service": "Water Pump & Timing/Drive Belt Replacement",
        "reasoning": (
            "High-pitched screeching or rumbling from the front accessory belt accompanied by coolant weeping from "
            "the pump weep hole and overheating points to bearing and mechanical seal failure."
        ),
        "safety_warning": "A seized water pump can snap the timing or serpentine belt, leading to engine destruction on interference engines.",
        "matcher": lambda state: (
            (0.35 if state.get("problem", {}).get("primary_category") in ["overheating", "coolant_leak"] else 0.0) +
            (0.35 if state.get("problem", {}).get("noise_type") in ["squealing", "grinding", "humming"] else 0.0) +
            (0.25 if state.get("observations", {}).get("location") == "front" else 0.0)
        )
    },
    # 24. Low Engine Oil
    {
        "id": "low_engine_oil",
        "issue": "Critically low engine oil level",
        "severity": "high",
        "service": "Engine Oil Level Check & Top-Up / Leak Inspection",
        "reasoning": (
            "Ticking or tapping sound from the top cylinder head (hydraulic valve lifters) especially under acceleration "
            "is caused by oil starvation and loss of hydraulic cushion."
        ),
        "safety_warning": "DO NOT DRIVE: Operating an engine with low oil leads to rod bearing wipeout and seized pistons.",
        "matcher": lambda state: (
            (0.40 if state.get("observations", {}).get("warning_light") == "oil" else 0.0) +
            (0.35 if state.get("problem", {}).get("noise_type") in ["clicking", "knocking"] and state.get("problem", {}).get("system") == "engine" else 0.0) +
            (0.20 if state.get("problem", {}).get("primary_category") in ["engine_noise", "oil_leak"] else 0.0)
        )
    },
    # 25. Engine Oil Leak
    {
        "id": "oil_leak",
        "issue": "Engine oil leak (gasket or seal)",
        "severity": "medium",
        "service": "Engine Valve Cover / Oil Pan Gasket Inspection",
        "reasoning": (
            "Dark brown or amber fluid spots under the engine bay, oil pooling on the exhaust manifold, or burning oil "
            "odor in the cabin points to valve cover gasket or crankshaft seal leakage."
        ),
        "safety_warning": "Oil dripping onto hot exhaust components poses a potential engine bay smoke and fire hazard.",
        "matcher": lambda state: (
            (0.55 if state.get("problem", {}).get("primary_category") == "oil_leak" else 0.0) +
            (0.30 if state.get("observations", {}).get("location") == "front" else 0.0) +
            (0.15 if state.get("problem", {}).get("system") == "engine" else 0.0)
        )
    },
    # 26. Blown Head Gasket
    {
        "id": "head_gasket",
        "issue": "Possible blown cylinder head gasket",
        "severity": "high",
        "service": "Combustion Gas Block Test & Compression Test",
        "reasoning": (
            "Persistent white sweet-smelling exhaust smoke, bubbling in the coolant expansion tank, and milky oil residue "
            "under the oil filler cap mean combustion gases are breaching the cooling jacket."
        ),
        "safety_warning": "Coolant entering the cylinders can cause hydraulic lock (hydro-lock), bending connecting rods.",
        "matcher": lambda state: (
            (0.50 if state.get("observations", {}).get("smoke_color") == "white" else 0.0) +
            (0.30 if state.get("problem", {}).get("primary_category") in ["overheating", "smoke"] else 0.0) +
            (0.15 if state.get("problem", {}).get("system") == "cooling" else 0.0)
        )
    },
    # 27. Low AC Refrigerant
    {
        "id": "ac_refrigerant",
        "issue": "Low AC refrigerant charge (R134a/R1234yf leak)",
        "severity": "low",
        "service": "AC Leak Detection & Refrigerant Re-Gas",
        "reasoning": (
            "AC vents blowing mildly cool or warm ambient air with the blower fan functioning normally indicates "
            "loss of refrigerant pressure through O-rings or condenser stone damage."
        ),
        "safety_warning": "Operating an empty AC system starves the compressor of lubricating oil, causing compressor seizure.",
        "matcher": lambda state: (
            (0.50 if state.get("problem", {}).get("primary_category") == "ac_problem" else 0.0) +
            (0.35 if state.get("problem", {}).get("system") == "ac" else 0.0) +
            (0.10 if state.get("conditions", {}).get("engine_state") != "cold" else 0.0)
        )
    },
    # 28. AC Compressor Clutch Failure
    {
        "id": "ac_compressor",
        "issue": "Failing AC compressor or magnetic clutch",
        "severity": "medium",
        "service": "AC Compressor Clutch & Belt Diagnostic",
        "reasoning": (
            "Loud clicking, rattling, or squealing from the engine bay specifically when pressing the AC button, "
            "along with loss of cooling, indicates electromagnetic clutch slip or internal compressor lock."
        ),
        "safety_warning": "A seized compressor pulley can shred the serpentine belt, disabling the alternator and water pump.",
        "matcher": lambda state: (
            (0.40 if state.get("problem", {}).get("primary_category") == "ac_problem" else 0.0) +
            (0.35 if state.get("problem", {}).get("noise_type") in ["squealing", "clicking", "rattling"] else 0.0) +
            (0.20 if state.get("problem", {}).get("system") == "ac" else 0.0)
        )
    },
    # 29. Blower Motor Failure
    {
        "id": "blower_motor",
        "issue": "HVAC blower motor or resistor failure",
        "severity": "low",
        "service": "Cabin Blower Motor & Resistor Diagnostic",
        "reasoning": (
            "No air emerging from dashboard vents regardless of fan speed setting, or fan only functioning on highest "
            "speed, points to a blown thermal resistor fuse or seized blower motor armature."
        ),
        "safety_warning": "Loss of cabin blower prevents windshield defogging in rainy or cold conditions.",
        "matcher": lambda state: (
            (0.45 if state.get("problem", {}).get("primary_category") == "ac_problem" else 0.0) +
            (0.35 if state.get("problem", {}).get("noise_type") in ["rattling", "humming"] and state.get("problem", {}).get("system") == "ac" else 0.0) +
            (0.15 if state.get("observations", {}).get("location") == "dashboard" else 0.0)
        )
    },
    # 30. Slipping Clutch Assembly
    {
        "id": "clutch_wear",
        "issue": "Worn manual clutch pressure plate & friction disc",
        "severity": "high",
        "service": "Clutch Kit (Disc, Cover, Release Bearing) Replacement",
        "reasoning": (
            "Engine RPM revs upward when accelerating in high gear (3rd/4th) without a corresponding increase in vehicle "
            "speed, accompanied by an acrid burning friction smell, demonstrates a slipping clutch."
        ),
        "safety_warning": "A severely slipping clutch will leave you unable to climb inclines or merge into moving traffic.",
        "matcher": lambda state: (
            (0.50 if state.get("problem", {}).get("primary_category") in ["clutch_problem", "transmission_problem"] else 0.0) +
            (0.30 if state.get("conditions", {}).get("acceleration") is True else 0.0) +
            (0.15 if state.get("problem", {}).get("system") in ["transmission", "clutch"] else 0.0)
        )
    },
    # 31. Low / Degraded Transmission Fluid
    {
        "id": "transmission_fluid",
        "issue": "Low or burnt automatic transmission fluid (ATF)",
        "severity": "medium",
        "service": "Automatic Transmission Fluid Flush & Level Check",
        "reasoning": (
            "Delayed gear engagement into Drive or Reverse, delayed upshifts, and harsh shift shudder are typical "
            "consequences of low fluid level or oxidized fluid failing to build hydraulic pressure."
        ),
        "safety_warning": "Low hydraulic pressure burns automatic transmission friction clutches, causing total transmission failure.",
        "matcher": lambda state: (
            (0.45 if state.get("problem", {}).get("primary_category") == "transmission_problem" else 0.0) +
            (0.30 if state.get("observations", {}).get("vibration") is True else 0.0) +
            (0.20 if state.get("problem", {}).get("system") == "transmission" else 0.0)
        )
    },
    # 32. Automatic Gearbox Shift Solenoid Issue
    {
        "id": "gearbox_issue",
        "issue": "Automatic transmission shift solenoid failure",
        "severity": "high",
        "service": "Transmission TCU Diagnostic Scan & Solenoid Replacement",
        "reasoning": (
            "Transmission becoming locked in 3rd gear (Limp Home Mode), harsh clunk when selecting gear, and "
            "Check Engine/Transmission warning lights point to an electrical solenoid fault in the valve body."
        ),
        "safety_warning": "Vehicle performance is restricted in Limp mode to protect gearbox internals.",
        "matcher": lambda state: (
            (0.40 if state.get("problem", {}).get("primary_category") == "transmission_problem" else 0.0) +
            (0.35 if state.get("observations", {}).get("warning_light") is not None and state.get("observations", {}).get("warning_light") is not False else 0.0) +
            (0.20 if state.get("problem", {}).get("system") == "transmission" else 0.0)
        )
    },
    # 33. Serpentine Drive Belt Wear / Slip
    {
        "id": "drive_belt",
        "issue": "Worn or loose serpentine accessory drive belt",
        "severity": "medium",
        "service": "Serpentine Drive Belt & Tensioner Replacement",
        "reasoning": (
            "Loud, high-pitched screeching or squealing on cold engine start or when turning steering to full lock / turning on AC "
            "is caused by an aged, glazed rubber belt slipping over alternator or power steering pulleys."
        ),
        "safety_warning": "If the drive belt snaps, power steering assistance, alternator battery charging, and water pump circulation stop.",
        "matcher": lambda state: (
            (0.45 if state.get("problem", {}).get("noise_type") == "squealing" and state.get("conditions", {}).get("braking") is not True else 0.0) +
            (0.30 if state.get("conditions", {}).get("engine_state") == "cold" or state.get("problem", {}).get("system") == "engine" else 0.0) +
            (0.20 if state.get("observations", {}).get("location") == "front" else 0.0)
        )
    },
    # 34. Timing Belt / Chain Slack
    {
        "id": "timing_belt",
        "issue": "Timing chain stretch or worn tensioner",
        "severity": "high",
        "service": "Timing Chain & Hydraulic Tensioner Inspection",
        "reasoning": (
            "Metallic rattling or buzzing from front engine timing cover for 2–3 seconds upon cold start before oil "
            "pressure builds indicates a slack timing chain slapping against its plastic guides."
        ),
        "safety_warning": "CRITICAL RISK: A jumped timing chain will cause piston-to-valve collision, ruining the cylinder head.",
        "matcher": lambda state: (
            (0.40 if state.get("problem", {}).get("noise_type") == "rattling" and state.get("problem", {}).get("system") == "engine" else 0.0) +
            (0.35 if state.get("conditions", {}).get("engine_state") == "cold" else 0.0) +
            (0.20 if state.get("observations", {}).get("location") == "front" else 0.0)
        )
    },
    # 35. Worn Engine Mount
    {
        "id": "engine_mount",
        "issue": "Torn hydraulic engine or transmission mount",
        "severity": "medium",
        "service": "Engine & Transmission Mount Replacement",
        "reasoning": (
            "Excessive cabin vibration felt at idle that smooths out once moving, accompanied by a heavy thump "
            "when shifting between Drive and Reverse or accelerating hard, indicates torn rubber or oil leakage from engine mounts."
        ),
        "safety_warning": "Excessive engine movement places severe fatigue stress on exhaust flex pipes, coolant hoses, and CV axles.",
        "matcher": lambda state: (
            (0.45 if state.get("observations", {}).get("vibration") is True and state.get("conditions", {}).get("speed") in ["idle", "low"] else 0.0) +
            (0.30 if state.get("problem", {}).get("noise_type") == "clunking" or state.get("problem", {}).get("system") == "engine" else 0.0) +
            (0.20 if state.get("conditions", {}).get("braking") is not True else 0.0)
        )
    },
    # 36. Exhaust Leak / Broken Flex Pipe
    {
        "id": "exhaust_leak",
        "issue": "Exhaust manifold gasket leak or broken flex pipe",
        "severity": "medium",
        "service": "Exhaust System Smoke & Leak Diagnostic",
        "reasoning": (
            "Loud buzzing, hissing, or motorcycle-like roaring noise under acceleration that quietens down at cruise, "
            "often accompanied by exhaust fumes near the cabin, indicates a fractured exhaust flex joint."
        ),
        "safety_warning": "Dangerous carbon monoxide exhaust gas can seep into the passenger compartment.",
        "matcher": lambda state: (
            (0.45 if state.get("problem", {}).get("noise_type") in ["roaring", "hissing", "rattling"] and state.get("problem", {}).get("system") == "exhaust" else 0.0) +
            (0.30 if state.get("conditions", {}).get("acceleration") is True else 0.0) +
            (0.20 if state.get("problem", {}).get("primary_category") in ["smoke", "engine_noise"] else 0.0)
        )
    },
    # 37. Catalytic Converter Degradation
    {
        "id": "catalytic_converter",
        "issue": "Degraded catalytic converter (efficiency below threshold)",
        "severity": "medium",
        "service": "Catalytic Converter & Emission Test (OBD P0420)",
        "reasoning": (
            "Rattling sound like marbles in a tin can from under the floorboards at idle, rotten egg (sulfur) smell, "
            "and Check Engine Light indicate broken ceramic catalyst substrate."
        ),
        "safety_warning": "A disintegrating catalyst can block exhaust gas escape, causing engine choking and severe power loss.",
        "matcher": lambda state: (
            (0.40 if state.get("observations", {}).get("warning_light") == "check_engine" else 0.0) +
            (0.35 if state.get("problem", {}).get("noise_type") == "rattling" and state.get("problem", {}).get("system") == "exhaust" else 0.0) +
            (0.20 if state.get("problem", {}).get("primary_category") in ["warning_light", "poor_acceleration"] else 0.0)
        )
    },
    # 38. Faulty Oxygen Sensor (O2)
    {
        "id": "oxygen_sensor",
        "issue": "Faulty upstream or downstream oxygen sensor",
        "severity": "low",
        "service": "O2 Sensor Waveform Test & Replacement",
        "reasoning": (
            "Drop in fuel economy (10–20%), slight engine hesitation on initial throttle tip-in, and persistent "
            "Check Engine Light are caused by a sluggish zirconia O2 sensor element."
        ),
        "safety_warning": "Incorrect air-fuel trimming will eventually overheat and damage the catalytic converter.",
        "matcher": lambda state: (
            (0.40 if state.get("observations", {}).get("warning_light") == "check_engine" else 0.0) +
            (0.35 if state.get("problem", {}).get("primary_category") in ["fuel_problem", "warning_light"] else 0.0) +
            (0.20 if state.get("conditions", {}).get("acceleration") is True else 0.0)
        )
    },
    # 39. Dirty Mass Airflow Sensor (MAF)
    {
        "id": "maf_sensor",
        "issue": "Contaminated mass airflow (MAF) sensor",
        "severity": "medium",
        "service": "MAF Sensor Electronic Cleaning & Calibration",
        "reasoning": (
            "Engine hesitation, stalling during deceleration, rough idle, and black smoke under load result from "
            "dirt or oil deposits on the heated platinum MAF sensor wire miscalculating intake air density."
        ),
        "safety_warning": "Engine may stall unexpectedly while slowing down at intersections.",
        "matcher": lambda state: (
            (0.40 if state.get("problem", {}).get("primary_category") in ["poor_acceleration", "smoke", "starting_problem"] else 0.0) +
            (0.30 if state.get("observations", {}).get("warning_light") == "check_engine" else 0.0) +
            (0.20 if state.get("conditions", {}).get("acceleration") is True else 0.0)
        )
    },
    # 40. Throttle Body Carbon Buildup
    {
        "id": "throttle_body",
        "issue": "Carbon buildup on electronic throttle body plate",
        "severity": "low",
        "service": "Electronic Throttle Body Decarbonization & Idle Relearn",
        "reasoning": (
            "Unstable wandering engine idle RPM (hunting between 500 and 1200 RPM) or engine dying after AC is switched "
            "on occurs when oily blow-by carbon chokes the idle airflow gap around the throttle butterfly valve."
        ),
        "safety_warning": "Can cause engine stalling when coming to a sudden stop.",
        "matcher": lambda state: (
            (0.45 if state.get("conditions", {}).get("speed") == "idle" or state.get("problem", {}).get("system") == "engine" else 0.0) +
            (0.30 if state.get("observations", {}).get("vibration") is True else 0.0) +
            (0.20 if state.get("problem", {}).get("primary_category") in ["engine_noise", "poor_acceleration"] else 0.0)
        )
    },
    # 41. ABS Wheel Speed Sensor
    {
        "id": "abs_sensor",
        "issue": "Faulty ABS wheel speed sensor",
        "severity": "medium",
        "service": "ABS Sensor Resistance Test & Tone Ring Inspection",
        "reasoning": (
            "ABS warning light illuminated, traction control disabled, and occasional unwanted brake pedal shudder "
            "at low speed stopping indicates metal debris on magnetic tone rings or broken sensor wiring."
        ),
        "safety_warning": "Anti-lock braking and electronic stability control are deactivated while ABS light is on.",
        "matcher": lambda state: (
            (0.50 if state.get("observations", {}).get("warning_light") == "abs" else 0.0) +
            (0.30 if state.get("conditions", {}).get("braking") is True else 0.0) +
            (0.15 if state.get("observations", {}).get("vibration") is True else 0.0)
        )
    },
    # 42. Sticking Brake Caliper
    {
        "id": "sticking_caliper",
        "issue": "Sticking brake caliper guide pins or hydraulic piston",
        "severity": "high",
        "service": "Brake Caliper Service & Guide Pin Lubrication",
        "reasoning": (
            "Vehicle pulls to one side while cruising, burning brake smell with excessive heat radiating from one wheel, "
            "and accelerated pad wear indicate a frozen caliper piston failing to retract."
        ),
        "safety_warning": "Excessive friction heat can boil brake fluid, causing sudden total brake pedal failure.",
        "matcher": lambda state: (
            (0.40 if state.get("problem", {}).get("system") == "brakes" else 0.0) +
            (0.35 if state.get("conditions", {}).get("direction") in ["left", "right"] and state.get("conditions", {}).get("braking") is not True else 0.0) +
            (0.20 if state.get("problem", {}).get("primary_category") == "brake_noise" else 0.0)
        )
    }
]


def evaluate_rules(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Evaluates all 42 rules against the structured state.
    Returns ranked candidate list:
      [
        {
          "id": "...",
          "issue": "...",
          "score": 0.92,
          "severity": "...",
          "service": "...",
          "reasoning": "...",
          "safety_warning": "..."
        },
        ...
      ]
    """
    candidates = []
    for rule in RULES:
        score = rule["matcher"](state)
        # Cap score between 0.0 and 1.0
        score = min(max(round(score, 2), 0.0), 1.0)
        if score > 0.25:
            candidates.append({
                "id": rule["id"],
                "issue": rule["issue"],
                "score": score,
                "severity": rule["severity"],
                "service": rule["service"],
                "reasoning": rule["reasoning"],
                "safety_warning": rule["safety_warning"]
            })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates


def is_case_clear(candidates: List[Dict[str, Any]]) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Determines if candidate scores produce a decisive local diagnosis.
    Returns: (is_clear, top_candidate)
      - is_clear == True: rule engine is confident (score >= 0.80 and runner-up is significantly lower)
      - is_clear == False: ambiguous or multiple close candidates, candidate list passed to Gemini
    """
    if not candidates:
        return False, None

    top = candidates[0]
    if len(candidates) == 1:
        if top["score"] >= 0.70:
            return True, top
        return False, top

    runner_up = candidates[1]
    # If top score is >= 0.80 and leads runner-up by at least 0.20
    if top["score"] >= 0.80 and (top["score"] - runner_up["score"]) >= 0.20:
        return True, top

    return False, top

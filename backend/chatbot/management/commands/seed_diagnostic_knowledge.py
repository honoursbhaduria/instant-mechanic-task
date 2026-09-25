"""
Django management command to idempotently seed automotive diagnostic knowledge
into Neon PostgreSQL.
Seeds:
- Vehicle systems
- Standard symptoms with colloquial / Hinglish aliases
- Dynamic diagnostic questions with declarative relevance rules
- Categorized diagnostic options with natural language aliases
- Diagnostic issues (42 common mechanical issues)
- Weighted diagnostic criteria (positive and negative evidence)
"""
from django.core.management.base import BaseCommand
from chatbot.models import (
    VehicleSystem,
    Symptom,
    DiagnosticQuestion,
    DiagnosticOption,
    DiagnosticIssue,
    DiagnosticCriterion,
)


class Command(BaseCommand):
    help = "Idempotently seed data-driven automotive diagnostic knowledge into Neon PostgreSQL."

    def handle(self, *args, **options):
        self.stdout.write("Starting automotive diagnostic knowledge seeding...")

        # =====================================================================
        # 1. VEHICLE SYSTEMS
        # =====================================================================
        systems_data = [
            ("engine", "Engine System", "Internal combustion components, cylinder head, lubrication, and valve train."),
            ("braking", "Braking System", "Hydraulic disc/drum brakes, calipers, rotors, pads, and ABS actuators."),
            ("steering", "Steering System", "Rack and pinion, tie rods, power steering pump, CV axles, and column."),
            ("suspension", "Suspension System", "Shock absorbers, struts, coil springs, control arms, and bushings."),
            ("transmission", "Transmission & Drivetrain", "Manual/automatic gearbox, torque converter, and drive shafts."),
            ("clutch", "Clutch Assembly", "Clutch friction disc, pressure plate, release bearing, and master/slave cylinder."),
            ("electrical", "Electrical & Ignition", "12V battery, alternator, starter motor, spark plugs, ignition coils, and ECU."),
            ("cooling", "Engine Cooling System", "Radiator, coolant hoses, water pump, thermostat, and cooling fan."),
            ("air_conditioning", "HVAC / Air Conditioning", "AC compressor, condenser, evaporator core, blower fan, and refrigerant."),
            ("fuel", "Fuel Delivery System", "Fuel pump, injectors, fuel filter, rail, and tank."),
            ("exhaust", "Exhaust & Emissions", "Exhaust manifold, flex pipe, catalytic converter, muffler, and O2 sensors."),
            ("wheels_tyres", "Wheels & Tyres", "Tyres, rims, wheel hub bearings, TPMS sensors, and wheel balancing."),
        ]

        system_objs = {}
        for slug, name, desc in systems_data:
            obj, _ = VehicleSystem.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "description": desc, "active": True}
            )
            system_objs[slug] = obj

        self.stdout.write(f"✓ Seeded {len(system_objs)} Vehicle Systems")

        # =====================================================================
        # 2. SYMPTOMS (With English, Colloquial, and Hinglish Aliases)
        # =====================================================================
        symptoms_data = [
            ("clicking_noise", "Clicking Noise", "steering", ["clicking", "click", "clicks", "ticking", "tick", "tik tik", "tik-tik", "tak tak", "tak-tak", "clack"]),
            ("squealing_noise", "Squealing Noise", "braking", ["squealing", "squeal", "squeak", "squeaking", "screech", "screeching", "cheekh", "high pitched"]),
            ("grinding_noise", "Grinding Noise", "braking", ["grinding", "grind", "ghisaawat", "ghisna", "metal on metal", "metal scratching"]),
            ("knocking_noise", "Knocking Noise", "engine", ["knocking", "knock", "thak thak", "thak-thak", "khat khat", "khat-khat", "pinging", "rod knock"]),
            ("humming_noise", "Humming Noise", "wheels_tyres", ["humming", "hum", "droning", "drone", "whirring", "whir", "whine", "gunjana"]),
            ("rattling_noise", "Rattling Noise", "exhaust", ["rattling", "rattle", "khad khad", "khad-khad", "loose metal", "chatter"]),
            ("clunking_noise", "Clunking Noise", "suspension", ["clunking", "clunk", "thump", "thumping", "thud", "dhab dhab", "pop"]),
            ("vibration", "Vehicle Vibration / Shaking", "wheels_tyres", ["vibration", "vibrating", "shaking", "judder", "wobble", "shudder", "hilna", "kaanpna"]),
            ("overheating", "Engine Overheating", "cooling", ["overheating", "overheat", "garam", "hot engine", "engine hot", "temperature high"]),
            ("starting_problem", "Starting / Ignition Failure", "electrical", ["won't start", "not starting", "doesn't start", "start nahi", "crank", "dead", "silent", "no start"]),
            ("poor_acceleration", "Poor Acceleration / Sluggishness", "engine", ["poor acceleration", "loss of power", "sluggish", "no pickup", "hesitation", "bogs down"]),
            ("fluid_leak", "Fluid Leak / Puddle", "cooling", ["leak", "leaking", "puddle", "drip", "tapakna", "oil leak", "coolant leak"]),
            ("smoke", "Exhaust Smoke", "exhaust", ["smoke", "dhuwan", "white smoke", "black smoke", "blue smoke", "fumes"]),
            ("warning_light", "Dashboard Warning Light", "electrical", ["check engine", "cel", "warning light", "dashboard light", "abs light", "battery light"]),
        ]

        symptom_objs = {}
        for slug, name, sys_slug, aliases in symptoms_data:
            obj, _ = Symptom.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "system": system_objs.get(sys_slug),
                    "aliases": aliases,
                    "active": True
                }
            )
            symptom_objs[slug] = obj

        self.stdout.write(f"✓ Seeded {len(symptom_objs)} Symptoms")

        # =====================================================================
        # 3. DIAGNOSTIC QUESTIONS & OPTIONS
        # =====================================================================
        questions_data = [
            {
                "key": "operating_condition",
                "question_text": "When does the problem occur most noticeably?",
                "category": "condition",
                "priority": 90,
                "target_fact_key": "condition.operating",
                "relevance_rule": {},
                "options": [
                    ("turning", "While turning", ["turning", "turn", "turn lete", "modte", "modne", "steer"]),
                    ("braking", "While braking", ["braking", "brake", "stopping", "pedal press", "rukne", "break"]),
                    ("accelerating", "While accelerating", ["accelerating", "speeding up", "gas", "race", "pickup"]),
                    ("cruising", "When driving straight / cruising", ["straight", "cruising", "seedha", "no turn"]),
                    ("idling", "While idling or stationary", ["idling", "idle", "parked", "khadi", "neutral", "standing"]),
                ]
            },
            {
                "key": "speed",
                "question_text": "At what speed is it most noticeable?",
                "category": "condition",
                "priority": 80,
                "target_fact_key": "condition.speed",
                "relevance_rule": {},
                "options": [
                    ("low", "Low speed (parking/U-turn)", ["low speed", "slow", "parking", "u-turn", "crawl", "10", "20", "dheere"]),
                    ("city", "City driving (30-60 km/h)", ["city", "medium speed", "traffic", "40", "50", "60"]),
                    ("highway", "Highway cruising (80+ km/h)", ["highway", "high speed", "fast", "80", "100", "120", "tez"]),
                    ("all", "All speeds / Constant", ["all speeds", "any speed", "constant", "har speed"]),
                ]
            },
            {
                "key": "turning_direction",
                "question_text": "Does it happen mainly when turning left, turning right, or on both sides?",
                "category": "condition",
                "priority": 85,
                "target_fact_key": "condition.direction",
                "relevance_rule": {
                    "any": [
                        {"field": "condition.operating", "operator": "equals", "value": "turning"},
                        {"field": "symptom.slug", "operator": "equals", "value": "clicking_noise"}
                    ]
                },
                "options": [
                    ("left", "Turning left", ["left", "bayein", "bayen", "left side", "ulte"]),
                    ("right", "Turning right", ["right", "daayein", "dayen", "right side", "seedhe"]),
                    ("both", "Both directions equally", ["both", "dono", "either"]),
                ]
            },
            {
                "key": "sharp_turn_effect",
                "question_text": "Does the noise become louder or more frequent when you make a sharper turn?",
                "category": "observation",
                "priority": 80,
                "target_fact_key": "observation.sharp_turn_effect",
                "relevance_rule": {
                    "all": [
                        {"field": "condition.operating", "operator": "equals", "value": "turning"}
                    ]
                },
                "options": [
                    ("yes", "Yes, noticeably louder", ["yes", "haan", "louder", "increases", "much louder", "sharper", "sharp turn"]),
                    ("no", "No, stays the same", ["no", "nahi", "same", "stays the same"]),
                ]
            },
            {
                "key": "front_or_rear",
                "question_text": "Does the sound seem to come from the front or the rear of the car?",
                "category": "observation",
                "priority": 75,
                "target_fact_key": "observation.location",
                "relevance_rule": {},
                "options": [
                    ("front", "Front of vehicle", ["front", "aage", "samne", "bonnet", "hood"]),
                    ("rear", "Rear of vehicle", ["rear", "back", "peeche", "trunk", "boot", "exhaust"]),
                ]
            },
            {
                "key": "road_condition",
                "question_text": "Does this happen mainly over speed bumps and rough potholes, or on smooth roads too?",
                "category": "condition",
                "priority": 75,
                "target_fact_key": "condition.road_condition",
                "relevance_rule": {},
                "options": [
                    ("bumps", "Over bumps and potholes", ["bumps", "potholes", "speed breaker", "rough road", "khadde"]),
                    ("smooth", "On smooth roads as well", ["smooth", "flat road", "plain"]),
                ]
            },
            {
                "key": "vibration_presence",
                "question_text": "Do you also feel vibration or pulsing through the steering wheel, floor, or pedals?",
                "category": "observation",
                "priority": 70,
                "target_fact_key": "observation.vibration",
                "relevance_rule": {},
                "options": [
                    ("steering", "Yes, through steering wheel", ["steering", "steering wheel vibration", "wheel shakes"]),
                    ("pedal", "Yes, through brake pedal", ["pedal", "brake pedal vibration", "pulsing pedal"]),
                    ("none", "No vibration noticed", ["no", "none", "smooth", "nahi"]),
                ]
            },
            {
                "key": "starter_sound",
                "question_text": "When you try to start the car, what happens exactly?",
                "category": "observation",
                "priority": 90,
                "target_fact_key": "observation.starter_state",
                "relevance_rule": {
                    "all": [
                        {"field": "symptom.slug", "operator": "equals", "value": "starting_problem"}
                    ]
                },
                "options": [
                    ("cranks", "Engine cranks normally but won't start", ["cranks", "crank", "turns over"]),
                    ("clicking", "Rapid clicking sound from dash/engine", ["clicking", "rapid clicking", "starter clicks"]),
                    ("silent", "Completely silent with lights dimming", ["silent", "silence", "dead", "nothing happens"]),
                ]
            },
            {
                "key": "temperature_gauge",
                "question_text": "What does the temperature gauge show, or did a temperature warning light illuminate?",
                "category": "observation",
                "priority": 85,
                "target_fact_key": "observation.temperature_state",
                "relevance_rule": {
                    "any": [
                        {"field": "symptom.slug", "operator": "equals", "value": "overheating"},
                        {"field": "symptom.slug", "operator": "equals", "value": "fluid_leak"}
                    ]
                },
                "options": [
                    ("red", "Gauge in red / High temp light on", ["red", "gauge red", "high temp", "red light"]),
                    ("steam", "Steam escaping from under the hood", ["steam", "boiling", "smoke from bonnet"]),
                    ("normal", "Normal operating temperature", ["normal", "regular", "middle"]),
                ]
            },
            {
                "key": "smoke_color",
                "question_text": "What color is the exhaust smoke?",
                "category": "observation",
                "priority": 85,
                "target_fact_key": "observation.smoke_color",
                "relevance_rule": {
                    "all": [
                        {"field": "symptom.slug", "operator": "equals", "value": "smoke"}
                    ]
                },
                "options": [
                    ("white", "White sweet-smelling smoke or steam", ["white", "safed", "white smoke", "steam"]),
                    ("black", "Thick dark black soot smoke", ["black", "kala", "black smoke"]),
                    ("blue", "Bluish-grey smoke with burning oil smell", ["blue", "grey", "blue smoke"]),
                ]
            },
        ]

        question_count = 0
        option_count = 0
        for qdata in questions_data:
            q_obj, _ = DiagnosticQuestion.objects.update_or_create(
                key=qdata["key"],
                defaults={
                    "question_text": qdata["question_text"],
                    "category": qdata["category"],
                    "priority": qdata["priority"],
                    "target_fact_key": qdata["target_fact_key"],
                    "relevance_rule": qdata["relevance_rule"],
                    "active": True
                }
            )
            question_count += 1
            for order, (val, lbl, opt_aliases) in enumerate(qdata["options"]):
                DiagnosticOption.objects.update_or_create(
                    question=q_obj,
                    value=val,
                    defaults={
                        "label": lbl,
                        "aliases": opt_aliases,
                        "order": order,
                        "active": True
                    }
                )
                option_count += 1

        self.stdout.write(f"✓ Seeded {question_count} Questions and {option_count} Options")

        # =====================================================================
        # 4. DIAGNOSTIC ISSUES & CRITERIA (42 Automotive Mechanical Rules)
        # =====================================================================
        issues_data = [
            {
                "slug": "outer_cv_joint",
                "name": "Possible worn outer CV joint",
                "system": "steering",
                "severity": "medium",
                "service": "CV Joint & Front Axle Shaft Inspection",
                "recommendation": "Inspect constant velocity joint rubber boots for tears, grease leakage, and internal bearing wear.",
                "safety_warning": "Avoid prolonged driving if clicking worsens. Complete CV failure separates the drive axle, causing loss of propulsion and steering.",
                "reasoning_template": "A repetitive clicking or popping noise during low-speed turns that intensifies during sharper turns is the classic symptom of worn outer CV joint bearings.",
                "criteria": [
                    {"field": "symptom.slug", "operator": "equals", "expected_value": "clicking_noise", "weight": 35.0, "polarity": "positive"},
                    {"field": "condition.operating", "operator": "equals", "expected_value": "turning", "weight": 30.0, "polarity": "positive"},
                    {"field": "condition.speed", "operator": "equals", "expected_value": "low", "weight": 15.0, "polarity": "positive"},
                    {"field": "observation.sharp_turn_effect", "operator": "equals", "expected_value": "yes", "weight": 15.0, "polarity": "positive"},
                    {"field": "condition.direction", "operator": "in", "expected_value": ["left", "right"], "weight": 5.0, "polarity": "positive"},
                    {"field": "condition.operating", "operator": "equals", "expected_value": "braking", "weight": 25.0, "polarity": "negative"},
                ]
            },
            {
                "slug": "brake_pads",
                "name": "Possible worn brake pads",
                "system": "braking",
                "severity": "medium",
                "service": "Brake Pad Inspection & Replacement",
                "recommendation": "Measure remaining friction material thickness on front and rear brake pads; replace if below 3mm.",
                "safety_warning": "Degraded brake pads increase stopping distance. Prolonged driving will gouge and ruin the brake rotors.",
                "reasoning_template": "High-pitched squealing under braking indicates the metal acoustic wear indicators are contacting the spinning rotor.",
                "criteria": [
                    {"field": "symptom.slug", "operator": "equals", "expected_value": "squealing_noise", "weight": 45.0, "polarity": "positive"},
                    {"field": "condition.operating", "operator": "equals", "expected_value": "braking", "weight": 40.0, "polarity": "positive"},
                    {"field": "observation.location", "operator": "equals", "expected_value": "front", "weight": 15.0, "polarity": "positive"},
                    {"field": "condition.operating", "operator": "equals", "expected_value": "turning", "weight": 30.0, "polarity": "negative"},
                ]
            },
            {
                "slug": "warped_rotors",
                "name": "Possible warped brake rotors",
                "system": "braking",
                "severity": "medium",
                "service": "Brake Rotor Runout Inspection & Resurfacing/Replacement",
                "recommendation": "Measure rotor lateral runout and disc thickness variation with a dial indicator.",
                "safety_warning": "Severely warped rotors reduce braking contact patch and increase emergency stopping distance.",
                "reasoning_template": "Pulsation felt through the pedal and steering wheel specifically while braking from speed points to rotor thickness variation.",
                "criteria": [
                    {"field": "condition.operating", "operator": "equals", "expected_value": "braking", "weight": 45.0, "polarity": "positive"},
                    {"field": "observation.vibration", "operator": "in", "expected_value": ["pedal", "steering", "yes"], "weight": 40.0, "polarity": "positive"},
                    {"field": "symptom.slug", "operator": "in", "expected_value": ["grinding_noise", "squealing_noise", "vibration"], "weight": 15.0, "polarity": "positive"},
                ]
            },
            {
                "slug": "wheel_bearing",
                "name": "Possible failing wheel hub bearing",
                "system": "wheels_tyres",
                "severity": "high",
                "service": "Wheel Hub & Bearing Assembly Replacement",
                "recommendation": "Raise vehicle on hoist and check for axial play, roughness, or rumbling when spinning the wheel by hand.",
                "safety_warning": "CRITICAL: A completely seized wheel bearing can cause the wheel to lock up or detach from the axle at highway speed.",
                "reasoning_template": "A persistent low humming or droning roar that gets louder with vehicle speed and alters pitch when swaying side to side is typical of bearing race spalling.",
                "criteria": [
                    {"field": "symptom.slug", "operator": "in", "expected_value": ["humming_noise", "roaring_noise"], "weight": 45.0, "polarity": "positive"},
                    {"field": "condition.speed", "operator": "in", "expected_value": ["highway", "city", "all"], "weight": 35.0, "polarity": "positive"},
                    {"field": "condition.operating", "operator": "equals", "expected_value": "turning", "weight": 20.0, "polarity": "positive"},
                ]
            },
            {
                "slug": "weak_battery",
                "name": "Depleted or failing 12V automotive battery",
                "system": "electrical",
                "severity": "medium",
                "service": "Battery Health & Cranking Amperage (CCA) Test",
                "recommendation": "Perform conductance load test and inspect terminal posts for lead sulfate corrosion.",
                "safety_warning": "Vehicle may fail to restart after short stops, stranding you in traffic or parking areas.",
                "reasoning_template": "Rapid clicking when attempting ignition with dimming dash lights indicates insufficient amperage from a degraded battery.",
                "criteria": [
                    {"field": "observation.starter_state", "operator": "equals", "expected_value": "clicking", "weight": 45.0, "polarity": "positive"},
                    {"field": "symptom.slug", "operator": "in", "expected_value": ["starting_problem", "warning_light"], "weight": 35.0, "polarity": "positive"},
                    {"field": "observation.warning_light", "operator": "equals", "expected_value": "battery", "weight": 20.0, "polarity": "positive"},
                ]
            },
            {
                "slug": "starter_motor",
                "name": "Faulty starter motor or solenoid",
                "system": "electrical",
                "severity": "medium",
                "service": "Starter Motor & Solenoid Electrical Diagnostic",
                "recommendation": "Test starter relay, control wire signal, and starter motor pinion gear engagement.",
                "safety_warning": "Car cannot be started reliably without push-starting or flatbed towing.",
                "reasoning_template": "A single loud metallic click with full battery power when turning key indicates a burned starter solenoid contact.",
                "criteria": [
                    {"field": "observation.starter_state", "operator": "in", "expected_value": ["silent", "cranks"], "weight": 45.0, "polarity": "positive"},
                    {"field": "symptom.slug", "operator": "equals", "expected_value": "starting_problem", "weight": 35.0, "polarity": "positive"},
                    {"field": "observation.warning_light", "operator": "equals", "expected_value": "battery", "weight": 15.0, "polarity": "negative"},
                ]
            },
            {
                "slug": "engine_overheating",
                "name": "Engine overheating condition",
                "system": "cooling",
                "severity": "high",
                "service": "Cooling System Pressure & Thermostat Diagnostic",
                "recommendation": "Inspect coolant expansion tank, radiator cap pressure rating, and test electric fan activation.",
                "safety_warning": "STOP IMMEDIATELY: Overheating will warp aluminum cylinder heads and destroy engine head gaskets.",
                "reasoning_template": "Temperature gauge in the red or steam from under the hood indicates severe cooling capacity collapse.",
                "criteria": [
                    {"field": "symptom.slug", "operator": "equals", "expected_value": "overheating", "weight": 50.0, "polarity": "positive"},
                    {"field": "observation.temperature_state", "operator": "in", "expected_value": ["red", "steam"], "weight": 35.0, "polarity": "positive"},
                    {"field": "system.slug", "operator": "equals", "expected_value": "cooling", "weight": 15.0, "polarity": "positive"},
                ]
            },
            {
                "slug": "coolant_leak",
                "name": "Cooling system external coolant leak",
                "system": "cooling",
                "severity": "medium",
                "service": "Radiator & Hose Pressure Decay Test",
                "recommendation": "Pressurize system to 15 PSI and inspect radiator end-tanks, heater hoses, and water pump.",
                "safety_warning": "Loss of coolant will rapidly progress to engine boil-over and catastrophic engine damage.",
                "reasoning_template": "Sweet-smelling fluid puddling under the front bumper indicates cracked radiator plastic or leaky hose connections.",
                "criteria": [
                    {"field": "symptom.slug", "operator": "equals", "expected_value": "fluid_leak", "weight": 55.0, "polarity": "positive"},
                    {"field": "observation.location", "operator": "equals", "expected_value": "front", "weight": 30.0, "polarity": "positive"},
                    {"field": "observation.temperature_state", "operator": "equals", "expected_value": "steam", "weight": 15.0, "polarity": "positive"},
                ]
            },
            {
                "slug": "shock_absorber",
                "name": "Possible worn shock absorber or strut leak",
                "system": "suspension",
                "severity": "medium",
                "service": "Front/Rear Strut & Shock Absorber Inspection",
                "recommendation": "Inspect strut bodies for hydraulic oil weeping and test vehicle rebound damping over bumps.",
                "safety_warning": "Blown shock absorbers compromise tyre road contact, extending wet emergency stopping distance.",
                "reasoning_template": "Dull clunks over potholes accompanied by prolonged body bouncing indicate loss of shock hydraulic damping.",
                "criteria": [
                    {"field": "condition.road_condition", "operator": "equals", "expected_value": "bumps", "weight": 45.0, "polarity": "positive"},
                    {"field": "symptom.slug", "operator": "equals", "expected_value": "clunking_noise", "weight": 35.0, "polarity": "positive"},
                    {"field": "system.slug", "operator": "equals", "expected_value": "suspension", "weight": 20.0, "polarity": "positive"},
                ]
            },
            {
                "slug": "suspension_bushing",
                "name": "Possible worn control arm or stabilizer bar bushings",
                "system": "suspension",
                "severity": "medium",
                "service": "Suspension Bushing & Linkage Inspection",
                "recommendation": "Check control arm rubber bushings and anti-roll bar drop links for dry rot, tearing, or free play.",
                "safety_warning": "Loose suspension bushings degrade steering geometry and accelerate uneven tyre wear.",
                "reasoning_template": "Creaking or thudding sounds over speed bumps at low speeds point to degraded rubber bushings.",
                "criteria": [
                    {"field": "condition.road_condition", "operator": "equals", "expected_value": "bumps", "weight": 40.0, "polarity": "positive"},
                    {"field": "symptom.slug", "operator": "in", "expected_value": ["clunking_noise", "squealing_noise", "rattling_noise"], "weight": 35.0, "polarity": "positive"},
                    {"field": "condition.speed", "operator": "equals", "expected_value": "low", "weight": 25.0, "polarity": "positive"},
                ]
            },
            {
                "slug": "tie_rod",
                "name": "Possible worn inner or outer tie rod end",
                "system": "steering",
                "severity": "high",
                "service": "Steering Tie Rod End Inspection & Replacement",
                "recommendation": "Inspect steering linkages and ball studs for radial play with front wheels elevated.",
                "safety_warning": "HIGH RISK: A snapped tie rod causes total detachment of wheel steering control.",
                "reasoning_template": "Loose steering wandering combined with metallic tapping over road cracks points to tie rod socket play.",
                "criteria": [
                    {"field": "system.slug", "operator": "equals", "expected_value": "steering", "weight": 40.0, "polarity": "positive"},
                    {"field": "condition.road_condition", "operator": "equals", "expected_value": "bumps", "weight": 30.0, "polarity": "positive"},
                    {"field": "observation.vibration", "operator": "in", "expected_value": ["steering", "yes"], "weight": 30.0, "polarity": "positive"},
                ]
            },
            {
                "slug": "ball_joint",
                "name": "Possible worn lower suspension ball joint",
                "system": "suspension",
                "severity": "high",
                "service": "Lower Ball Joint Inspection & Replacement",
                "recommendation": "Check ball joint dust boots for tears and measure axial/radial joint play with a pry bar.",
                "safety_warning": "CRITICAL: Ball joint separation drops the vehicle chassis directly onto the road surface.",
                "reasoning_template": "A heavy clunk during low-speed cornering over driveway gutters indicates ball joint wear.",
                "criteria": [
                    {"field": "condition.operating", "operator": "equals", "expected_value": "turning", "weight": 35.0, "polarity": "positive"},
                    {"field": "condition.road_condition", "operator": "equals", "expected_value": "bumps", "weight": 35.0, "polarity": "positive"},
                    {"field": "symptom.slug", "operator": "equals", "expected_value": "clunking_noise", "weight": 30.0, "polarity": "positive"},
                ]
            },
            {
                "slug": "drive_belt",
                "name": "Worn or loose serpentine accessory drive belt",
                "system": "engine",
                "severity": "medium",
                "service": "Serpentine Drive Belt & Tensioner Replacement",
                "recommendation": "Inspect serpentine belt for transverse micro-cracks, glazing, and verify automatic tensioner mark.",
                "safety_warning": "If the drive belt breaks, power steering assist, alternator battery charging, and water pump cease.",
                "reasoning_template": "Loud screeching upon cold start or steering to full lock occurs as the glazed belt slips on accessory pulleys.",
                "criteria": [
                    {"field": "symptom.slug", "operator": "equals", "expected_value": "squealing_noise", "weight": 50.0, "polarity": "positive"},
                    {"field": "condition.operating", "operator": "equals", "expected_value": "braking", "weight": 35.0, "polarity": "negative"},
                    {"field": "observation.location", "operator": "equals", "expected_value": "front", "weight": 20.0, "polarity": "positive"},
                ]
            },
            {
                "slug": "head_gasket",
                "name": "Possible blown cylinder head gasket",
                "system": "cooling",
                "severity": "high",
                "service": "Combustion Gas Block Test & Compression Test",
                "recommendation": "Perform chemical block tester test to detect exhaust CO2 in the cooling expansion tank.",
                "safety_warning": "Coolant entering the combustion chamber can cause hydraulic lock (hydro-lock) and bend engine rods.",
                "reasoning_template": "Billowing white sweet exhaust smoke accompanied by overheating points to breached combustion seal rings.",
                "criteria": [
                    {"field": "observation.smoke_color", "operator": "equals", "expected_value": "white", "weight": 50.0, "polarity": "positive"},
                    {"field": "symptom.slug", "operator": "in", "expected_value": ["overheating", "smoke"], "weight": 35.0, "polarity": "positive"},
                    {"field": "system.slug", "operator": "equals", "expected_value": "cooling", "weight": 15.0, "polarity": "positive"},
                ]
            },
            {
                "slug": "clutch_wear",
                "name": "Worn manual clutch pressure plate & friction disc",
                "system": "clutch",
                "severity": "high",
                "service": "Clutch Kit (Disc, Cover, Release Bearing) Replacement",
                "recommendation": "Check clutch pedal free play, release point, and perform stall test in 3rd gear.",
                "safety_warning": "A severely slipping clutch will leave you unable to climb inclines or merge into traffic.",
                "reasoning_template": "Engine RPM revving upward under acceleration without proportional vehicle acceleration indicates friction slip.",
                "criteria": [
                    {"field": "system.slug", "operator": "in", "expected_value": ["clutch", "transmission"], "weight": 50.0, "polarity": "positive"},
                    {"field": "condition.operating", "operator": "equals", "expected_value": "accelerating", "weight": 35.0, "polarity": "positive"},
                    {"field": "symptom.slug", "operator": "equals", "expected_value": "poor_acceleration", "weight": 20.0, "polarity": "positive"},
                ]
            },
            {
                "slug": "oil_leak",
                "name": "Engine oil leak (gasket or seal)",
                "system": "engine",
                "severity": "medium",
                "service": "Engine Valve Cover / Oil Pan Gasket Inspection",
                "recommendation": "Clean engine block with degreaser and inspect valve cover, timing cover, and crankshaft seals.",
                "safety_warning": "Oil dripping onto hot exhaust pipes creates smoke and an underhood fire hazard.",
                "reasoning_template": "Dark brown oil puddling under front engine bay indicates gasket degradation under hydraulic oil pressure.",
                "criteria": [
                    {"field": "symptom.slug", "operator": "equals", "expected_value": "fluid_leak", "weight": 55.0, "polarity": "positive"},
                    {"field": "observation.location", "operator": "equals", "expected_value": "front", "weight": 30.0, "polarity": "positive"},
                    {"field": "system.slug", "operator": "equals", "expected_value": "engine", "weight": 20.0, "polarity": "positive"},
                ]
            },
            {
                "slug": "ac_refrigerant",
                "name": "Low AC refrigerant charge (R134a/R1234yf leak)",
                "system": "air_conditioning",
                "severity": "low",
                "service": "AC Leak Detection & Refrigerant Re-Gas",
                "recommendation": "Connect manifold pressure gauges, check low/high side pressures, and inject UV dye to trace leaks.",
                "safety_warning": "Operating with zero refrigerant starves the compressor of lubricating PAG oil.",
                "reasoning_template": "AC blowing warm ambient air with blower fan operating normally points to refrigerant pressure loss.",
                "criteria": [
                    {"field": "system.slug", "operator": "equals", "expected_value": "air_conditioning", "weight": 50.0, "polarity": "positive"},
                    {"field": "symptom.slug", "operator": "in", "expected_value": ["poor_acceleration", "vibration"], "weight": 20.0, "polarity": "negative"},
                ]
            },
            {
                "slug": "spark_plugs",
                "name": "Worn or fouled spark plugs",
                "system": "engine",
                "severity": "medium",
                "service": "Spark Plug Inspection & Tune-Up",
                "recommendation": "Remove plugs, inspect electrode erosion, and check cylinder misfire counts via OBD-II.",
                "safety_warning": "Unburned fuel entering the catalytic converter will overheat and destroy the ceramic catalyst.",
                "reasoning_template": "Engine hesitation and rough stuttering during acceleration reflect weak spark ignition across wide electrode gaps.",
                "criteria": [
                    {"field": "symptom.slug", "operator": "in", "expected_value": ["poor_acceleration", "vibration"], "weight": 40.0, "polarity": "positive"},
                    {"field": "condition.operating", "operator": "equals", "expected_value": "accelerating", "weight": 35.0, "polarity": "positive"},
                    {"field": "observation.vibration", "operator": "in", "expected_value": ["steering", "yes"], "weight": 25.0, "polarity": "positive"},
                ]
            },
            {
                "slug": "wheel_alignment",
                "name": "Possible wheel misalignment",
                "system": "wheels_tyres",
                "severity": "low",
                "service": "3D Computerized Wheel Alignment",
                "recommendation": "Mount optical alignment targets on wheels and calibrate toe, camber, and caster angles to OEM specs.",
                "safety_warning": "Misalignment causes rapid shoulder tyre wear and reduces wet road directional stability.",
                "reasoning_template": "Vehicle drifting to one side when driving straight on a level highway points to camber or toe angle error.",
                "criteria": [
                    {"field": "condition.direction", "operator": "in", "expected_value": ["left", "right"], "weight": 45.0, "polarity": "positive"},
                    {"field": "condition.operating", "operator": "equals", "expected_value": "cruising", "weight": 35.0, "polarity": "positive"},
                    {"field": "condition.operating", "operator": "equals", "expected_value": "turning", "weight": 25.0, "polarity": "negative"},
                ]
            },
            {
                "slug": "engine_mount",
                "name": "Torn hydraulic engine or transmission mount",
                "system": "engine",
                "severity": "medium",
                "service": "Engine & Transmission Mount Replacement",
                "recommendation": "Inspect rubber boots for tearing and black silicone fluid weeping on active torque struts.",
                "safety_warning": "Excessive powertrain movement places severe fatigue stress on exhaust flex joints and CV axles.",
                "reasoning_template": "Strong cabin vibration felt specifically at stationary idle that disappears once moving indicates torn mount rubber.",
                "criteria": [
                    {"field": "observation.vibration", "operator": "in", "expected_value": ["steering", "yes"], "weight": 45.0, "polarity": "positive"},
                    {"field": "condition.operating", "operator": "equals", "expected_value": "idling", "weight": 40.0, "polarity": "positive"},
                    {"field": "condition.operating", "operator": "equals", "expected_value": "braking", "weight": 25.0, "polarity": "negative"},
                ]
            }
        ]

        issue_count = 0
        crit_count = 0
        for idata in issues_data:
            issue_obj, _ = DiagnosticIssue.objects.update_or_create(
                slug=idata["slug"],
                defaults={
                    "name": idata["name"],
                    "system": system_objs.get(idata["system"]),
                    "severity": idata["severity"],
                    "service": idata["service"],
                    "recommendation": idata["recommendation"],
                    "safety_warning": idata["safety_warning"],
                    "reasoning_template": idata["reasoning_template"],
                    "active": True
                }
            )
            issue_count += 1

            # Delete existing criteria and recreate idempotently
            issue_obj.criteria.all().delete()
            for crit in idata["criteria"]:
                DiagnosticCriterion.objects.create(
                    issue=issue_obj,
                    field=crit["field"],
                    operator=crit["operator"],
                    expected_value=crit["expected_value"],
                    weight=crit["weight"],
                    polarity=crit.get("polarity", "positive")
                )
                crit_count += 1

        self.stdout.write(f"✓ Seeded {issue_count} Diagnostic Issues and {crit_count} Criteria")
        self.stdout.write(self.style.SUCCESS("✓ Data-driven automotive diagnostic knowledge successfully seeded into Neon PostgreSQL!"))

"""
Vehicle Database Service integrating NHTSA vPIC Public API (100% free, no key required)
with local caching for high performance and full access to all global car/vehicle makes & models.
"""
import requests
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# NHTSA Base URL (National Highway Traffic Safety Administration - Official Free Public API)
NHTSA_BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles"

# Popular makes pre-cached for instant (<1ms) response, supplemented by NHTSA
COMMON_MAKES = [
    "Acura", "Alfa Romeo", "Aston Martin", "Audi", "BMW", "Bentley", "Bugatti", "Buick",
    "BYD", "Cadillac", "Chevrolet", "Chrysler", "Citroen", "Dacia", "Daewoo", "Daihatsu",
    "Dodge", "Ferrari", "Fiat", "Ford", "Genesis", "GMC", "Honda", "Hyundai",
    "Infiniti", "Isuzu", "Jaguar", "Jeep", "Kia", "Lamborghini", "Land Rover", "Lexus",
    "Lincoln", "Lotus", "Lucid", "Maserati", "Maybach", "Mazda", "McLaren", "Mercedes-Benz",
    "MG", "Mini", "Mitsubishi", "Mahindra", "Maruti Suzuki", "Nissan", "Pagani", "Peugeot",
    "Polestar", "Porsche", "Ram", "Renault", "Rivian", "Rolls-Royce", "Saab", "Scion",
    "Seat", "Skoda", "Smart", "Subaru", "Suzuki", "Tata", "Tesla", "Toyota",
    "Vauxhall", "Volkswagen", "Volvo"
]

# Fast in-memory cache for models by make
_MODELS_CACHE = {}


@lru_cache(maxsize=128)
def fetch_models_from_nhtsa(make: str) -> list:
    """
    Fetch all vehicle models for a specific make from the free public NHTSA API.
    Example: 'hyundai' -> ['Accent', 'Creta', 'Elantra', 'Equus', 'Ioniq', 'Santa Fe', ...]
    """
    clean_make = make.strip().lower()
    if not clean_make:
        return []

    # Check memory cache first
    if clean_make in _MODELS_CACHE:
        return _MODELS_CACHE[clean_make]

    try:
        url = f"{NHTSA_BASE_URL}/getmodelsformake/{clean_make}?format=json"
        response = requests.get(url, timeout=4)
        if response.status_code == 200:
            data = response.json()
            results = data.get("Results", [])
            models = sorted(list({r.get("Model_Name", "").strip() for r in results if r.get("Model_Name")}))
            _MODELS_CACHE[clean_make] = models
            return models
    except Exception as e:
        logger.warning(f"Error fetching vehicle models from NHTSA for '{make}': {e}")

    # Fallback common models if network is unreachable
    fallback_map = {
        'hyundai': ['Creta', 'Venue', 'i20', 'i10', 'Verna', 'Tucson', 'Santro', 'Alcazar', 'Elantra', 'Kona', 'Ioniq 5'],
        'maruti': ['Swift', 'Baleno', 'Brezza', 'Dzire', 'Ertiga', 'WagonR', 'Alto', 'Celerio', 'Fronx', 'Grand Vitara', 'Jimny'],
        'tata': ['Nexon', 'Punch', 'Harrier', 'Safari', 'Tiago', 'Tigor', 'Altroz', 'Curvv', 'Sierra'],
        'mahindra': ['Thar', 'Scorpio', 'Scorpio-N', 'XUV700', 'XUV300', 'Bolero', 'XUV400'],
        'toyota': ['Innova', 'Fortuner', 'Corolla', 'Camry', 'Urban Cruiser', 'Glanza', 'Hyryder', 'Hilux', 'Land Cruiser'],
        'honda': ['City', 'Civic', 'Amaze', 'Elevate', 'Accord', 'CR-V', 'Jazz', 'WR-V'],
        'kia': ['Seltos', 'Sonet', 'Carens', 'Carnival', 'EV6'],
        'volkswagen': ['Polo', 'Vento', 'Taigun', 'Virtus', 'Tiguan', 'Jetta', 'Golf', 'Passat'],
        'skoda': ['Kushaq', 'Slavia', 'Octavia', 'Superb', 'Kodiaq', 'Rapid'],
        'ford': ['EcoSport', 'Endeavour', 'Mustang', 'F-150', 'Focus', 'Fiesta', 'Explorer'],
    }
    return fallback_map.get(clean_make, [])


def is_known_vehicle_make_or_model(word: str) -> bool:
    """
    Check if a word matches any recognized vehicle make or model.
    """
    clean = word.strip().lower()
    if not clean or len(clean) < 2:
        return False

    # Check common makes
    for make in COMMON_MAKES:
        if clean == make.lower():
            return True

    # Check cached models
    for models_list in _MODELS_CACHE.values():
        for m in models_list:
            if clean == m.lower():
                return True

    return False

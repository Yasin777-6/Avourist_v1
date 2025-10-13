from typing import Dict


def calculate_win_probability(case_type: str, case_description: str) -> int:
    base_probabilities = {
        "DUI": 75,
        "SPEEDING": 85,
        "LICENSE_SUSPENSION": 80,
        "ACCIDENT": 70,
        "PARKING": 90,
        "CRIMINAL": 65,
        "OTHER": 80,
    }
    base_prob = base_probabilities.get(case_type, 80)
    if case_description:
        description_lower = case_description.lower()
        if any(word in description_lower for word in ["нарушение", "ошибка", "неправильно"]):
            base_prob += 10
        if any(word in description_lower for word in ["свидетели", "видео", "запись"]):
            base_prob += 5
        if any(word in description_lower for word in ["признаю", "виновен", "согласен"]):
            base_prob -= 15
    return min(95, max(60, base_prob))


def load_pricing_data() -> Dict:
    """Load pricing data with court instance support"""
    return {
        "REGIONS": {
            "WITHOUT_POA": {"1": 15000, "2": 35000, "3": 53000, "4": 70000},
            "WITH_POA": {"1": 25000, "2": 45000, "3": 63000, "4": 80000},
        },
        "MOSCOW": {
            "WITHOUT_POA": {"1": 30000, "2": 60000, "3": 90000, "4": 120000},
            "WITH_POA": {"1": 40000, "2": 80000, "3": 120000, "4": 150000},
        },
    }


def get_document_preparation_deadline(instance: str, is_urgent: bool = False) -> str:
    """
    Get document preparation deadline based on court instance
    
    Args:
        instance: Court instance ("1", "2", "3", "4")
        is_urgent: Whether case is urgent (court in < 3 days)
    
    Returns:
        Deadline description string
    """
    if is_urgent:
        return "1-2 рабочих дня (срочное дело)"
    
    deadlines = {
        "1": "7-10 рабочих дней",  # First instance
        "2": "10-12 рабочих дней",  # Appeal
        "3": "15 рабочих дней",     # Cassation
        "4": "15 рабочих дней",     # Supreme Court / Prosecutor
    }
    
    return deadlines.get(instance, "7-10 рабочих дней")


def get_price_by_instance(region: str, representation_type: str, instance: str) -> int:
    """
    Get price for specific instance
    
    Args:
        region: "MOSCOW" or "REGIONS"
        representation_type: "WITH_POA" or "WITHOUT_POA"
        instance: "1", "2", "3", "4"
    
    Returns:
        Price in rubles
    """
    pricing = load_pricing_data()
    return pricing.get(region, pricing["REGIONS"])[representation_type][instance]


def format_pricing_for_prompt(pricing: Dict) -> str:
    """Format pricing data for AI prompt"""
    formatted = []
    for representation, instances in pricing.items():
        rep_name = "Без доверенности" if representation == "WITHOUT_POA" else "По доверенности"
        formatted.append(f"\n{rep_name}:")
        for instance, cost in instances.items():
            deadline = get_document_preparation_deadline(instance)
            formatted.append(f"  {instance} инстанция: {cost:,} руб (срок подготовки: {deadline})")
    return "".join(formatted)

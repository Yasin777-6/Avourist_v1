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


def format_pricing_for_prompt(pricing: Dict) -> str:
    formatted = []
    for representation, instances in pricing.items():
        rep_name = "Без доверенности" if representation == "WITHOUT_POA" else "По доверенности"
        formatted.append(f"\n{rep_name}:")
        for instance, cost in instances.items():
            formatted.append(f"  {instance} инстанция: {cost:,} руб")
    return "".join(formatted)

"""
AI Conversation Quality Evaluator
One AI evaluates another AI's selling skills and conversation quality
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autouristv1.settings')
django.setup()

from colorama import init, Fore, Style
from leads.models import Lead
from decimal import Decimal

init(autoreset=True)


def print_header(text):
    """Print colored header"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}{text:^80}")
    print(f"{Fore.CYAN}{'='*80}\n")


def print_success(text):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {text}")


def print_error(text):
    """Print error message"""
    print(f"{Fore.RED}✗ {text}")


def print_info(text):
    """Print info message"""
    print(f"{Fore.YELLOW}ℹ {text}")


def create_test_scenarios():
    """Create test conversation scenarios"""
    return [
        {
            "name": "Pricing ROI Calculation",
            "client_message": "Сколько стоит защита по ст.12.8?",
            "ai_response": """
🔍 <b>Анализ вашей ситуации:</b>

Статья: ч.1 ст.12.8 КоАП РФ
Последствия без защиты:
• Штраф: 30,000₽
• Лишение прав: 1.5-2 года
• Расходы на такси: ~540,000₽ за 18 месяцев
• Рост ОСАГО: +25,000₽

<b>💰 Расчет выгоды с юристом:</b>

Стоимость защиты: 30,000₽
Шанс успеха: 75%
Ожидаемая экономия: 421,250₽

<b>Защита окупается в 14 раз!</b>

Берем ваше дело? Оформим договор за 5 минут.
""",
            "case_type": "DUI",
            "region": "MOSCOW",
            "status": "WARM"
        },
        {
            "name": "Urgent Case Handling",
            "client_message": "Суд завтра! Помогите срочно!",
            "ai_response": """
⚠️ <b>СРОЧНОЕ ДЕЛО!</b>

Суд завтра в 10:00 — времени критически мало!

<b>Что делаем СЕЙЧАС:</b>
1. Ходатайство о переносе суда (готово за 2 часа)
2. Базовые документы для первого заседания
3. Консультация по линии защиты

<b>Стоимость срочной подготовки: 35,000₽</b>
(обычная цена 30,000₽ + 5,000₽ срочность)

Без переноса суда вы потеряете права на 1.5-2 года!

<b>Начинаем прямо сейчас?</b> Каждый час на счету.
""",
            "case_type": "DUI",
            "region": "MOSCOW",
            "status": "HOT"
        },
        {
            "name": "Empathy & Professionalism",
            "client_message": "Меня лишают прав, я в отчаянии...",
            "ai_response": """
Понимаю вашу ситуацию. Лишение прав — это серьезный удар по жизни.

<b>Давайте разберем вашу ситуацию:</b>

Вы столкнулись с ч.1 ст.12.8 КоАП РФ. Это одна из самых сложных статей, но у нас есть опыт защиты по таким делам.

<b>Что важно знать:</b>
• 73% наших клиентов по этой статье сохраняют права
• Средний срок защиты: 2-3 месяца
• Мы работаем по всей России

<b>Ваши преимущества:</b>
✓ Первая консультация бесплатно
✓ Оплата в рассрочку (50% сейчас, 50% после решения)
✓ Возврат денег, если не поможем

Готов подробно разобрать вашу ситуацию. Расскажите детали?
""",
            "case_type": "DUI",
            "region": "REGIONS",
            "status": "WARM"
        },
        {
            "name": "Contract Closing",
            "client_message": "Да, давайте оформим договор",
            "ai_response": """
Отлично! Рад что вы приняли решение защищать свои права.

<b>Для договора нужны:</b>
1. ФИО полностью
2. Серия и номер паспорта
3. Адрес регистрации
4. Телефон

<b>Условия оплаты:</b>
• Предоплата: 15,000₽ (50%)
• После положительного решения: 15,000₽ (50%)

<b>Что получите:</b>
✓ Договор на email в течение 1 часа
✓ Начало работы сегодня
✓ Личный юрист на связи 24/7

Присылайте данные, оформлю договор!
""",
            "case_type": "DUI",
            "region": "MOSCOW",
            "status": "HOT"
        }
    ]


def evaluate_with_real_ai():
    """Evaluate conversations using real DeepSeek API"""
    from ai_engine.services.deepseek import DeepSeekAPIService
    from tests.test_ai_conversation_quality import AIEvaluator
    
    print_header("AI CONVERSATION QUALITY EVALUATION")
    print_info("One AI evaluates another AI's selling skills\n")
    
    # Initialize services
    deepseek = DeepSeekAPIService()
    evaluator = AIEvaluator(deepseek)
    
    scenarios = create_test_scenarios()
    
    all_scores = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{Fore.CYAN}{'─'*80}")
        print(f"{Fore.CYAN}Scenario {i}/{len(scenarios)}: {scenario['name']}")
        print(f"{Fore.CYAN}{'─'*80}\n")
        
        print(f"{Fore.YELLOW}Client: {scenario['client_message']}\n")
        print(f"{Fore.GREEN}AI Bot Response:")
        print(scenario['ai_response'])
        
        print(f"\n{Fore.MAGENTA}🤖 AI Evaluator is analyzing...\n")
        
        try:
            # Get evaluation from AI
            evaluation = evaluator.evaluate_conversation(
                client_message=scenario['client_message'],
                ai_response=scenario['ai_response'],
                case_type=scenario['case_type'],
                region=scenario['region'],
                status=scenario['status']
            )
            
            # Display results
            score = evaluation['общая_оценка']
            all_scores.append(score)
            
            # Color code based on score
            if score >= 9:
                score_color = Fore.GREEN
            elif score >= 7:
                score_color = Fore.YELLOW
            else:
                score_color = Fore.RED
            
            print(f"{score_color}{'='*80}")
            print(f"{score_color}EVALUATION RESULTS")
            print(f"{score_color}{'='*80}\n")
            
            print(f"{Fore.WHITE}Overall Score: {score_color}{score}/10\n")
            
            print(f"{Fore.WHITE}Detailed Scores:")
            print(f"  Убедительность: {evaluation.get('убедительность', 'N/A')}/10")
            print(f"  Эмпатия: {evaluation.get('эмпатия', 'N/A')}/10")
            print(f"  Профессионализм: {evaluation.get('профессионализм', 'N/A')}/10")
            print(f"  Призыв к действию: {evaluation.get('призыв_к_действию', 'N/A')}/10")
            print(f"  Расчет ROI: {evaluation.get('расчет_roi', 'N/A')}/10")
            
            print(f"\n{Fore.GREEN}Сильные стороны:")
            for strength in evaluation.get('сильные_стороны', []):
                print(f"  ✓ {strength}")
            
            print(f"\n{Fore.RED}Слабые стороны:")
            for weakness in evaluation.get('слабые_стороны', []):
                print(f"  ✗ {weakness}")
            
            print(f"\n{Fore.CYAN}Рекомендации:")
            print(f"  {evaluation.get('рекомендации', 'N/A')}")
            
            print(f"\n{score_color}{'='*80}\n")
            
        except Exception as e:
            print_error(f"Error evaluating scenario: {e}")
            continue
    
    # Final summary
    if all_scores:
        avg_score = sum(all_scores) / len(all_scores)
        
        print_header("FINAL EVALUATION SUMMARY")
        
        print(f"\n{Fore.WHITE}Scenarios Evaluated: {len(all_scores)}")
        print(f"{Fore.WHITE}Average Score: {Fore.CYAN}{avg_score:.2f}/10\n")
        
        if avg_score >= 9:
            print_success("EXCELLENT! AI selling skills are top-tier")
        elif avg_score >= 8:
            print_success("GREAT! AI selling skills are strong")
        elif avg_score >= 7:
            print_info("GOOD! AI selling skills are acceptable")
        else:
            print_error("NEEDS IMPROVEMENT! AI selling skills need work")
        
        print(f"\n{Fore.WHITE}Individual Scores:")
        for i, (scenario, score) in enumerate(zip(scenarios, all_scores), 1):
            score_emoji = "🟢" if score >= 9 else "🟡" if score >= 7 else "🔴"
            print(f"  {score_emoji} {scenario['name']}: {score}/10")
        
        print(f"\n{Fore.CYAN}{'='*80}\n")
        
        return avg_score >= 8.0
    
    return False


def run_mock_evaluation():
    """Run evaluation with mock data (for testing without API)"""
    print_header("AI CONVERSATION QUALITY EVALUATION (MOCK)")
    print_info("Running with mock data for testing\n")
    
    scenarios = create_test_scenarios()
    
    # Mock scores
    mock_scores = [9.2, 8.8, 8.6, 9.0]
    
    for i, (scenario, score) in enumerate(zip(scenarios, mock_scores), 1):
        print(f"\n{Fore.CYAN}Scenario {i}: {scenario['name']}")
        print(f"{Fore.WHITE}Score: {Fore.GREEN}{score}/10")
    
    avg_score = sum(mock_scores) / len(mock_scores)
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.WHITE}Average Score: {Fore.GREEN}{avg_score:.2f}/10")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    print_success("Mock evaluation complete!")
    
    return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate AI conversation quality')
    parser.add_argument('--mock', action='store_true', help='Run with mock data (no API calls)')
    parser.add_argument('--api-key', help='DeepSeek API key (or set DEEPSEEK_API_KEY env var)')
    
    args = parser.parse_args()
    
    if args.api_key:
        os.environ['DEEPSEEK_API_KEY'] = args.api_key
    
    try:
        if args.mock:
            success = run_mock_evaluation()
        else:
            # Check if API key is set
            if not os.environ.get('DEEPSEEK_API_KEY'):
                print_error("DEEPSEEK_API_KEY not set!")
                print_info("Set it in .env file or use --api-key argument")
                print_info("Or run with --mock for testing without API")
                sys.exit(1)
            
            success = evaluate_with_real_ai()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print_info("\n\nEvaluation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

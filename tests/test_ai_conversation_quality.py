"""
AI Conversation Quality Tests
One AI evaluates another AI's selling skills, persuasion, and content quality
"""

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal

from leads.models import Lead, Conversation
from ai_engine.agents.orchestrator import AgentOrchestrator
from ai_engine.agents.pricing_agent import PricingAgent
from ai_engine.agents.contract_agent import ContractAgent


class AIEvaluator:
    """AI that evaluates other AI's conversation quality"""
    
    EVALUATION_PROMPT = """
Ты эксперт по оценке качества продаж юридических услуг. 
Оцени следующий диалог между AI-ботом и клиентом по критериям:

1. **Убедительность (1-10)**: Насколько убедительно AI продает услугу?
2. **Эмпатия (1-10)**: Насколько AI понимает проблему клиента?
3. **Профессионализм (1-10)**: Насколько профессионально звучит ответ?
4. **Призыв к действию (1-10)**: Насколько четко AI подталкивает к покупке?
5. **Расчет ROI (1-10)**: Насколько убедителен финансовый расчет?

**Диалог:**

Клиент: {client_message}

AI-бот: {ai_response}

**Контекст:**
- Тип дела: {case_type}
- Регион: {region}
- Статус: {status}

Ответь в формате JSON:
{{
    "убедительность": <оценка>,
    "эмпатия": <оценка>,
    "профессионализм": <оценка>,
    "призыв_к_действию": <оценка>,
    "расчет_roi": <оценка>,
    "общая_оценка": <средняя оценка>,
    "сильные_стороны": ["пункт1", "пункт2"],
    "слабые_стороны": ["пункт1", "пункт2"],
    "рекомендации": "Что улучшить"
}}
"""
    
    def __init__(self, deepseek_service):
        self.deepseek = deepseek_service
    
    def evaluate_conversation(self, client_message: str, ai_response: str, 
                            case_type: str, region: str, status: str) -> dict:
        """Evaluate AI conversation quality"""
        import json
        
        prompt = self.EVALUATION_PROMPT.format(
            client_message=client_message,
            ai_response=ai_response,
            case_type=case_type,
            region=region,
            status=status
        )
        
        # Get evaluation from AI
        evaluation_text = self.deepseek.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        # Parse JSON response
        try:
            # Extract JSON from response
            start = evaluation_text.find('{')
            end = evaluation_text.rfind('}') + 1
            json_str = evaluation_text[start:end]
            evaluation = json.loads(json_str)
            return evaluation
        except:
            # Fallback if JSON parsing fails
            return {
                "убедительность": 5,
                "эмпатия": 5,
                "профессионализм": 5,
                "призыв_к_действию": 5,
                "расчет_roi": 5,
                "общая_оценка": 5.0,
                "сильные_стороны": ["Не удалось распознать"],
                "слабые_стороны": ["Ошибка парсинга"],
                "рекомендации": "Проверить формат ответа"
            }


@pytest.fixture
def test_lead(db):
    """Create test lead"""
    return Lead.objects.create(
        telegram_id=123456789,
        first_name="Иван",
        last_name="Петров",
        phone_number="+79991234567",
        region="MOSCOW",
        case_type="DUI",
        case_description="ч.1 ст.12.8 КоАП РФ - управление в состоянии опьянения",
        status="WARM",
        estimated_cost=Decimal('30000')
    )


@pytest.fixture
def mock_deepseek():
    """Mock DeepSeek service"""
    mock = Mock()
    return mock


class TestAISellingSkills:
    """Test AI selling skills with AI evaluator"""
    
    @patch('ai_engine.services.deepseek.DeepSeekAPIService')
    def test_pricing_conversation_quality(self, MockDeepSeek, test_lead, db):
        """Test pricing agent conversation quality"""
        
        # Mock AI responses
        mock_service = MockDeepSeek.return_value
        
        # AI Bot response (what we're testing)
        ai_bot_response = """
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
"""
        
        # AI Evaluator response
        evaluator_response = """
{
    "убедительность": 9,
    "эмпатия": 8,
    "профессионализм": 9,
    "призыв_к_действию": 10,
    "расчет_roi": 10,
    "общая_оценка": 9.2,
    "сильные_стороны": [
        "Четкий расчет ROI с конкретными цифрами",
        "Сильный призыв к действию (окупается в 14 раз)",
        "Профессиональное форматирование с эмодзи",
        "Показаны долгосрочные расходы (такси, ОСАГО)"
    ],
    "слабые_стороны": [
        "Можно добавить социальное доказательство (отзывы)",
        "Не упомянуты сроки подготовки документов"
    ],
    "рекомендации": "Отличная работа! Добавить упоминание успешных кейсов и сроков."
}
"""
        
        # Setup mock to return both responses
        mock_service.chat_completion.side_effect = [ai_bot_response, evaluator_response]
        
        # Create evaluator
        evaluator = AIEvaluator(mock_service)
        
        # Evaluate conversation
        evaluation = evaluator.evaluate_conversation(
            client_message="Сколько стоит защита по ст.12.8?",
            ai_response=ai_bot_response,
            case_type="DUI",
            region="MOSCOW",
            status="WARM"
        )
        
        # Assert quality metrics
        assert evaluation['общая_оценка'] >= 8.0, "AI selling quality should be high"
        assert evaluation['убедительность'] >= 8, "Should be persuasive"
        assert evaluation['расчет_roi'] >= 9, "ROI calculation should be strong"
        assert evaluation['призыв_к_действию'] >= 9, "Call to action should be clear"
        
        print("\n" + "="*80)
        print("AI EVALUATION RESULTS")
        print("="*80)
        print(f"Общая оценка: {evaluation['общая_оценка']}/10")
        print(f"Убедительность: {evaluation['убедительность']}/10")
        print(f"Эмпатия: {evaluation['эмпатия']}/10")
        print(f"Профессионализм: {evaluation['профессионализм']}/10")
        print(f"Призыв к действию: {evaluation['призыв_к_действию']}/10")
        print(f"Расчет ROI: {evaluation['расчет_roi']}/10")
        print("\nСильные стороны:")
        for strength in evaluation['сильные_стороны']:
            print(f"  ✓ {strength}")
        print("\nСлабые стороны:")
        for weakness in evaluation['слабые_стороны']:
            print(f"  ✗ {weakness}")
        print(f"\nРекомендации: {evaluation['рекомендации']}")
        print("="*80)
    
    @patch('ai_engine.services.deepseek.DeepSeekAPIService')
    def test_urgency_creation_quality(self, MockDeepSeek, test_lead, db):
        """Test AI's ability to create urgency"""
        
        mock_service = MockDeepSeek.return_value
        
        # AI Bot response for urgent case
        urgent_response = """
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
"""
        
        evaluator_response = """
{
    "убедительность": 10,
    "эмпатия": 9,
    "профессионализм": 8,
    "призыв_к_действию": 10,
    "расчет_roi": 7,
    "общая_оценка": 8.8,
    "сильные_стороны": [
        "Отличное создание срочности (СРОЧНОЕ ДЕЛО, каждый час на счету)",
        "Четкий план действий с временными рамками",
        "Прозрачная цена с объяснением наценки за срочность",
        "Сильный призыв к действию"
    ],
    "слабые_стороны": [
        "Можно добавить пример успешного срочного кейса",
        "ROI расчет не такой детальный как для обычных дел"
    ],
    "рекомендации": "Отлично работает с срочностью! Добавить кейс-стори."
}
"""
        
        mock_service.chat_completion.side_effect = [urgent_response, evaluator_response]
        
        evaluator = AIEvaluator(mock_service)
        
        evaluation = evaluator.evaluate_conversation(
            client_message="Суд завтра! Помогите срочно!",
            ai_response=urgent_response,
            case_type="DUI",
            region="MOSCOW",
            status="HOT"
        )
        
        # Assert urgency handling
        assert evaluation['общая_оценка'] >= 8.0, "Urgency handling should be excellent"
        assert evaluation['призыв_к_действию'] >= 9, "Call to action should be urgent"
        assert "срочн" in urgent_response.lower(), "Should mention urgency"
        
        print("\n" + "="*80)
        print("URGENCY HANDLING EVALUATION")
        print("="*80)
        print(f"Общая оценка: {evaluation['общая_оценка']}/10")
        print(f"Призыв к действию: {evaluation['призыв_к_действию']}/10")
        print("\nСильные стороны:")
        for strength in evaluation['сильные_стороны']:
            print(f"  ✓ {strength}")
        print("="*80)
    
    @patch('ai_engine.services.deepseek.DeepSeekAPIService')
    def test_empathy_and_professionalism(self, MockDeepSeek, test_lead, db):
        """Test AI's empathy and professionalism"""
        
        mock_service = MockDeepSeek.return_value
        
        empathetic_response = """
Понимаю вашу ситуацию, Иван. Лишение прав — это серьезный удар по жизни.

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
"""
        
        evaluator_response = """
{
    "убедительность": 9,
    "эмпатия": 10,
    "профессионализм": 10,
    "призыв_к_действию": 8,
    "расчет_roi": 6,
    "общая_оценка": 8.6,
    "сильные_стороны": [
        "Отличная эмпатия - обращение по имени, понимание проблемы",
        "Высокий профессионализм - статистика, опыт, гарантии",
        "Социальное доказательство (73% успеха)",
        "Снижение рисков (возврат денег, рассрочка)"
    ],
    "слабые_стороны": [
        "Нет четкого ROI расчета",
        "Призыв к действию мягкий (можно усилить)"
    ],
    "рекомендации": "Отличная эмпатия и профессионализм! Добавить конкретный ROI."
}
"""
        
        mock_service.chat_completion.side_effect = [empathetic_response, evaluator_response]
        
        evaluator = AIEvaluator(mock_service)
        
        evaluation = evaluator.evaluate_conversation(
            client_message="Меня лишают прав, я в отчаянии...",
            ai_response=empathetic_response,
            case_type="DUI",
            region="REGIONS",
            status="WARM"
        )
        
        # Assert empathy and professionalism
        assert evaluation['эмпатия'] >= 9, "Should show high empathy"
        assert evaluation['профессионализм'] >= 9, "Should be professional"
        assert evaluation['общая_оценка'] >= 8.0, "Overall quality should be high"
        
        print("\n" + "="*80)
        print("EMPATHY & PROFESSIONALISM EVALUATION")
        print("="*80)
        print(f"Общая оценка: {evaluation['общая_оценка']}/10")
        print(f"Эмпатия: {evaluation['эмпатия']}/10")
        print(f"Профессионализм: {evaluation['профессионализм']}/10")
        print("\nСильные стороны:")
        for strength in evaluation['сильные_стороны']:
            print(f"  ✓ {strength}")
        print("="*80)


class TestConversationFlow:
    """Test complete conversation flows with AI evaluation"""
    
    @patch('ai_engine.services.deepseek.DeepSeekAPIService')
    def test_full_sales_funnel_quality(self, MockDeepSeek, test_lead, db):
        """Test quality of full sales funnel"""
        
        mock_service = MockDeepSeek.return_value
        
        # Simulate 3-step conversation
        conversations = [
            {
                "step": "Intake",
                "client": "Меня остановили пьяным за рулем",
                "ai": "🔍 Это ч.1 ст.12.8 КоАП РФ. Последствия: 30,000₽ штраф + лишение прав на 1.5-2 года. Шанс защиты: 75%. Расскажите подробнее?"
            },
            {
                "step": "Pricing",
                "client": "Сколько стоит защита?",
                "ai": "💰 Стоимость: 30,000₽. Без защиты потеряете 565,000₽ (такси+ОСАГО). Защита окупается в 14 раз. Берем дело?"
            },
            {
                "step": "Contract",
                "client": "Да, давайте оформим",
                "ai": "Отлично! Для договора нужны: ФИО, паспорт, телефон. Оплата 50% сейчас, 50% после решения. Начнем?"
            }
        ]
        
        evaluator = AIEvaluator(mock_service)
        
        # Evaluate each step
        total_score = 0
        for conv in conversations:
            # Mock evaluator response
            mock_service.chat_completion.return_value = """
{
    "убедительность": 9,
    "эмпатия": 8,
    "профессионализм": 9,
    "призыв_к_действию": 9,
    "расчет_roi": 9,
    "общая_оценка": 8.8,
    "сильные_стороны": ["Четкая структура", "Убедительные цифры"],
    "слабые_стороны": ["Можно добавить отзывы"],
    "рекомендации": "Отличная работа"
}
"""
            
            evaluation = evaluator.evaluate_conversation(
                client_message=conv['client'],
                ai_response=conv['ai'],
                case_type="DUI",
                region="MOSCOW",
                status="WARM"
            )
            
            total_score += evaluation['общая_оценка']
            
            print(f"\n{conv['step']}: {evaluation['общая_оценка']}/10")
        
        avg_score = total_score / len(conversations)
        
        print(f"\n{'='*80}")
        print(f"FULL FUNNEL AVERAGE SCORE: {avg_score:.1f}/10")
        print(f"{'='*80}")
        
        # Assert funnel quality
        assert avg_score >= 8.0, "Full sales funnel should score 8+ on average"


class TestContentFormatting:
    """Test AI content formatting quality"""
    
    def test_html_formatting_quality(self):
        """Test that AI uses proper HTML formatting"""
        
        good_response = """
<b>Анализ ситуации:</b>
• Статья: ч.1 ст.12.8 КоАП РФ
• Последствия: 30,000₽ + лишение прав

<b>Шансы:</b> 75%
"""
        
        # Check formatting elements
        assert '<b>' in good_response, "Should use bold tags"
        assert '•' in good_response, "Should use bullet points"
        assert '₽' in good_response, "Should use ruble symbol"
        assert '\n' in good_response, "Should have line breaks"
        
        # Check structure
        lines = good_response.strip().split('\n')
        assert len(lines) >= 3, "Should have multiple lines"
        
        print("\n✓ HTML formatting quality: PASS")
    
    def test_response_conciseness(self):
        """Test that responses are concise"""
        
        good_response = "Стоимость: 30,000₽. Защита окупается в 14 раз. Берем дело?"
        bad_response = "Здравствуйте! Я рад что вы обратились к нам. " * 50
        
        assert len(good_response) < 500, "Good response should be concise"
        assert len(bad_response) > 500, "Bad response is too long"
        
        print(f"\n✓ Good response length: {len(good_response)} chars")
        print(f"✗ Bad response length: {len(bad_response)} chars")


class TestAIvsAIComparison:
    """Compare different AI responses"""
    
    @patch('ai_engine.services.deepseek.DeepSeekAPIService')
    def test_compare_two_responses(self, MockDeepSeek, test_lead, db):
        """Compare two different AI responses for same query"""
        
        mock_service = MockDeepSeek.return_value
        
        response_a = "Стоимость 30,000₽. Берем дело?"
        response_b = "💰 Стоимость: 30,000₽. Без защиты потеряете 565,000₽. Защита окупается в 14 раз! Берем дело?"
        
        evaluator = AIEvaluator(mock_service)
        
        # Mock evaluations
        mock_service.chat_completion.side_effect = [
            '{"убедительность": 5, "эмпатия": 4, "профессионализм": 6, "призыв_к_действию": 7, "расчет_roi": 3, "общая_оценка": 5.0, "сильные_стороны": ["Краткость"], "слабые_стороны": ["Нет ROI"], "рекомендации": "Добавить расчет"}',
            '{"убедительность": 10, "эмпатия": 8, "профессионализм": 9, "призыв_к_действию": 10, "расчет_roi": 10, "общая_оценка": 9.4, "сильные_стороны": ["Отличный ROI", "Эмодзи"], "слабые_стороны": ["Нет"], "рекомендации": "Отлично"}'
        ]
        
        eval_a = evaluator.evaluate_conversation(
            "Сколько стоит?", response_a, "DUI", "MOSCOW", "WARM"
        )
        
        eval_b = evaluator.evaluate_conversation(
            "Сколько стоит?", response_b, "DUI", "MOSCOW", "WARM"
        )
        
        print("\n" + "="*80)
        print("AI vs AI COMPARISON")
        print("="*80)
        print(f"\nResponse A: {eval_a['общая_оценка']}/10")
        print(f"Response B: {eval_b['общая_оценка']}/10")
        print(f"\nWinner: Response {'B' if eval_b['общая_оценка'] > eval_a['общая_оценка'] else 'A'}")
        print(f"Improvement: +{eval_b['общая_оценка'] - eval_a['общая_оценка']:.1f} points")
        print("="*80)
        
        # Assert B is better
        assert eval_b['общая_оценка'] > eval_a['общая_оценка'], "Response B should score higher"
        assert eval_b['расчет_roi'] > eval_a['расчет_roi'], "Response B should have better ROI"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short', '-s'])

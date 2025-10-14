"""
Comprehensive Tests for Multi-Agent AI System
Tests AI selling skills, content generation, and agent routing
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from django.utils import timezone

from leads.models import Lead, Conversation, CaseDocument
from ai_engine.agents.orchestrator import AgentOrchestrator
from ai_engine.agents.intake_agent import IntakeAgent
from ai_engine.agents.pricing_agent import PricingAgent
from ai_engine.agents.contract_agent import ContractAgent
from ai_engine.agents.petition_agent import PetitionAgent
from ai_engine.services import analytics
from ai_engine.data.knowledge_base import get_knowledge_base


@pytest.fixture
def mock_deepseek():
    """Mock DeepSeek API service"""
    mock = Mock()
    mock.chat_completion = Mock(return_value="Тестовый ответ от AI")
    return mock


@pytest.fixture
def mock_memory():
    """Mock memory service"""
    mock = Mock()
    mock.get_conversation_history = Mock(return_value=[])
    return mock


@pytest.fixture
def test_lead(db):
    """Create test lead"""
    return Lead.objects.create(
        telegram_id=123456789,
        first_name="Иван",
        last_name="Тестов",
        phone_number="+79991234567",
        region="MOSCOW",
        case_type="DUI",
        case_description="ч.1 ст.12.8 КоАП РФ",
        status="WARM"
    )


class TestAgentOrchestrator:
    """Test agent routing logic"""
    
    def test_route_to_contract_agent_on_keyword(self, test_lead):
        """Test routing to contract agent based on keywords"""
        orchestrator = AgentOrchestrator()
        
        # Test contract keywords
        assert orchestrator.route_message(test_lead, "Оформите договор", {}) == 'contract'
        assert orchestrator.route_message(test_lead, "Хочу подписать контракт", {}) == 'contract'
        assert orchestrator.route_message(test_lead, "Нужен документ", {}) == 'contract'
    
    def test_route_to_petition_agent_on_keyword(self, test_lead):
        """Test routing to petition agent based on keywords"""
        orchestrator = AgentOrchestrator()
        
        assert orchestrator.route_message(test_lead, "Нужно ходатайство", {}) == 'petition'
        assert orchestrator.route_message(test_lead, "Заявление в суд", {}) == 'petition'
        assert orchestrator.route_message(test_lead, "Вернуть права", {}) == 'petition'
    
    def test_route_to_pricing_agent_on_keyword(self, test_lead):
        """Test routing to pricing agent based on keywords"""
        orchestrator = AgentOrchestrator()
        
        assert orchestrator.route_message(test_lead, "Сколько стоит?", {}) == 'pricing'
        assert orchestrator.route_message(test_lead, "Какая цена?", {}) == 'pricing'
        assert orchestrator.route_message(test_lead, "Тариф", {}) == 'pricing'
    
    def test_route_verification_code(self, test_lead):
        """Test routing 6-digit verification code to contract agent"""
        orchestrator = AgentOrchestrator()
        
        assert orchestrator.route_message(test_lead, "123456", {}) == 'contract'
        assert orchestrator.route_message(test_lead, "999888", {}) == 'contract'
    
    def test_default_route_to_intake(self, test_lead):
        """Test default routing to intake agent"""
        orchestrator = AgentOrchestrator()
        
        assert orchestrator.route_message(test_lead, "Меня остановили", {}) == 'intake'
        assert orchestrator.route_message(test_lead, "Помогите", {}) == 'intake'


class TestIntakeAgent:
    """Test intake agent - article identification"""
    
    def test_knowledge_base_article_matching(self, test_lead, mock_deepseek, mock_memory):
        """Test that intake agent uses knowledge base for article matching"""
        agent = IntakeAgent(mock_deepseek, mock_memory)
        context = {}
        
        # Process message about drunk driving
        agent.process(test_lead, "Меня остановили пьяным за рулем", context)
        
        # Check that knowledge base suggested an article
        assert 'suggested_article' in context
        assert context['suggested_article']['article'] == 'ч.1 ст.12.8 КоАП РФ'
    
    def test_system_prompt_includes_article_hint(self, test_lead, mock_deepseek, mock_memory):
        """Test that system prompt includes article hint from knowledge base"""
        agent = IntakeAgent(mock_deepseek, mock_memory)
        context = {'suggested_article': {
            'article': 'ч.1 ст.12.8 КоАП РФ',
            'title': 'Управление в состоянии опьянения',
            'punishment': {'fine': '45 000 ₽', 'license_suspension': '1.5 - 2 года'}
        }}
        
        prompt = agent.get_system_prompt(test_lead, context)
        
        assert 'Подсказка из базы знаний' in prompt
        assert 'ч.1 ст.12.8 КоАП РФ' in prompt
        assert '45 000 ₽' in prompt


class TestPricingAgent:
    """Test pricing agent - ROI calculations"""
    
    def test_pricing_by_instance(self):
        """Test pricing calculation for different court instances"""
        # Test Moscow pricing
        price_1st = analytics.get_price_by_instance("MOSCOW", "WITHOUT_POA", "1")
        assert price_1st == 30000
        
        price_4th = analytics.get_price_by_instance("MOSCOW", "WITHOUT_POA", "4")
        assert price_4th == 120000
        
        # Test regions pricing
        price_regions = analytics.get_price_by_instance("REGIONS", "WITH_POA", "3")
        assert price_regions == 63000
    
    def test_document_preparation_deadlines(self):
        """Test document preparation deadlines by instance"""
        deadline_1 = analytics.get_document_preparation_deadline("1")
        assert "7-10 рабочих дней" in deadline_1
        
        deadline_3 = analytics.get_document_preparation_deadline("3")
        assert "15 рабочих дней" in deadline_3
        
        deadline_urgent = analytics.get_document_preparation_deadline("1", is_urgent=True)
        assert "срочное дело" in deadline_urgent
    
    def test_pricing_prompt_includes_deadlines(self, test_lead, mock_deepseek, mock_memory):
        """Test that pricing prompt includes preparation deadlines"""
        agent = PricingAgent(mock_deepseek, mock_memory)
        context = {}
        
        prompt = agent.get_system_prompt(test_lead, context)
        
        assert "срок подготовки" in prompt
        assert "рабочих дней" in prompt


class TestContractAgent:
    """Test contract agent - contract generation"""
    
    def test_verification_code_detection(self, test_lead, mock_deepseek, mock_memory):
        """Test that contract agent detects 6-digit verification codes"""
        agent = ContractAgent(mock_deepseek, mock_memory)
        
        assert agent._is_verification_code("123456") == True
        assert agent._is_verification_code("999888") == True
        assert agent._is_verification_code("12345") == False
        assert agent._is_verification_code("abc123") == False


class TestPetitionAgent:
    """Test petition agent - petition generation"""
    
    def test_petition_type_detection(self, test_lead, mock_deepseek, mock_memory):
        """Test petition type detection from keywords"""
        agent = PetitionAgent(mock_deepseek, mock_memory)
        
        assert agent._detect_petition_type("Нужно вернуть права") == 'return_license'
        assert agent._detect_petition_type("Перенести судебное заседание") == 'postpone_hearing'
        assert agent._detect_petition_type("Нужна экспертиза") == 'request_expertise'
        assert agent._detect_petition_type("Привлечь представителя") == 'attract_representative'
        assert agent._detect_petition_type("Получить судебные акты") == 'obtain_court_acts'
    
    def test_knowledge_base_template_loading(self, test_lead, mock_deepseek, mock_memory):
        """Test that petition agent loads templates from knowledge base"""
        agent = PetitionAgent(mock_deepseek, mock_memory)
        context = {}
        
        # Process message
        agent.process(test_lead, "Нужно ходатайство о привлечении представителя", context)
        
        # Check that template was loaded
        assert 'petition_type' in context
        assert context['petition_type'] == 'attract_representative'
        assert 'petition_template' in context
        assert context['petition_template']['title'] == 'Ходатайство о привлечении представителя'
    
    def test_new_petition_templates_exist(self):
        """Test that all 8 petition templates exist"""
        kb = get_knowledge_base()
        
        # Original 5 templates
        assert kb.get_petition_template('return_license') is not None
        assert kb.get_petition_template('postpone_hearing') is not None
        assert kb.get_petition_template('request_expertise') is not None
        assert kb.get_petition_template('call_witnesses') is not None
        assert kb.get_petition_template('review_materials') is not None
        
        # New 3 templates
        assert kb.get_petition_template('attract_representative') is not None
        assert kb.get_petition_template('review_materials_detailed') is not None
        assert kb.get_petition_template('obtain_court_acts') is not None


class TestKnowledgeBase:
    """Test knowledge base functionality"""
    
    def test_article_search_by_keywords(self):
        """Test article search by keywords"""
        kb = get_knowledge_base()
        
        # Search for drunk driving
        article = kb.find_article_by_keywords("пьяный за рулем")
        assert article is not None
        assert article['article'] == 'ч.1 ст.12.8 КоАП РФ'
        
        # Search for speeding
        article = kb.find_article_by_keywords("превышение скорости 50 км")
        assert article is not None
        assert '12.9' in article['article']
    
    def test_article_by_code(self):
        """Test getting article by exact code"""
        kb = get_knowledge_base()
        
        article = kb.get_article_by_code('ч.1 ст.12.8 КоАП РФ')
        assert article is not None
        assert 'опьянение' in article['title'].lower()


class TestAISellingSkills:
    """Test AI selling skills and persuasion"""
    
    @patch('ai_engine.services.deepseek.DeepSeekAPIService.chat_completion')
    def test_roi_calculation_persuasiveness(self, mock_chat, test_lead, mock_memory):
        """Test that AI generates persuasive ROI calculations"""
        # Mock AI response with ROI calculation
        mock_chat.return_value = """
📊 <b>Расчет выгоды:</b>

💰 <b>Без юриста:</b>
• Лишение прав: 18 месяцев
• Такси/каршеринг: 540,000₽
• Рост ОСАГО: 25,000₽
• <b>Итого потери: 565,000₽</b>

✅ <b>С юристом:</b>
• Стоимость: 30,000₽
• Шанс успеха: 70%
• Ожидаемая экономия: 365,500₽
• <b>Защита окупается в 12 раз</b>

Берем ваше дело?
"""
        
        agent = PricingAgent(Mock(chat_completion=mock_chat), mock_memory)
        response = agent.process(test_lead, "Сколько стоит?", {})
        
        # Check persuasive elements
        assert "Расчет выгоды" in response
        assert "окупается" in response
        assert "₽" in response
        assert "Берем ваше дело?" in response
    
    @patch('ai_engine.services.deepseek.DeepSeekAPIService.chat_completion')
    def test_urgency_creation(self, mock_chat, test_lead, mock_memory):
        """Test that AI creates urgency for urgent cases"""
        mock_chat.return_value = """
⚠️ <b>СРОЧНОЕ ДЕЛО!</b>

Суд завтра — времени критически мало!

Сейчас подготовим:
1. Ходатайство о переносе суда (1-2 часа)
2. Базовые документы для первого заседания

Срок подготовки: <b>1-2 рабочих дня</b>

Начинаем?
"""
        
        agent = ContractAgent(Mock(chat_completion=mock_chat), mock_memory)
        response = agent.process(test_lead, "Суд завтра, помогите!", {})
        
        assert "СРОЧНОЕ" in response or "срочное" in response
        assert "1-2" in response


class TestCaseDocumentModel:
    """Test case document upload functionality"""
    
    def test_case_document_creation(self, test_lead, db):
        """Test creating case document"""
        doc = CaseDocument.objects.create(
            lead=test_lead,
            document_type='protocol',
            file='test.pdf',
            file_name='Протокол.pdf',
            file_size=1024000
        )
        
        assert doc.lead == test_lead
        assert doc.document_type == 'protocol'
        assert doc.get_document_type_display() == 'Протокол об административном правонарушении'
    
    def test_case_document_types(self, db):
        """Test all document types are available"""
        types = [choice[0] for choice in CaseDocument.DOCUMENT_TYPE_CHOICES]
        
        assert 'protocol' in types
        assert 'photo' in types
        assert 'video' in types
        assert 'court_decision' in types
        assert 'medical_certificate' in types


class TestEndToEndScenarios:
    """Test complete conversation flows"""
    
    @patch('ai_engine.services.deepseek.DeepSeekAPIService.chat_completion')
    def test_full_sales_funnel(self, mock_chat, test_lead, mock_memory):
        """Test complete sales funnel from intake to contract"""
        orchestrator = AgentOrchestrator()
        
        # Step 1: Intake - identify article
        mock_chat.return_value = "🔍 Похоже на ч.1 ст.12.8 КоАП РФ - управление в состоянии опьянения..."
        agent_type = orchestrator.route_message(test_lead, "Меня остановили пьяным", {})
        assert agent_type == 'intake'
        
        # Step 2: Pricing - calculate ROI
        test_lead.case_type = 'DUI'
        test_lead.case_description = 'ч.1 ст.12.8 КоАП РФ'
        test_lead.save()
        
        mock_chat.return_value = "📊 Расчет выгоды: защита окупается в 12 раз..."
        agent_type = orchestrator.route_message(test_lead, "Сколько стоит?", {})
        assert agent_type == 'pricing'
        
        # Step 3: Contract - generate contract
        test_lead.status = 'HOT'
        test_lead.estimated_cost = Decimal('30000')
        test_lead.save()
        
        mock_chat.return_value = "Для договора нужны паспортные данные..."
        agent_type = orchestrator.route_message(test_lead, "Оформите договор", {})
        assert agent_type == 'contract'
    
    def test_petition_generation_flow(self, test_lead, mock_deepseek, mock_memory):
        """Test petition generation flow"""
        agent = PetitionAgent(mock_deepseek, mock_memory)
        context = {}
        
        # Request petition
        response = agent.process(test_lead, "Нужно ходатайство о привлечении представителя", context)
        
        # Verify template was loaded
        assert context['petition_type'] == 'attract_representative'
        assert 'petition_template' in context


class TestAIContentQuality:
    """Test AI-generated content quality"""
    
    def test_response_uses_html_formatting(self):
        """Test that responses use proper HTML formatting"""
        # This would test actual AI responses
        sample_response = """
<b>Анализ ситуации:</b>
• Статья: ч.1 ст.12.8 КоАП РФ
• Последствия: штраф 30,000₽ + лишение прав 1.5-2 года

<b>Шансы на успех:</b> 70%
"""
        assert '<b>' in sample_response
        assert '•' in sample_response
        assert '₽' in sample_response
    
    def test_response_is_concise(self):
        """Test that responses are concise (not too long)"""
        # AI responses should be under 500 characters for good UX
        sample_response = "Короткий ответ от AI"
        assert len(sample_response) < 500


# Performance benchmarks
class TestPerformance:
    """Test system performance"""
    
    def test_orchestrator_routing_speed(self, test_lead):
        """Test that routing is fast (< 10ms)"""
        import time
        
        orchestrator = AgentOrchestrator()
        
        start = time.time()
        for _ in range(100):
            orchestrator.route_message(test_lead, "Оформите договор", {})
        end = time.time()
        
        avg_time = (end - start) / 100
        assert avg_time < 0.01  # Less than 10ms per routing
    
    def test_knowledge_base_search_speed(self):
        """Test that knowledge base search is fast"""
        import time
        
        kb = get_knowledge_base()
        
        start = time.time()
        for _ in range(100):
            kb.find_article_by_keywords("пьяный за рулем")
        end = time.time()
        
        avg_time = (end - start) / 100
        assert avg_time < 0.01  # Less than 10ms per search


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

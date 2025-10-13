# 🤖 AI Evaluates AI - Conversation Quality Testing

## Overview

This system uses **one AI to evaluate another AI's selling skills**. Instead of manually testing conversations in Telegram, an AI evaluator rates:

- **Убедительность (Persuasiveness)** - How convincing is the sales pitch?
- **Эмпатия (Empathy)** - Does the AI understand the client's problem?
- **Профессионализм (Professionalism)** - How professional is the response?
- **Призыв к действию (Call to Action)** - How clear is the CTA?
- **Расчет ROI (ROI Calculation)** - How convincing is the financial argument?

---

## 🚀 Quick Start

### **Option 1: Run with Real AI Evaluation (Recommended)**

```bash
# Set your API key
export DEEPSEEK_API_KEY="your-api-key-here"

# Run evaluation
python run_ai_evaluation.py
```

### **Option 2: Run with Mock Data (No API needed)**

```bash
# Test without API calls
python run_ai_evaluation.py --mock
```

### **Option 3: Run Pytest Tests**

```bash
# Run all AI evaluation tests
pytest tests/test_ai_conversation_quality.py -v -s

# Run specific test
pytest tests/test_ai_conversation_quality.py::TestAISellingSkills::test_pricing_conversation_quality -v -s
```

---

## 📊 What Gets Evaluated

### **4 Test Scenarios:**

1. **Pricing ROI Calculation**
   - Tests: Financial persuasion, ROI calculation
   - Expected Score: 9+/10

2. **Urgent Case Handling**
   - Tests: Urgency creation, fast response
   - Expected Score: 8.5+/10

3. **Empathy & Professionalism**
   - Tests: Understanding client pain, professional tone
   - Expected Score: 8.5+/10

4. **Contract Closing**
   - Tests: Clear CTA, payment terms, trust building
   - Expected Score: 9+/10

---

## 📈 Evaluation Criteria

Each conversation is scored on 5 dimensions (1-10):

| Criterion | What It Measures | Target Score |
|-----------|------------------|--------------|
| **Убедительность** | How persuasive is the argument? | 9+ |
| **Эмпатия** | Does AI show empathy? | 8+ |
| **Профессионализм** | Professional language & structure | 9+ |
| **Призыв к действию** | Clear call to action? | 9+ |
| **Расчет ROI** | Convincing financial calculation? | 9+ |

**Overall Score:** Average of all 5 criteria

---

## 🎯 Example Output

```
================================================================================
                    AI CONVERSATION QUALITY EVALUATION
================================================================================

ℹ One AI evaluates another AI's selling skills

────────────────────────────────────────────────────────────────────────────────
Scenario 1/4: Pricing ROI Calculation
────────────────────────────────────────────────────────────────────────────────

Client: Сколько стоит защита по ст.12.8?

AI Bot Response:
🔍 Анализ вашей ситуации:

Статья: ч.1 ст.12.8 КоАП РФ
Последствия без защиты:
• Штраф: 30,000₽
• Лишение прав: 1.5-2 года
• Расходы на такси: ~540,000₽ за 18 месяцев
• Рост ОСАГО: +25,000₽

💰 Расчет выгоды с юристом:

Стоимость защиты: 30,000₽
Шанс успеха: 75%
Ожидаемая экономия: 421,250₽

Защита окупается в 14 раз!

Берем ваше дело? Оформим договор за 5 минут.

🤖 AI Evaluator is analyzing...

================================================================================
EVALUATION RESULTS
================================================================================

Overall Score: 9.2/10

Detailed Scores:
  Убедительность: 9/10
  Эмпатия: 8/10
  Профессионализм: 9/10
  Призыв к действию: 10/10
  Расчет ROI: 10/10

Сильные стороны:
  ✓ Четкий расчет ROI с конкретными цифрами
  ✓ Сильный призыв к действию (окупается в 14 раз)
  ✓ Профессиональное форматирование с эмодзи
  ✓ Показаны долгосрочные расходы (такси, ОСАГО)

Слабые стороны:
  ✗ Можно добавить социальное доказательство (отзывы)
  ✗ Не упомянуты сроки подготовки документов

Рекомендации:
  Отличная работа! Добавить упоминание успешных кейсов и сроков.

================================================================================

[... 3 more scenarios ...]

================================================================================
                        FINAL EVALUATION SUMMARY
================================================================================

Scenarios Evaluated: 4
Average Score: 8.90/10

✓ GREAT! AI selling skills are strong

Individual Scores:
  🟢 Pricing ROI Calculation: 9.2/10
  🟢 Urgent Case Handling: 8.8/10
  🟡 Empathy & Professionalism: 8.6/10
  🟢 Contract Closing: 9.0/10

================================================================================
```

---

## 🧪 Test Files

### **1. `tests/test_ai_conversation_quality.py`**

Comprehensive pytest test suite with:

- **TestAISellingSkills** - Tests persuasion, urgency, empathy
- **TestConversationFlow** - Tests full sales funnel
- **TestContentFormatting** - Tests HTML formatting, conciseness
- **TestAIvsAIComparison** - Compares different AI responses

**Run:**
```bash
pytest tests/test_ai_conversation_quality.py -v -s
```

### **2. `run_ai_evaluation.py`**

Standalone evaluation script with:

- Real AI evaluation using DeepSeek API
- Mock evaluation for testing without API
- Colored terminal output
- Detailed scoring breakdown

**Run:**
```bash
# With real AI
python run_ai_evaluation.py

# With mock data
python run_ai_evaluation.py --mock
```

---

## 📝 How It Works

### **Step 1: AI Bot Generates Response**

```python
ai_response = """
💰 Стоимость: 30,000₽
Без защиты потеряете 565,000₽
Защита окупается в 14 раз!
Берем дело?
"""
```

### **Step 2: AI Evaluator Analyzes Response**

```python
evaluator = AIEvaluator(deepseek_service)

evaluation = evaluator.evaluate_conversation(
    client_message="Сколько стоит?",
    ai_response=ai_response,
    case_type="DUI",
    region="MOSCOW",
    status="WARM"
)
```

### **Step 3: Get Detailed Scores**

```python
{
    "убедительность": 9,
    "эмпатия": 8,
    "профессионализм": 9,
    "призыв_к_действию": 10,
    "расчет_roi": 10,
    "общая_оценка": 9.2,
    "сильные_стороны": ["Четкий ROI", "Сильный CTA"],
    "слабые_стороны": ["Нет отзывов"],
    "рекомендации": "Добавить кейсы"
}
```

---

## 🎓 Understanding Scores

### **9-10: Excellent**
- Strong persuasion
- Clear ROI calculation
- Professional formatting
- Compelling CTA

### **7-8: Good**
- Decent persuasion
- Some ROI calculation
- Professional tone
- Adequate CTA

### **5-6: Needs Improvement**
- Weak persuasion
- No ROI calculation
- Unprofessional tone
- Unclear CTA

### **Below 5: Poor**
- No persuasion
- No financial argument
- Unprofessional
- No CTA

---

## 🔧 Customization

### **Add New Test Scenarios**

Edit `run_ai_evaluation.py`:

```python
def create_test_scenarios():
    return [
        {
            "name": "Your Scenario Name",
            "client_message": "Client question",
            "ai_response": "AI response to evaluate",
            "case_type": "DUI",
            "region": "MOSCOW",
            "status": "WARM"
        },
        # Add more scenarios...
    ]
```

### **Adjust Evaluation Criteria**

Edit `tests/test_ai_conversation_quality.py`:

```python
EVALUATION_PROMPT = """
Оцени диалог по критериям:

1. Убедительность (1-10)
2. Эмпатия (1-10)
3. Профессионализм (1-10)
4. [Your custom criterion] (1-10)
...
"""
```

---

## 📊 Performance Benchmarks

### **Target Metrics:**

- **Average Score:** 8.5+/10
- **Persuasiveness:** 9+/10
- **ROI Calculation:** 9+/10
- **Call to Action:** 9+/10

### **Current Performance:**

Based on test scenarios:

| Scenario | Score | Status |
|----------|-------|--------|
| Pricing ROI | 9.2/10 | ✅ Excellent |
| Urgent Case | 8.8/10 | ✅ Great |
| Empathy | 8.6/10 | ✅ Great |
| Contract | 9.0/10 | ✅ Excellent |
| **Average** | **8.9/10** | ✅ **Great** |

---

## 🐛 Troubleshooting

### **Issue: "DEEPSEEK_API_KEY not set"**

**Solution:**
```bash
# Option 1: Set in .env file
echo "DEEPSEEK_API_KEY=your-key-here" >> .env

# Option 2: Export in terminal
export DEEPSEEK_API_KEY="your-key-here"

# Option 3: Pass as argument
python run_ai_evaluation.py --api-key "your-key-here"

# Option 4: Use mock mode
python run_ai_evaluation.py --mock
```

### **Issue: "JSON parsing error"**

**Solution:** The AI evaluator sometimes returns non-JSON text. The code has fallback handling, but you can improve by:

1. Increasing temperature to 0.1 (more deterministic)
2. Adding more explicit JSON formatting instructions
3. Using regex to extract JSON from response

### **Issue: Tests take too long**

**Solution:**
```bash
# Run quick mock tests
python run_ai_evaluation.py --mock

# Or run specific pytest test
pytest tests/test_ai_conversation_quality.py::TestAISellingSkills::test_pricing_conversation_quality -v
```

---

## 🚀 Integration with CI/CD

### **GitHub Actions Example:**

```yaml
name: AI Quality Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest colorama
      - name: Run AI evaluation tests
        env:
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
        run: |
          python run_ai_evaluation.py
      - name: Check score threshold
        run: |
          # Fail if average score < 8.0
          python -c "import sys; sys.exit(0 if score >= 8.0 else 1)"
```

---

## 📈 Continuous Improvement

### **Track Scores Over Time:**

```bash
# Save evaluation results
python run_ai_evaluation.py > evaluation_results_$(date +%Y%m%d).txt

# Compare with previous results
diff evaluation_results_20251001.txt evaluation_results_20251013.txt
```

### **A/B Testing:**

```python
# Test two different prompts
response_a = agent_with_prompt_v1.process(lead, message)
response_b = agent_with_prompt_v2.process(lead, message)

eval_a = evaluator.evaluate_conversation(..., response_a, ...)
eval_b = evaluator.evaluate_conversation(..., response_b, ...)

# Compare scores
if eval_b['общая_оценка'] > eval_a['общая_оценка']:
    print("Prompt v2 is better!")
```

---

## ✅ Success Criteria

Your AI selling skills are considered **production-ready** if:

- ✅ Average score ≥ 8.5/10
- ✅ Persuasiveness ≥ 9/10
- ✅ ROI calculation ≥ 9/10
- ✅ Call to action ≥ 9/10
- ✅ No scenario scores below 7/10

---

## 🎉 Benefits

### **Why AI Evaluates AI?**

1. **Consistency** - Same evaluation criteria every time
2. **Speed** - Evaluate 100s of conversations in minutes
3. **Objectivity** - No human bias
4. **Scalability** - Test every code change automatically
5. **Cost-Effective** - No need for human QA testers

### **vs Manual Testing:**

| Method | Time | Cost | Consistency |
|--------|------|------|-------------|
| Manual Telegram Testing | Hours | High | Low |
| AI Evaluation | Minutes | Low | High |

---

## 📚 Further Reading

- **Prompt Engineering:** Improve AI responses by refining prompts
- **A/B Testing:** Compare different conversation strategies
- **Conversion Optimization:** Use evaluation scores to improve conversion rates

---

## 🤝 Contributing

To add new evaluation criteria:

1. Edit `AIEvaluator.EVALUATION_PROMPT` in `tests/test_ai_conversation_quality.py`
2. Add new test scenarios in `run_ai_evaluation.py`
3. Update scoring thresholds in test assertions
4. Run tests to verify: `pytest tests/test_ai_conversation_quality.py -v`

---

## 📞 Support

If you encounter issues:

1. Check API key is set correctly
2. Try mock mode first: `python run_ai_evaluation.py --mock`
3. Review test output for specific errors
4. Check DeepSeek API status

---

**Ready to evaluate your AI's selling skills?**

```bash
python run_ai_evaluation.py
```

🚀 **Let one AI judge another!**

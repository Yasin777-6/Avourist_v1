# ✅ COMPLETE TEST CHECKLIST

## 🎯 Pre-Deployment Testing

Use this checklist to verify everything before deploying to production.

---

## 📋 Phase 1: Automated Tests (5 minutes)

### ✅ Test 1: Quick Verification
```bash
python verify_implementation.py
```

**Expected:**
- [ ] ✓ Pricing by Instance: PASS
- [ ] ✓ Document Deadlines: PASS
- [ ] ✓ Petition Templates: PASS
- [ ] ✓ CaseDocument Model: PASS
- [ ] ✓ Contract Price Auto-Fill: PASS
- [ ] ✓ Results: 5/5 tests passed

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

### ✅ Test 2: AI Evaluation (Mock)
```bash
python run_ai_evaluation.py --mock
```

**Expected:**
- [ ] Scenario 1 (Pricing ROI): 9.2/10
- [ ] Scenario 2 (Urgent Case): 8.8/10
- [ ] Scenario 3 (Empathy): 8.6/10
- [ ] Scenario 4 (Contract): 9.0/10
- [ ] Average Score: 8.9/10
- [ ] ✓ Mock evaluation complete!

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

### ✅ Test 3: Unit Tests
```bash
pytest tests/test_ai_agents.py -v
```

**Expected:**
- [ ] TestAgentOrchestrator: All tests pass
- [ ] TestIntakeAgent: All tests pass
- [ ] TestPricingAgent: All tests pass
- [ ] TestContractAgent: All tests pass
- [ ] TestPetitionAgent: All tests pass
- [ ] TestKnowledgeBase: All tests pass
- [ ] TestPerformance: All tests pass

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

## 📋 Phase 2: Local Bot Testing (10 minutes)

### ✅ Test 4: Start Bot Locally
```bash
python run_bot_local.py
```

**Expected:**
- [ ] Bot starts without errors
- [ ] Logs show: "Starting bot in polling mode..."
- [ ] No database connection errors
- [ ] No import errors

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

### ✅ Test 5: Telegram Integration Tests

Send these messages to your bot and verify responses:

#### **Test 5.1: Intake Agent - Article Identification**
**Send:** `Меня остановили пьяным за рулем`

**Expected Response Should Include:**
- [ ] Identifies ч.1 ст.12.8 КоАП РФ
- [ ] Mentions штраф 30,000₽
- [ ] Mentions лишение прав 1.5-2 года
- [ ] Shows win probability (70-75%)
- [ ] Asks for more details

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

#### **Test 5.2: Pricing Agent - ROI Calculation**
**Send:** `Сколько стоит защита?`

**Expected Response Should Include:**
- [ ] Shows pricing by instance (1-4)
- [ ] 1st instance: 30,000₽ (Moscow) or 15,000₽ (Regions)
- [ ] Shows document preparation deadlines
- [ ] ROI calculation (окупается в X раз)
- [ ] Mentions taxi costs (540,000₽)
- [ ] Clear call to action

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

#### **Test 5.3: Pricing by Instance - Cassation**
**Send:** `Сколько стоит защита в кассации?`

**Expected Response Should Include:**
- [ ] 3rd instance pricing: 90,000₽ (Moscow) or 53,000₽ (Regions)
- [ ] Deadline: 15 рабочих дней
- [ ] Explains cassation specifics
- [ ] Shows higher complexity

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

#### **Test 5.4: Contract Agent - Contract Generation**
**Send:** `Оформите договор`

**Expected Response Should Include:**
- [ ] Asks for passport data (ФИО, серия/номер)
- [ ] Mentions payment terms (50% prepayment)
- [ ] Price should match lead.estimated_cost
- [ ] Professional tone
- [ ] Clear next steps

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

#### **Test 5.5: Petition Agent - New Template 1**
**Send:** `Нужно ходатайство о привлечении представителя`

**Expected Response Should Include:**
- [ ] Generates petition template
- [ ] Includes КоАП РФ ст.25.5 reference
- [ ] Includes Пленум ВС РФ reference
- [ ] Asks for case details (court name, case number)
- [ ] Professional legal language

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

#### **Test 5.6: Petition Agent - New Template 2**
**Send:** `Нужно получить судебные акты`

**Expected Response Should Include:**
- [ ] Generates court acts request template
- [ ] Mentions certified copies (В ДВУХ ЭКЗЕМПЛЯРАХ)
- [ ] Includes legal references
- [ ] Asks for decision dates

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

#### **Test 5.7: Petition Agent - New Template 3**
**Send:** `Хочу ознакомиться с материалами дела подробно`

**Expected Response Should Include:**
- [ ] Generates detailed review petition
- [ ] Mentions photo/video access
- [ ] Includes КоАП РФ ст.25.1 reference
- [ ] Professional legal format

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

#### **Test 5.8: Urgent Case Handling**
**Send:** `Суд завтра! Помогите срочно!`

**Expected Response Should Include:**
- [ ] Creates urgency (⚠️ СРОЧНОЕ ДЕЛО)
- [ ] Shows 1-2 working days deadline
- [ ] Suggests postponement petition
- [ ] Higher price for urgency (+5,000₽)
- [ ] Strong call to action

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

#### **Test 5.9: Photo Upload (OCR)**
**Send:** Photo of protocol/document

**Expected Response Should Include:**
- [ ] Recognizes text from image
- [ ] Shows extracted text
- [ ] Asks for clarification
- [ ] Continues conversation naturally

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

#### **Test 5.10: Multi-Turn Conversation**
**Send sequence:**
1. `Меня остановили`
2. `Пьяный за рулем`
3. `Сколько стоит?`
4. `Давайте оформим договор`

**Expected:**
- [ ] Maintains context across messages
- [ ] Remembers previous information
- [ ] Smooth conversation flow
- [ ] No repeated questions

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

## 📋 Phase 3: Performance Tests (5 minutes)

### ✅ Test 6: Response Time
```bash
# Send 10 messages and measure response time
```

**Expected:**
- [ ] Average response time < 2 seconds
- [ ] No timeouts
- [ ] Consistent performance

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

### ✅ Test 7: Routing Performance
```bash
pytest tests/test_ai_agents.py::TestPerformance -v
```

**Expected:**
- [ ] Routing speed < 10ms
- [ ] Knowledge base search < 10ms
- [ ] All performance benchmarks pass

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

## 📋 Phase 4: Edge Cases (5 minutes)

### ✅ Test 8: Edge Cases

#### **Test 8.1: Empty Message**
**Send:** ` ` (space)

**Expected:**
- [ ] Handles gracefully
- [ ] Asks for clarification
- [ ] No errors

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

#### **Test 8.2: Very Long Message**
**Send:** 500+ character message

**Expected:**
- [ ] Processes without error
- [ ] Response is coherent
- [ ] No truncation issues

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

#### **Test 8.3: Special Characters**
**Send:** `Штраф 30,000₽ по ст.12.8 КоАП РФ`

**Expected:**
- [ ] Handles special characters (₽, №)
- [ ] Recognizes article reference
- [ ] No encoding errors

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

#### **Test 8.4: Multiple Requests Simultaneously**
**Send:** 5 messages rapidly

**Expected:**
- [ ] All messages processed
- [ ] Correct order maintained
- [ ] No race conditions

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

## 📋 Phase 5: Database Tests (2 minutes)

### ✅ Test 9: Data Persistence

**Check:**
- [ ] Leads are created correctly
- [ ] Conversations are saved
- [ ] estimated_cost is populated
- [ ] case_type is identified
- [ ] region is detected

**Command:**
```bash
python manage.py shell
>>> from leads.models import Lead
>>> Lead.objects.all().count()  # Should show test leads
>>> Lead.objects.last()  # Check latest lead data
```

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

## 📋 Phase 6: AI Quality Tests (Optional, 60 seconds)

### ✅ Test 10: Real AI Evaluation
```bash
python run_ai_evaluation.py
```

**Expected:**
- [ ] Scenario 1: 9+/10
- [ ] Scenario 2: 8.5+/10
- [ ] Scenario 3: 8.5+/10
- [ ] Scenario 4: 9+/10
- [ ] Average: 8.5+/10

**Status:** ⬜ Not Run | ✅ Passed | ❌ Failed

---

## 📊 Final Checklist Summary

### **Automated Tests (Must Pass)**
- [ ] ✅ Quick Verification (5/5)
- [ ] ✅ AI Evaluation Mock (8.9/10)
- [ ] ✅ Unit Tests (All pass)

### **Bot Tests (Must Pass)**
- [ ] ✅ Bot starts successfully
- [ ] ✅ Intake agent works
- [ ] ✅ Pricing agent works
- [ ] ✅ Contract agent works
- [ ] ✅ Petition agent works (all 3 new templates)
- [ ] ✅ Urgent case handling works
- [ ] ✅ OCR works
- [ ] ✅ Multi-turn conversation works

### **Performance Tests (Must Pass)**
- [ ] ✅ Response time < 2s
- [ ] ✅ Routing < 10ms
- [ ] ✅ No timeouts

### **Edge Cases (Should Pass)**
- [ ] ✅ Empty messages handled
- [ ] ✅ Long messages handled
- [ ] ✅ Special characters handled
- [ ] ✅ Multiple requests handled

### **Data Tests (Must Pass)**
- [ ] ✅ Leads created correctly
- [ ] ✅ Conversations saved
- [ ] ✅ Data persists

---

## 🎯 Deployment Readiness

**Minimum Requirements:**
- ✅ All automated tests pass (Phase 1)
- ✅ Bot starts and responds (Phase 2, Tests 4-5.4)
- ✅ At least 2 new petition templates work (Phase 2, Tests 5.5-5.7)
- ✅ Performance acceptable (Phase 3)

**Recommended:**
- ✅ All Telegram tests pass (Phase 2)
- ✅ All edge cases handled (Phase 4)
- ✅ Data persistence verified (Phase 5)

---

## 📝 Test Results

**Date:** _____________

**Tester:** _____________

**Overall Status:** ⬜ Not Ready | ⬜ Ready with Issues | ✅ Ready for Production

**Notes:**
```
[Add any issues or observations here]
```

---

## 🚀 Quick Test Commands

```bash
# Run all automated tests (5 minutes)
python verify_implementation.py && \
python run_ai_evaluation.py --mock && \
pytest tests/test_ai_agents.py -v

# Start bot for manual testing
python run_bot_local.py

# Check database
python manage.py shell
>>> from leads.models import Lead
>>> Lead.objects.all()
```

---

## ✅ Sign-Off

- [ ] All critical tests passed
- [ ] Bot responds correctly in Telegram
- [ ] Performance is acceptable
- [ ] No critical bugs found
- [ ] Ready for production deployment

**Approved by:** _____________

**Date:** _____________

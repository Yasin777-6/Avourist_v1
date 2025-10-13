# 🐛 BUGFIX: Bot Asks for Contract Too Early

## 🔴 Bug Report

**Issue:** Bot immediately asks for contract data on first message, skipping the trust-building flow.

**Example:**
```
User: "Я сбил пешехода"
Bot: "Для оформления договора мне нужны паспортные данные..." ❌ WRONG!
```

**Expected:**
```
User: "Я сбил пешехода"
Bot: "Расскажите подробнее о ситуации..." ✅ CORRECT!
```

**Root Cause:** Orchestrator routes to Contract Agent if `lead.status == 'HOT'`, but lead becomes HOT too early (after first message).

**Log Evidence:**
```
[INFO] Lead is HOT with pricing - routing to contract
[INFO] ContractAgent processing message
```

---

## ✅ Fix Applied

### **Removed Premature Contract Routing:**

**Before (Lines 89-92):**
```python
# If lead has pricing and is HOT, suggest contract
if lead.status == 'HOT' and lead.estimated_cost:
    logger.info("Lead is HOT with pricing - routing to contract")
    return 'contract'
```

**After:**
```python
# Only route to contract if client EXPLICITLY wants contract
# Don't route just because lead is HOT - that's too early!
# Client must first see value (analysis, petition, pricing)
```

---

## 📊 Correct Flow Now

### **Trust-Building Flow:**

```
1. User: "Я сбил пешехода"
   → Route to: Intake Agent
   → Bot: "Расскажите подробнее..."

2. User: "Да" (confirms case)
   → Route to: Intake Agent
   → Bot: "Пришлите документы для анализа"

3. User: [Sends photo]
   → Route to: Intake Agent
   → Bot: [Free expert analysis + violations found]

4. User: "Что дальше?"
   → Route to: Pricing Agent
   → Bot: [ROI calculation + pricing]

5. User: "Давайте оформим"
   → Route to: Contract Agent
   → Bot: "Для договора нужны данные..."
```

---

## 🎯 When to Route to Contract Agent

**ONLY when client explicitly says:**
- "давайте оформим"
- "хочу договор"
- "оформите договор"
- "заключим договор"

**NOT when:**
- ❌ Lead status is HOT
- ❌ Lead has estimated_cost
- ❌ First message from client
- ❌ Client asks questions

---

## 📁 File Modified

- ✅ `ai_engine/agents/orchestrator.py` - Removed premature contract routing

---

## 🧪 Test Case

**Scenario: New client with DUI case**

```
1. User: "Меня остановили пьяным"
   Expected: Intake Agent (article identification) ✅
   
2. User: "Да"
   Expected: Intake Agent (document request) ✅
   
3. User: [Photo]
   Expected: Intake Agent (expert analysis) ✅
   
4. User: "Сколько стоит?"
   Expected: Pricing Agent (ROI + pricing) ✅
   
5. User: "Давайте оформим"
   Expected: Contract Agent (passport data request) ✅
```

**Before Fix:**
- Step 1 → Contract Agent ❌ (asks for passport immediately)

**After Fix:**
- Step 1 → Intake Agent ✅ (builds trust first)

---

## 🎯 Summary of All Bugs Fixed

### **Bug 1: Documents sent for all messages** ✅
- Only petitions sent as .docx

### **Bug 2: Wrong article in contract** ✅
- Use Lead's case_type

### **Bug 3: Contract contains petition text** ✅
- Ignore history fluff

### **Bug 4: Bot asks for contract too early** ✅
- Build trust first, contract last

---

**All bugs fixed! Bot now follows proper trust-building flow!** 🎉

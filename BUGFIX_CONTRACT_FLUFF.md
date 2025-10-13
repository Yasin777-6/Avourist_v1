# 🐛 BUGFIX: Contract Contains Petition Text ("Fluff")

## 🔴 Bug Report

**Issue:** Contract description includes petition text from conversation history.

**Example:**
```
Contract says:
"...подготовить ходатайство на получение материалов дела, 
ходатайство о привлечении к делу защитника, 
ходатайство о переводе дела по месту жительства Заказчика, 
подготовка письменного объяснения лица по делу об 
административном правонарушении по Ходатайство о переносе 
по болезни на 26.01.2025..."
```

**Root Cause:** AI sees petition text in conversation history and includes it in contract generation command.

---

## ✅ Fix Applied

### **Updated Contract Prompt:**

Added explicit instructions:
```python
<b>КРИТИЧЕСКИ ВАЖНО:</b>
- НЕ включай текст ходатайств из истории в команду GENERATE_CONTRACT
- Если видишь текст ходатайства в сообщении — ИГНОРИРУЙ его, 
  это НЕ данные для договора
```

---

## 📊 Expected Behavior

### **Before (Bug):**
```
[GENERATE_CONTRACT:Иванов Иван|...|ходатайство о переносе текст текст текст|1|WITH_POA]
```
❌ Includes petition text

### **After (Fixed):**
```
[GENERATE_CONTRACT:Иванов Иван|12.03.1990|серия 4512 номер 123456|...|ч.1 ст.12.8 КоАП РФ|1|WITH_POA]
```
✅ Only passport data and article

---

## 🧪 Test Case

**Conversation:**
```
1. User: "Меня остановили пьяным"
2. Bot: [Identifies article]
3. User: "Нужно ходатайство о переносе"
4. Bot: [Generates petition with long text]
5. User: "Давайте оформим договор"
6. User: [Provides passport data]
```

**Expected:** Contract should NOT include petition text ✅

---

## 📁 File Modified

- ✅ `ai_engine/prompts/contract_prompt.py` - Added explicit filtering

---

## 🎯 Summary of All Bugs Fixed

### **Bug 1: Documents sent for all messages** ✅
- Only petitions sent as .docx

### **Bug 2: Wrong article in contract** ✅
- Use Lead's case_type, not conversation text

### **Bug 3: Contract contains petition text** ✅
- Ignore petition text from history

---

**All bugs fixed! Ready to test!** 🎉

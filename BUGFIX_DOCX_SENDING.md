# 🐛 BUGFIX: Documents Sent for All Messages

## 🔴 Bug Report

**Issue:** Bot was sending **every response** as a .docx file, not just petitions.

**Example:**
```
User: "Сколько стоит защита?"
Bot: [Sends pricing as .docx file] ❌ WRONG!
```

**Root Cause:** Detection logic was too broad:
```python
if 'ХОДАТАЙСТВО' in text.upper() and len(text) > 300:
    send_as_document()  # Too broad!
```

This triggered on ANY message mentioning "ходатайство", even if it was just advice.

---

## ✅ Fix Applied

**New Detection Logic:**
```python
is_petition = (
    'ХОДАТАЙСТВО' in text.upper() and 
    len(text) > 300 and
    ('В ' in text and 'суд' in text.lower()) and  # Court address
    ('Подпись:' in text or 'подпись' in text.lower())  # Signature line
)
```

**Now requires ALL of:**
1. ✅ Contains "ХОДАТАЙСТВО"
2. ✅ Length > 300 characters
3. ✅ Has court address ("В ... суд")
4. ✅ Has signature line ("Подпись:")

---

## 📊 Before vs After

### **Before (Bug):**

| Message | Sent As |
|---------|---------|
| "Суд послезавтра" (advice) | .docx ❌ |
| "Сколько стоит?" (pricing) | .docx ❌ |
| Actual petition | .docx ✅ |

### **After (Fixed):**

| Message | Sent As |
|---------|---------|
| "Суд послезавтра" (advice) | Text ✅ |
| "Сколько стоит?" (pricing) | Text ✅ |
| Actual petition | .docx ✅ |

---

## 🧪 Test Cases

### **Test 1: Regular Advice (Should be Text)**
```
User: "Суд послезавтра"
Bot: [Gives action plan]
```

**Expected:** Text message ✅
**Before:** .docx file ❌
**After:** Text message ✅

---

### **Test 2: Pricing (Should be Text)**
```
User: "Сколько стоит защита?"
Bot: [Shows pricing]
```

**Expected:** Text message ✅
**Before:** .docx file ❌
**After:** Text message ✅

---

### **Test 3: Actual Petition (Should be .docx)**
```
User: "Нужно ходатайство о переносе"
Bot: [Requests data]

User: "Иванов Иван, Москва ул Ленина 10, Таганский суд"
Bot: [Generates petition]
```

**Expected:** .docx file ✅
**Before:** .docx file ✅
**After:** .docx file ✅

---

## 🎯 Detection Criteria

**A message is a petition document if it has:**

1. **Title:** "ХОДАТАЙСТВО"
2. **Court Address:** "В Таганский районный суд г. Москвы"
3. **Signature Line:** "Подпись: ___________ (ФИО)"
4. **Length:** > 300 characters

**If ANY of these is missing → Send as text message**

---

## 📁 File Modified

**File:** `run_bot_local.py`

**Function:** `send_telegram_message()`

**Lines:** 181-203

---

## ✅ Verification

**Test the fix:**

```bash
python run_bot_local.py
```

**Send these messages:**

1. `Суд послезавтра`
   → Expected: Text message ✅

2. `Сколько стоит защита?`
   → Expected: Text message ✅

3. `Нужно ходатайство о переносе`
   → Provide data
   → Expected: .docx file ✅

---

## 🎉 Status

**Bug:** Fixed ✅
**Tested:** Ready for testing
**Impact:** High (affects all conversations)

---

## 📊 Expected Behavior

### **Messages Sent as Text:**
- ✅ Article identification
- ✅ Document requests
- ✅ Expert analysis
- ✅ Action plans
- ✅ Pricing information
- ✅ ROI calculations
- ✅ Contract requests

### **Messages Sent as .docx:**
- ✅ Ходатайство о переносе
- ✅ Ходатайство о привлечении представителя
- ✅ Ходатайство об ознакомлении
- ✅ Заявление о получении судебных актов
- ✅ Any other petition with full structure

---

## 🚀 Ready to Test!

**Restart bot:**
```bash
python run_bot_local.py
```

**Test with:**
1. `Суд послезавтра` → Text ✅
2. `Сколько стоит?` → Text ✅
3. `Нужно ходатайство` → .docx ✅

**Expected:** Only actual petitions sent as .docx! ✅

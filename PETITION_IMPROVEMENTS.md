# 📝 PETITION GENERATION IMPROVEMENTS

## 🔴 Problems Fixed

### **Problem 1: Generic Petitions**
❌ Before: "[уточните название суда]", "[ваше ФИО]"
✅ After: Requests REAL data before generating

### **Problem 2: Sent as Text**
❌ Before: Sent inline with HTML tags
✅ After: Clean text format for easy copying

### **Problem 3: Poor Quality**
❌ Before: Basic template without legal references
✅ After: Professional with КоАП РФ references and Пленум ВС РФ

---

## ✅ What Changed

### **1. Intake Agent - Give Advice, Not Petitions**

**Before:**
```
Bot generates petition inline (poor quality)
```

**After:**
```
Bot gives advice and says:
"💡 Если нужно ходатайство о переносе — напишите, подготовлю профессиональный документ."
```

**Benefit:** Client explicitly requests petition → routes to PetitionAgent

---

### **2. Petition Agent - Professional Documents**

**New Requirements:**
- ✅ Request ALL required data (ФИО, адрес, суд, дата)
- ✅ Use REAL data, not placeholders
- ✅ Include legal references (ст. 24.4, 25.1 КоАП РФ)
- ✅ Send as clean text (no HTML tags)
- ✅ Add instructions on how to submit

**Example Output:**
```
📄 Ходатайство готово:

В Хостинский районный суд г. Сочи
от Иванова Ивана Ивановича
Адрес: г. Сочи, ул. Ленина, д. 10, кв. 5

ХОДАТАЙСТВО
о переносе судебного заседания

Судебное заседание по делу об административном правонарушении, 
предусмотренном ч.1 ст.12.8 КоАП РФ, назначено на 15.10.2025.

В связи с необходимостью подготовки защиты, сбора доказательств 
и привлечения профессионального представителя прошу перенести 
рассмотрение дела на более позднюю дату.

Согласно ст. 24.4 КоАП РФ, лицо, в отношении которого ведется 
производство по делу об административном правонарушении, вправе 
знакомиться со всеми материалами дела, давать объяснения, 
представлять доказательства, заявлять ходатайства.

Для реализации права на защиту мне необходимо время для:
- Ознакомления с материалами дела
- Подготовки возражений на протокол
- Сбора доказательств в свою защиту
- Привлечения представителя

На основании изложенного, руководствуясь ст. 24.4, ст. 25.1 КоАП РФ,

ПРОШУ:
1. Перенести рассмотрение дела об административном правонарушении 
   на более позднюю дату (через 2-3 недели)
2. Предоставить возможность ознакомления с материалами дела

Дата: 13.10.2025
Подпись: ___________ (Иванов И.И.)

✅ Как подать:
1. Скопируйте текст выше
2. Распечатайте или перепишите от руки
3. Подайте в канцелярию суда СЕГОДНЯ
4. Сохраните копию с отметкой о приеме

⚠️ Также заявите ходатайство устно в начале заседания!
```

---

## 🎯 New Conversation Flow

### **Step 1: Client Mentions Urgent Court**
```
User: "Суд завтра в Сочи"

Bot: ⚠️ Срочное дело! Суд через 2 дня.

Срочный план действий:

1️⃣ СЕГОДНЯ:
• Запросите материалы дела в суде
• Сфотографируйте ВСЕ документы
• Подайте ходатайство о переносе

2️⃣ ЗАВТРА:
• Отнесите ходатайство в канцелярию
• Запросите копии материалов
• Не давайте показаний без юриста

💡 Если нужно ходатайство о переносе — напишите, 
   подготовлю профессиональный документ.
```

### **Step 2: Client Requests Petition**
```
User: "Нужно ходатайство о переносе"

Bot: Для ходатайства нужно:
1. Ваше ФИО полностью
2. Адрес регистрации
3. Точное название суда (например: "Хостинский районный суд г. Сочи")
4. Дата заседания

Пришлите эти данные — подготовлю за 5 минут.
```

### **Step 3: Client Provides Data**
```
User: "Иванов Иван Иванович, Сочи ул Ленина 10-5, 
       Хостинский суд, суд 15 октября"

Bot: [Generates professional petition with REAL data]
```

---

## 📊 Quality Comparison

| Aspect | Before | After |
|--------|--------|-------|
| **Data** | Generic placeholders | Real client data |
| **Legal Refs** | Missing | ст. 24.4, 25.1 КоАП РФ |
| **Format** | HTML tags mixed in | Clean text |
| **Instructions** | None | Step-by-step guide |
| **Professionalism** | Low | High |
| **Usability** | Hard to copy | Easy to copy/print |

---

## 🧪 Test the Improvements

```bash
python run_bot_local.py
```

**Send this sequence:**

1. `Суд завтра в Сочи`
   → Bot gives advice, mentions petition

2. `Нужно ходатайство о переносе`
   → Bot requests data (ФИО, адрес, суд)

3. `Иванов Иван Иванович, Сочи ул Ленина 10, Хостинский суд`
   → Bot generates PROFESSIONAL petition with real data

---

## ✅ Expected Results

### **Petition Quality:**
- ✅ Uses real client data
- ✅ Professional legal language
- ✅ Correct КоАП РФ references
- ✅ Clean text format (no HTML)
- ✅ Clear submission instructions

### **User Experience:**
- ✅ Easy to copy
- ✅ Easy to print
- ✅ Professional appearance
- ✅ Clear next steps

---

## 📁 Files Modified

1. **`ai_engine/prompts/intake_prompt.py`**
   - Removed inline petition generation
   - Added advice to request petition from PetitionAgent

2. **`ai_engine/prompts/petition_prompt.py`**
   - Added requirement to use REAL data
   - Added professional example
   - Added clean text format
   - Added submission instructions

---

## 🎓 Key Improvements

### **1. Data Collection**
- ❌ Before: Generated with placeholders
- ✅ After: Requests all required data first

### **2. Legal Quality**
- ❌ Before: Basic template
- ✅ After: Professional with legal references

### **3. Format**
- ❌ Before: HTML tags mixed in
- ✅ After: Clean text for copying

### **4. Instructions**
- ❌ Before: None
- ✅ After: Step-by-step submission guide

---

## 🚀 Ready to Test!

**The petition system now:**
- ✅ Requests real data
- ✅ Generates professional documents
- ✅ Includes legal references
- ✅ Easy to copy and submit

**Test it:**
```bash
python run_bot_local.py
```

Send: `Нужно ходатайство о переносе суда`

**Expected:** Bot requests data, then generates professional petition! ✅

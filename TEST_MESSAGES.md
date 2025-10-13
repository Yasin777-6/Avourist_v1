# 📱 TEST MESSAGES - Complete Testing Guide

## 🎯 How to Test the Bot

Send these messages **in order** to test all features.

---

## 🧪 Test Scenario 1: Full Sales Funnel (DUI Case)

### **Message 1: Article Identification**
```
Меня остановили пьяным за рулем
```

**Expected Response:**
- ✅ Identifies ч.1 ст.12.8 КоАП РФ
- ✅ Shows штраф 30,000₽ + лишение прав 1.5-2 года
- ✅ Mentions шанс успеха 70-75%
- ✅ Asks: "Правильно понимаю, дело по ч.1 ст.12.8 КоАП РФ?"

---

### **Message 2: Confirmation**
```
Да
```

**Expected Response:**
- ✅ Requests documents (протокол, освидетельствование)
- ✅ Asks for дата суда
- ✅ Offers free consultation
- ✅ Says: "Можете прислать фото протокола?"

---

### **Message 3: Send Photo (Any Image)**
```
[Send any photo from your phone]
```

**Expected Response:**
- ✅ Analyzes photo (or says text not recognized)
- ✅ Finds "violations" (typical ones for ст.12.8)
- ✅ Lists 3 нарушения ГИБДД
- ✅ Asks: "Суд когда?"

---

### **Message 4: Urgent Court Date**
```
Суд послезавтра
```

**Expected Response:**
- ✅ Creates urgency: "⚠️ СРОЧНОЕ ДЕЛО!"
- ✅ Gives action plan (1️⃣ СЕГОДНЯ, 2️⃣ ЗАВТРА, 3️⃣ В СУДЕ)
- ✅ Lists typical violations to look for
- ✅ Offers: "Если нужно ходатайство о переносе — напишите"

---

### **Message 5: Request Petition**
```
Нужно ходатайство о переносе
```

**Expected Response:**
- ✅ Requests data: ФИО, адрес, название суда, дата заседания
- ✅ Says: "Подготовлю за 10 минут"
- ✅ Professional tone

---

### **Message 6: Provide Data**
```
Иванов Иван Иванович, Москва ул Ленина 10, Таганский суд, суд 15 октября
```

**Expected Response:**
- ✅ Sends .docx file (NOT text message!)
- ✅ Caption: "📄 Ходатайство готово!"
- ✅ File contains clean text (no HTML tags like `<b>`)
- ✅ Instructions on how to submit

---

### **Message 7: Thank You**
```
Спасибо за ходатайство
```

**Expected Response:**
- ✅ Shows ROI calculation
- ✅ "💰 Без юриста: 565,000₽ потери"
- ✅ "✅ С юристом: 30,000₽"
- ✅ "Защита окупается в 14 раз!"
- ✅ Asks: "Берем ваше дело?"

---

### **Message 8: Pricing Question**
```
Сколько стоит защита?
```

**Expected Response:**
- ✅ Shows pricing by instance (1-4)
- ✅ 1st instance: 30,000₽ (Moscow) or 15,000₽ (Regions)
- ✅ Shows document preparation deadlines
- ✅ ROI calculation
- ✅ Strong CTA

---

### **Message 9: Contract Request**
```
Давайте оформим договор
```

**Expected Response:**
- ✅ Requests passport data (ФИО, серия/номер, адрес)
- ✅ Shows payment terms (50% prepayment)
- ✅ Price matches estimated_cost
- ✅ Professional tone

---

## 🧪 Test Scenario 2: Speeding Case

### **Message 1:**
```
Превышение скорости на 80 км/ч
```

**Expected:**
- ✅ Identifies ч.5 ст.12.9 КоАП РФ
- ✅ Shows штраф or лишение прав
- ✅ Asks for confirmation

---

## 🧪 Test Scenario 3: Refusal of Medical Examination

### **Message 1:**
```
Отказался от медосвидетельствования
```

**Expected:**
- ✅ Identifies ч.1 ст.12.26 КоАП РФ
- ✅ Shows same penalties as ст.12.8
- ✅ Explains consequences

---

## 🧪 Test Scenario 4: Different Petitions

### **Test 4.1: Postpone Hearing**
```
Нужно ходатайство о переносе суда
```

**Expected:**
- ✅ Requests data
- ✅ Generates professional petition
- ✅ Sends as .docx file

---

### **Test 4.2: Attract Representative**
```
Нужно ходатайство о привлечении представителя
```

**Expected:**
- ✅ Requests data
- ✅ Includes КоАП РФ ст.25.5 reference
- ✅ Includes Пленум ВС РФ reference
- ✅ Sends as .docx file

---

### **Test 4.3: Review Materials**
```
Хочу ознакомиться с материалами дела
```

**Expected:**
- ✅ Generates petition
- ✅ Mentions КоАП РФ ст.25.1
- ✅ Requests photo/video access
- ✅ Sends as .docx file

---

### **Test 4.4: Obtain Court Acts**
```
Нужно получить судебные акты
```

**Expected:**
- ✅ Generates заявление
- ✅ Mentions certified copies
- ✅ Includes legal references
- ✅ Sends as .docx file

---

## 🧪 Test Scenario 5: Pricing by Instance

### **Test 5.1: First Instance**
```
Сколько стоит защита в первой инстанции?
```

**Expected:**
- ✅ 30,000₽ (Moscow) or 15,000₽ (Regions)
- ✅ Deadline: 7-10 рабочих дней
- ✅ ROI calculation

---

### **Test 5.2: Appeal (Second Instance)**
```
Сколько стоит апелляция?
```

**Expected:**
- ✅ 60,000₽ (Moscow) or 35,000₽ (Regions)
- ✅ Deadline: 10-12 рабочих дней
- ✅ Higher complexity explained

---

### **Test 5.3: Cassation (Third Instance)**
```
Сколько стоит кассация?
```

**Expected:**
- ✅ 90,000₽ (Moscow) or 53,000₽ (Regions)
- ✅ Deadline: 15 рабочих дней
- ✅ Cassation specifics

---

### **Test 5.4: Supreme Court (Fourth Instance)**
```
Сколько стоит защита в Верховном Суде?
```

**Expected:**
- ✅ 120,000₽ (Moscow) or 70,000₽ (Regions)
- ✅ Deadline: 15 рабочих дней
- ✅ Supreme Court specifics

---

## 🧪 Test Scenario 6: Edge Cases

### **Test 6.1: Empty Message**
```
 
```
(Just a space)

**Expected:**
- ✅ Handles gracefully
- ✅ Asks for clarification
- ✅ No errors

---

### **Test 6.2: Very Long Message**
```
Меня остановили за рулем в состоянии алкогольного опьянения, был составлен протокол об административном правонарушении, проводилось медицинское освидетельствование, показания алкотестера составили 0.5 промилле, в протоколе указано что я отказался от медосвидетельствования хотя на самом деле я согласился, также в протоколе не указано точное время задержания, понятые при освидетельствовании отсутствовали, прибор освидетельствования не имел действующей поверки, срок поверки истек три месяца назад, суд назначен на послезавтра в Таганском районном суде города Москвы, мне нужна помощь юриста для защиты моих прав и интересов в суде
```

**Expected:**
- ✅ Processes without error
- ✅ Identifies article
- ✅ Responds coherently

---

### **Test 6.3: Special Characters**
```
Штраф 30,000₽ по ст.12.8 КоАП РФ №123456
```

**Expected:**
- ✅ Handles ₽, №
- ✅ Recognizes article reference
- ✅ No encoding errors

---

### **Test 6.4: Multiple Questions**
```
Сколько стоит? Когда будет готово? Какие шансы?
```

**Expected:**
- ✅ Answers all questions
- ✅ Structured response
- ✅ Clear information

---

## 🧪 Test Scenario 7: Conversation Context

### **Test 7.1: Multi-Turn Context**
Send in sequence:
```
1. Меня остановили
2. Пьяный за рулем
3. Сколько стоит?
4. Давайте оформим
```

**Expected:**
- ✅ Maintains context
- ✅ Remembers previous info
- ✅ Smooth flow
- ✅ No repeated questions

---

## 🧪 Test Scenario 8: Different Regions

### **Test 8.1: Moscow**
```
Меня остановили пьяным в Москве
```

**Expected:**
- ✅ Pricing: 30,000₽ (1st instance)
- ✅ Region detected: MOSCOW

---

### **Test 8.2: Regions**
```
Меня остановили пьяным в Сочи
```

**Expected:**
- ✅ Pricing: 15,000₽ (1st instance)
- ✅ Region detected: REGIONS

---

## 📊 Checklist for Each Test

After each message, verify:

- [ ] Response time < 2 seconds
- [ ] No errors in logs
- [ ] Response is relevant
- [ ] No HTML tags in petition text
- [ ] .docx files sent (not text)
- [ ] Proper formatting
- [ ] Context maintained
- [ ] Lead data saved in database

---

## 🎯 Critical Tests (Must Pass)

### **Priority 1: Core Flow**
1. ✅ Article identification
2. ✅ Document request
3. ✅ Petition generation (.docx)
4. ✅ ROI calculation
5. ✅ Contract generation

### **Priority 2: Quality**
6. ✅ No HTML tags in petitions
7. ✅ No repetitive messages
8. ✅ Professional formatting
9. ✅ Real data (no placeholders)

### **Priority 3: Features**
10. ✅ Pricing by instance
11. ✅ Dynamic deadlines
12. ✅ All 8 petition types
13. ✅ Urgency detection

---

## 🚀 Quick Test Script

**Copy-paste these messages one by one:**

```
1. Меня остановили пьяным за рулем
2. Да
3. [Send any photo]
4. Суд послезавтра
5. Нужно ходатайство о переносе
6. Иванов Иван Иванович, Москва ул Ленина 10, Таганский суд, суд 15 октября
7. Спасибо за ходатайство
8. Сколько стоит защита?
9. Давайте оформим договор
```

**Expected:** All 9 messages work correctly! ✅

---

## 📈 Success Criteria

**Bot passes if:**
- ✅ All 9 core messages work
- ✅ Petitions sent as .docx (not text)
- ✅ No HTML tags in documents
- ✅ ROI calculation shown
- ✅ No repetitive responses
- ✅ Response time < 2s
- ✅ Professional appearance

---

## 🎉 Ready to Test!

**Start bot:**
```bash
python run_bot_local.py
```

**Then send the messages above!**

**Expected result:** Professional bot that builds trust and converts! 🚀

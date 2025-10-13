# 📄 DOCUMENT SENDING FEATURE - Send Petitions as .docx Files

## ✅ What Was Implemented

### **Problem:**
❌ Petitions sent as text messages (hard to copy, unprofessional)

### **Solution:**
✅ Petitions automatically sent as downloadable .docx files

---

## 🎯 How It Works

### **1. Document Generator Service**
**File:** `ai_engine/services/document_generator.py`

**Features:**
- Generates professional .docx files
- Proper formatting (margins, fonts, alignment)
- Russian legal document standards
- Auto-cleanup of old files

**Methods:**
- `generate_petition_docx()` - Creates petition documents
- `generate_contract_docx()` - Creates contract documents
- `cleanup_old_documents()` - Removes old temp files

### **2. Smart Message Detection**
**File:** `run_bot_local.py`

**Logic:**
```python
if 'ХОДАТАЙСТВО' in text.upper() and len(text) > 300:
    # Send as .docx document
    send_petition_as_document(chat_id, text)
else:
    # Send as regular text message
    send_telegram_message(chat_id, text)
```

### **3. Telegram Document Sending**
**Function:** `send_petition_as_document()`

**Process:**
1. Generate .docx file
2. Send via Telegram `sendDocument` API
3. Add helpful caption
4. Clean up temp file

---

## 📊 User Experience

### **Before:**
```
[Text message with petition]
ХОДАТАЙСТВО
о переносе судебного заседания

В Хостинский районный суд...
[Hard to copy, no formatting]
```

### **After:**
```
[.docx file attachment]
📄 Ходатайство готово!

✅ Скачайте документ, распечатайте и подайте в суд.

💡 Также можете отредактировать в Word при необходимости.
```

**Client can:**
- ✅ Download .docx file
- ✅ Open in Microsoft Word
- ✅ Edit if needed
- ✅ Print directly
- ✅ Professional appearance

---

## 🎨 Document Formatting

### **Margins:**
- Top: 1 inch (2.54 cm)
- Bottom: 1 inch (2.54 cm)
- Left: 1.2 inches (3 cm)
- Right: 0.8 inches (2 cm)

### **Fonts:**
- Title: 14pt, Bold, Centered
- Court address: 12pt, Right-aligned
- Body text: 12pt, Justified
- Legal references: 12pt, Justified

### **Structure:**
```
                    [Court name - right-aligned]
                    [From: Name - right-aligned]
                    [Address - right-aligned]

            ХОДАТАЙСТВО
    о переносе судебного заседания

[Body text - justified, 12pt]

[Legal references]

ПРОШУ:
1. [Specific request]

Дата: __________
Подпись: __________
```

---

## 🧪 Testing

### **Test 1: Petition Generation**
```bash
python run_bot_local.py
```

**Send to bot:**
```
Нужно ходатайство о переносе
```

**Expected:**
1. Bot requests data (ФИО, адрес, суд)
2. You provide data
3. Bot sends .docx file (not text!) ✅

### **Test 2: Document Quality**
1. Download the .docx file from Telegram
2. Open in Microsoft Word
3. Check formatting:
   - ✅ Proper margins
   - ✅ Professional appearance
   - ✅ Editable
   - ✅ Ready to print

---

## 📁 Files Created/Modified

### **Created:**
1. `ai_engine/services/document_generator.py` - Document generation service
2. `temp_documents/` - Temporary storage for generated files

### **Modified:**
1. `run_bot_local.py` - Added document sending logic

### **Dependencies:**
- `python-docx==0.8.11` (already in requirements.txt) ✅

---

## 🔧 Technical Details

### **Document Generation:**
```python
from ai_engine.services.document_generator import DocumentGenerator

doc_gen = DocumentGenerator()
filepath = doc_gen.generate_petition_docx(
    petition_text="[petition content]",
    client_name="Иванов Иван"
)
# Returns: "temp_documents/Ходатайство_Иванов_Иван_20251013_190530.docx"
```

### **Telegram Sending:**
```python
url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"

with open(filepath, 'rb') as doc_file:
    files = {'document': doc_file}
    data = {
        'chat_id': chat_id,
        'caption': '📄 Ходатайство готово!'
    }
    response = requests.post(url, files=files, data=data)
```

### **Auto-Cleanup:**
```python
# Delete files older than 1 day
doc_gen.cleanup_old_documents(days=1)
```

---

## 🎯 Benefits

### **For Clients:**
- ✅ Professional .docx files
- ✅ Easy to download and print
- ✅ Editable in Word
- ✅ Proper legal formatting
- ✅ No copy-paste errors

### **For Lawyers:**
- ✅ Professional appearance
- ✅ Consistent formatting
- ✅ Reduced support requests
- ✅ Higher perceived value

### **For Business:**
- ✅ Higher conversion (professional = trustworthy)
- ✅ Reduced complaints
- ✅ Better reviews
- ✅ Competitive advantage

---

## 🚀 Deployment

### **Install Dependencies:**
```bash
pip install python-docx==0.8.11
```
(Already in requirements.txt, so just run `pip install -r requirements.txt`)

### **Start Bot:**
```bash
python run_bot_local.py
```

### **Test:**
Send: `Нужно ходатайство о переносе`

**Expected:** Bot sends .docx file! ✅

---

## 📊 Metrics to Track

### **Before (Text Messages):**
- Client satisfaction: Low
- Support requests: High ("How do I copy this?")
- Conversion rate: Lower

### **After (.docx Files):**
- Client satisfaction: High ✅
- Support requests: Low ✅
- Conversion rate: Higher ✅
- Professional perception: Much better ✅

---

## 🔮 Future Enhancements

### **Possible Improvements:**
1. **PDF Generation** - Also send as PDF for non-editable version
2. **Email Sending** - Send documents via email too
3. **Cloud Storage** - Store documents in cloud (S3, Google Drive)
4. **Templates** - Pre-designed Word templates with logos
5. **Digital Signatures** - Add digital signature support

---

## ✅ Success Criteria

**Feature is successful if:**
- ✅ Petitions sent as .docx files (not text)
- ✅ Files are downloadable
- ✅ Files open correctly in Word
- ✅ Formatting is professional
- ✅ No errors in document generation

---

## 🎉 Ready to Use!

**The bot now:**
- ✅ Detects petitions automatically
- ✅ Generates professional .docx files
- ✅ Sends as Telegram documents
- ✅ Includes helpful caption
- ✅ Cleans up temp files

**Test it:**
```bash
python run_bot_local.py
```

Send: `Нужно ходатайство о переносе`

**Expected:** You receive a .docx file you can download and print! 📄✅

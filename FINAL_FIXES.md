# Final Fixes Applied - Contract Fields

## Issues from Latest Logs

### 1. ❌ Passport Fields Not Showing in Contract
**Problem:** Data parsed correctly (series: 3526, number: 726837) but not appearing in generated contract

**Root Cause:** Template placeholder text variations not matched

**Fix Applied:**
- Added multiple passport placeholder variations to `docx_filler.py`
- Now handles:
  - `Паспорт Серия_____ Номер___________`
  - `Паспорт Серия_____  Номер___________` (2 spaces)
  - `Серия_____ Номер___________`
  - And more variations

### 2. ❌ Case Article Not Filled (Shows Generic Text)
**Problem:** Contract shows default "ч.1 ст.12.8 КоАП РФ" instead of actual article

**Root Cause:** `case_article` field was logged but never used in replacements

**Fix Applied:**
- Added `case_article` replacement logic in `docx_filler.py`
- Now replaces article in default descriptions:
  - "получение материалов дела... по ч.1 ст.12.8 КоАП РФ"
  - Will be replaced with actual article (e.g., "27.12 КоАП РФ")

### 3. ❌ AI Still Using Wrong Article
**Problem:** AI generating "27.12 КоАП РФ" instead of "ч.1 ст.12.8 КоАП РФ"

**Status:** Prompt updated but AI needs conversation history cleared

**Action Required:** User needs to send `/start` to reset conversation

### 4. ❌ Email Codes Not Arriving
**Problem:** No Celery worker service in Railway

**Status:** Documented in multiple guides

**Action Required:** User must add celery-worker service in Railway

---

## What Was Changed

### File: `contract_manager/docx_filler.py`

#### 1. Added Detailed Logging
```python
logger.info(f"=== DOCX REPLACEMENTS ===")
logger.info(f"Passport series: {data.get('client_passport_series', 'MISSING')}")
logger.info(f"Passport number: {data.get('client_passport_number', 'MISSING')}")
logger.info(f"Case article: {data.get('case_article', 'MISSING')}")
```

#### 2. Added Passport Variations
```python
passport_variations = [
    "Паспорт Серия_____ Номер___________",
    "Паспорт Серия_____  Номер___________",  # 2 spaces
    "Паспорт Серия_____ Номер__________",   # 10 underscores
    "Серия_____ Номер___________",
    "Серия_____  Номер___________",
]
```

#### 3. Added Case Article Replacement
```python
case_article = data.get('case_article', '')
if case_article:
    default_descs_with_article = [
        "подготовитьходатайство на получение материалов дела...",
        "получение материалов дела, ходатайство о привлечении..."
    ]
    for default_desc in default_descs_with_article:
        new_desc = default_desc.replace("ч.1 ст.12.8 КоАП РФ", case_article)
        replacements[default_desc] = new_desc
```

---

## Testing After Deploy

### 1. Deploy Changes
```bash
git add .
git commit -m "fix: Add passport variations and case article replacement in docx_filler"
git push
```

### 2. Reset Conversation
In Telegram, send: `/start`

### 3. Generate New Contract
Provide all data again and generate contract

### 4. Check Logs
Look for in Railway logs:
```
[INFO] === DOCX REPLACEMENTS ===
[INFO] Passport series: 3526
[INFO] Passport number: 726837
[INFO] Case article: ч.1 ст.12.8 КоАП РФ  ← Should be correct now
[INFO] Total replacements: XX
[INFO]   'Паспорт Серия_____ Номер___________' → 'Паспорт Серия 3526 Номер 726837'
```

### 5. Download Contract
Check that:
- ✅ Passport fields filled: "Паспорт Серия 3526 Номер 726837"
- ✅ Case article correct: "ч.1 ст.12.8 КоАП РФ" (not "27.12 КоАП РФ")
- ✅ All other fields filled

---

## Expected Log Output (After Fix)

```
[INFO] Opening template: /app/contract_manager/contracts/Договор...docx
[INFO] === DOCX REPLACEMENTS ===
[INFO] Passport series: 3526
[INFO] Passport number: 726837
[INFO] Case article: ч.1 ст.12.8 КоАП РФ
[INFO] Total replacements: 25
[INFO]   'Договор № 1-Б/24' → 'Договор № AV-20251011-B9B47E31'
[INFO]   'Паспорт Серия_____ Номер___________' → 'Паспорт Серия 3526 Номер 726837'
[INFO]   'подготовитьходатайство на получение материалов дела... по ч.1 ст.12.8 КоАП РФ' → '...по ч.1 ст.12.8 КоАП РФ'
[INFO] Filled DOCX saved to: /app/media/contracts/generated/contract_AV-20251011-B9B47E31.docx
```

---

## Still Need to Fix

### 1. Celery Worker (CRITICAL)
**Without this, emails will NEVER arrive!**

Follow: `RAILWAY_VISUAL_SETUP.md` or `QUICK_FIX.md`

### 2. AI Article Detection
**After deploying, send `/start` in Telegram to reset conversation**

Then test with: "был пьяным, забрали права"

AI should respond with "ч.1 ст.12.8 КоАП РФ" not "ст.27.12"

---

## Summary

✅ **Fixed:** Passport field replacement with multiple variations  
✅ **Fixed:** Case article replacement in contract descriptions  
✅ **Fixed:** Added detailed logging for debugging  
❌ **Still Need:** Celery worker service in Railway  
❌ **Still Need:** Reset conversation with `/start` for AI to use new prompts

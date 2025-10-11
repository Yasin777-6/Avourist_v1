# AI Contract Data Parsing Improvements

## Problem
The AI was not correctly extracting passport data and other fields from user messages. Example:
- Input: "номер пасспорта 2123 серия 124214"
- Expected: Series=2123, Number=124214
- Previous behavior: Failed to parse or mixed up the values

## Solution

### 1. Improved AI Prompt (`ai_engine/services/prompts.py`)

**Added explicit data collection instructions:**
- Step-by-step guide for collecting ALL required fields
- Clear format specification for GENERATE_CONTRACT command
- Pipe-delimited format: `ФИО|ДД.ММ.ГГГГ|серия ХХХХ номер ХХХХХХ|адрес|телефон|email|статья|инстанция|WITH_POA/WITHOUT_POA`

**Example command:**
```
[GENERATE_CONTRACT:Иванов Иван Иванович|12.03.1990|серия 4512 номер 123456|г. Москва, ул. Ленина, д. 5|+79991234567|test@mail.ru|ч.1 ст. 12.8 КоАП РФ|1|WITHOUT_POA]
```

### 2. New Pipe Format Parser (`ai_engine/services/contracts_flow.py`)

**Added `_parse_pipe_format()` method:**
- Parses structured pipe-delimited data from AI
- Extracts passport series (4 digits) and number (6 digits) correctly
- Saves email and phone to lead automatically

### 3. Enhanced Natural Language Parser

**Improved passport parsing with multiple fallback strategies:**

1. **Explicit format:** "серия 4512 номер 123456"
2. **Reversed format:** "номер 123456 серия 4512"
3. **Standalone numbers:** Finds any 4-digit and 6-digit numbers and matches them correctly

**Example patterns handled:**
- "серия 2123 номер 124214" ✅
- "номер 2123 серия 124214" ✅
- "паспорт 2123 124214" ✅
- "2123 124214" ✅

### 4. Data Flow

```
User Message → AI (DeepSeek) → [GENERATE_CONTRACT:...] → 
  ↓
contracts_flow.handle_contract_generation()
  ↓
If "|" in data → _parse_pipe_format() (structured)
Else → _parse_contract_data() (natural language)
  ↓
Contract Generation → Email Code (Celery async) → User
```

## Testing

Test with your example:
```
Ясин Арстанбеков Нааматович
12.03.2000
номер пасспорта 2123 серия 124214
адрес Москва чуковская 5
email kyzkyz777@gmail.com
+7888965834
```

Expected parsing:
- ✅ ФИО: Ясин Арстанбеков Нааматович
- ✅ Дата рождения: 12.03.2000
- ✅ Серия паспорта: 2123
- ✅ Номер паспорта: 124214
- ✅ Адрес: Москва чуковская 5
- ✅ Email: kyzkyz777@gmail.com
- ✅ Телефон: +7888965834

## Deployment

1. Commit changes:
   ```bash
   git add .
   git commit -m "Fix: Improve AI contract data parsing with pipe format and enhanced regex"
   git push
   ```

2. The changes will automatically deploy on Railway

3. Test with a new conversation in Telegram bot

## Files Modified

1. `ai_engine/services/prompts.py` - Enhanced AI instructions
2. `ai_engine/services/contracts_flow.py` - Added pipe parser and improved regex
3. `contract_manager/services.py` - Async email with Celery
4. `contract_manager/tasks.py` - New Celery task for emails
5. `autouristv1/settings.py` - Celery configuration
6. `docker-compose.yml` - Added celery_worker service

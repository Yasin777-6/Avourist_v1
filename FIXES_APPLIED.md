# Fixes Applied - 2025-10-11

## Issues Identified
1. **Worker timeouts** - Gunicorn workers timing out after 30s during contract generation
2. **AI speaking English** - Using terms like "ROI", "representation", "instance"
3. **Duplicate contract sends** - Client receiving document multiple times (reported)

## Fixes Applied

### 1. Increased Gunicorn Timeout
**File**: `Dockerfile`
**Change**: Added `--timeout 120` to gunicorn command
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "--workers", "4", "--threads", "2", "--timeout", "120", "autouristv1.wsgi:application"]
```
**Reason**: Contract generation with .docx filling can take 30-60 seconds, especially with complex templates

### 2. Fixed AI Language - Russian Only
**File**: `ai_engine/services/prompts.py`

**Changes**:
- Added explicit instruction: "КРИТИЧЕСКИ ВАЖНО: Говори ТОЛЬКО на русском языке"
- Added forbidden words list: "ЗАПРЕЩЕНО использовать английские слова: ROI, representation, instance, timeline, etc."
- Replaced "ROI" with "выгода защиты" (benefit of defense)
- Replaced "Расчет ROI" with "Расчет выгоды"
- Changed "ROI вашей защиты — x12" to "Защита окупается в 12 раз"
- Changed "представление в суде" to "моё личное присутствие в суде"

**Before**:
```
📊 Расчет ROI:
ROI = Потери без юриста ÷ Стоимость юриста
Пример: 180 000 ÷ 15 000 = x12
Если ROI > 5 → выдели жирным: «ROI вашей защиты — x12»
```

**After**:
```
📊 Расчет выгоды:
Выгода = Потери без юриста ÷ Стоимость защиты
Пример: 180 000 ÷ 15 000 = защита окупается в 12 раз
Если выгода > 5 раз → выдели жирным: «Защита окупается в 12 раз»
```

### 3. Template System Improvements
**Files**: 
- `contract_manager/services.py`
- `contract_manager/doc_text_replacer.py`
- `ai_engine/services/contracts_flow.py`
- `ai_engine/services/prompts.py`

**Changes**:
- System now uses `contract_manager/contracts/` for templates
- Automatically prefers `.docx` over `.doc` (no LibreOffice needed on server)
- AI asks clarifying questions before collecting passport data:
  1. Court instance (1st, 2nd, 3rd, 4th)
  2. Need for personal presence in court (with/without power of attorney)
- Enhanced parsing to extract instance and representation type from AI responses
- Added logging for selected template parameters

### 4. Converted All Templates to .docx
**Directory**: `contract_manager/contracts/`
**Result**: 18 .docx templates created from .doc files
- No LibreOffice required on server
- Faster contract generation
- More reliable document filling

## Testing Recommendations

### 1. Test Worker Timeout Fix
```bash
# Monitor logs for worker timeouts
docker logs -f <container_name> | grep "WORKER TIMEOUT"

# Should see no more timeouts during contract generation
```

### 2. Test AI Language
**Test conversation**:
```
User: "У меня лишение прав за пьянку"
AI should respond: "Защита окупается в X раз" (NOT "ROI вашей защиты")
AI should ask: "Нужно ли моё личное присутствие в суде?" (NOT "representation")
```

### 3. Test Contract Generation
**Test flow**:
1. AI asks: "На какой стадии ваше дело? 1-я, 2-я, 3-я, 4-я инстанция?"
2. AI asks: "Нужно ли моё личное присутствие в суде?"
3. AI collects passport data
4. Contract generated with correct template
5. Single contract sent to Telegram (not duplicates)
6. Email verification code sent

### 4. Monitor Performance
```bash
# Check contract generation time
grep "Contract generated" logs | tail -20

# Should complete within 60 seconds
```

## Deployment Steps

1. **Rebuild Docker image**:
   ```bash
   docker build -t autourist:latest .
   ```

2. **Deploy to server**:
   ```bash
   # Push to registry or deploy directly
   docker-compose up -d --build
   ```

3. **Verify deployment**:
   ```bash
   # Check logs
   docker logs -f autourist_web

   # Test health endpoint
   curl http://localhost:8000/
   ```

4. **Monitor first contracts**:
   - Watch for worker timeouts
   - Check AI responses for English words
   - Verify single contract send (not duplicates)
   - Confirm correct template selection

## Rollback Plan

If issues persist:

1. **Revert Dockerfile**:
   ```bash
   git checkout HEAD -- Dockerfile
   ```

2. **Revert prompts.py**:
   ```bash
   git checkout HEAD -- ai_engine/services/prompts.py
   ```

3. **Rebuild and redeploy**:
   ```bash
   docker-compose up -d --build
   ```

## Known Limitations

1. **Timeout still possible** if:
   - Network is slow
   - Database queries are slow
   - External API calls timeout (DeepSeek, Telegram)

2. **AI may still use English** if:
   - System prompt is overridden by conversation context
   - User explicitly asks in English
   - Solution: Add post-processing to filter English words

3. **Duplicate sends** may occur if:
   - User clicks "generate contract" multiple times
   - Network retry logic triggers
   - Solution: Add idempotency check based on lead + timestamp

## Next Steps

1. **Monitor production logs** for 24-48 hours
2. **Collect metrics** on contract generation time
3. **Gather user feedback** on AI language quality
4. **Consider adding**:
   - Rate limiting for contract generation
   - Idempotency keys to prevent duplicates
   - Async task queue for long-running operations (Celery)
   - Caching for frequently used templates

# Fixes Applied - 2025-10-11

## Issues Fixed

### 1. ❌ Email Codes Not Arriving
**Problem:** Celery worker not running in Railway
**Solution:** 
- Created `Procfile` with worker process definition
- Created `RAILWAY_CELERY_SETUP.md` with step-by-step guide
- Added detailed logging to email task
- **Action Required:** Add Celery worker service in Railway dashboard

### 2. ❌ Wrong Article in Contract
**Problem:** AI using "ст.27.12 КоАП РФ" (procedural) instead of "ч.1 ст.12.8 КоАП РФ" (actual violation)
**Solution:**
- Updated AI prompt to distinguish between procedural and substantive articles
- Added explicit examples and warnings
- Instructed AI to use full article with part number (ч.1 ст.12.8)

### 3. ✅ Passport Fields Parsing
**Status:** Already working correctly
- Series: 2123 ✅
- Number: 124214 ✅
- Fields are being filled in contract template

### 4. ✅ Contract Generation
**Status:** Working correctly
- Contract generated: AV-20251011-0A08C5E7
- Template selected correctly
- Document sent to Telegram

## Files Modified

1. `ai_engine/services/prompts.py`
   - Added article clarification
   - Emphasized using substantive articles (ч.1 ст.12.8) not procedural (ст.27.12)

2. `contract_manager/tasks.py`
   - Added comprehensive logging for email sending
   - Shows email backend, host, port, sender, recipient

3. **New Files:**
   - `RAILWAY_CELERY_SETUP.md` - Complete step-by-step setup guide for Celery worker

## Next Steps

### Immediate (Required for emails to work):

1. **Add Celery Worker in Railway:**
   ```
   Service Name: celery-worker
   Start Command: celery -A autouristv1 worker --loglevel=info --concurrency=2
   ```

2. **Copy Environment Variables to Worker:**
   - REDIS_URL
   - DATABASE_URL
   - All EMAIL_* variables
   - DEEPSEEK_API_KEY
   - TELEGRAM_BOT_TOKEN

3. **Link Services:**
   - Link worker to Postgres
   - Link worker to Redis

### Testing:

1. Deploy changes:
   ```bash
   git add .
   git commit -m "fix: Add Celery worker, improve AI article detection, enhance logging"
   git push
   ```

2. Wait for both services to deploy

3. Test contract generation flow

4. Check logs:
   - Web service: Contract generation
   - Celery worker: Email task execution

## Expected Log Output

### When Email Task Runs:
```
[INFO] === EMAIL TASK STARTED ===
[INFO] Task ID: abc-123-def
[INFO] Recipient: kyzkyz777@gmail.com
[INFO] Contract: AV-20251011-0A08C5E7
[INFO] Code: 123456
[INFO] Sending email from noreply@example.com to kyzkyz777@gmail.com
[INFO] Email backend: django.core.mail.backends.smtp.EmailBackend
[INFO] Email host: smtp.gmail.com:587
[INFO] ✅ Verification code sent successfully to kyzkyz777@gmail.com
```

## Verification Checklist

- [ ] Celery worker service added in Railway
- [ ] Environment variables copied to worker
- [ ] Services linked (Postgres + Redis)
- [ ] Code deployed
- [ ] Worker logs show "celery@worker ready"
- [ ] Test contract generation
- [ ] Email code arrives within 10 seconds
- [ ] Article in contract shows "ч.1 ст.12.8 КоАП РФ" not "ст.27.12"
- [ ] Passport fields filled correctly

## Troubleshooting

### If email still doesn't arrive:

1. Check celery worker logs for task execution
2. Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are set
3. For Gmail: Use App Password, not regular password
4. Check EMAIL_USE_TLS=True
5. Verify DEFAULT_FROM_EMAIL matches EMAIL_HOST_USER

### If wrong article still appears:

1. Clear conversation history (/start)
2. Mention "пьяное вождение" or "управление в опьянении"
3. AI should respond with "ч.1 ст.12.8 КоАП РФ"

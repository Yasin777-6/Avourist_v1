# Email Not Arriving - Debug Guide

## Current Status from Logs

✅ **Contract Generated:** AV-20251011-EFE274B1  
✅ **Email Task Queued:** `Email task queued for kyzkyz777@gmail.com`  
❌ **Email NOT Arriving:** No Celery worker to process the task

---

## The Problem

Your web service is queuing email tasks to Redis, but **there's no Celery worker running** to process them.

### Evidence from Logs:
```
[INFO] Email task queued for kyzkyz777@gmail.com
```

This means:
1. ✅ Task created successfully
2. ✅ Task sent to Redis queue
3. ❌ **No worker to pick up and execute the task**

---

## Solution: Add Celery Worker Service

### Quick Check: Do you have a celery-worker service in Railway?

**If NO** → Follow these steps:

### 1. Create Celery Worker Service

In Railway Dashboard:
```
1. Click "+ New" → "Empty Service"
2. Connect to your GitHub repo
3. Name: celery-worker
```

### 2. Configure Service

**Settings → Build:**
- Builder: Dockerfile
- Dockerfile Path: `Dockerfile`

**Settings → Deploy:**
- Custom Start Command: 
  ```bash
  celery -A autouristv1 worker --loglevel=info --concurrency=2
  ```

### 3. Add Environment Variables

**Copy ALL variables from web service, especially:**

```bash
# Critical for Celery
REDIS_URL=${{Redis.REDIS_URL}}
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Critical for Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Other required
DEBUG=True
SECRET_KEY=your-secret-key
DEEPSEEK_API_KEY=your-key
TELEGRAM_BOT_TOKEN=your-token
```

### 4. Link Services

In celery-worker Variables tab:
- Add reference to Postgres → `DATABASE_URL`
- Add reference to Redis → `REDIS_URL`

### 5. Deploy and Verify

**Check celery-worker logs for:**
```
[INFO] Connected to redis://...
[INFO] celery@worker ready
[INFO] Registered tasks:
  - contract_manager.tasks.send_verification_email_task
```

---

## Testing Email Flow

### 1. Generate Contract
Send message in Telegram: "давай договор"

### 2. Check Web Service Logs
Should see:
```
[INFO] Email task queued for kyzkyz777@gmail.com
```

### 3. Check Celery Worker Logs
Should see:
```
[INFO] === EMAIL TASK STARTED ===
[INFO] Task ID: abc-123
[INFO] Recipient: kyzkyz777@gmail.com
[INFO] Contract: AV-20251011-EFE274B1
[INFO] Code: 123456
[INFO] Sending email from noreply@example.com to kyzkyz777@gmail.com
[INFO] Email backend: django.core.mail.backends.smtp.EmailBackend
[INFO] Email host: smtp.gmail.com:587
[INFO] ✅ Verification code sent successfully to kyzkyz777@gmail.com
```

### 4. Check Gmail
Email should arrive within 10 seconds with subject:
```
Код подтверждения договора AV-20251011-EFE274B1
```

---

## Gmail Setup (If Using Gmail)

### 1. Enable 2-Factor Authentication
1. Go to Google Account settings
2. Security → 2-Step Verification → Turn On

### 2. Generate App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Name it: "Railway Autourist"
4. Copy the 16-character password

### 3. Use in Railway
```bash
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop  # App password (16 chars)
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

---

## Common Issues

### Issue: Worker starts but crashes immediately

**Check logs for:**
- `ModuleNotFoundError` → Missing dependencies in requirements.txt
- `Connection refused` → REDIS_URL not set or wrong
- `Database error` → DATABASE_URL not set

**Fix:** Ensure ALL environment variables are copied from web service

### Issue: Task queued but never executes

**Symptoms:**
- Web logs: `Email task queued`
- Worker logs: Nothing

**Cause:** REDIS_URL mismatch between services

**Fix:** 
1. Check web service REDIS_URL
2. Check celery-worker REDIS_URL
3. They must be identical
4. Use reference: `${{Redis.REDIS_URL}}`

### Issue: Email sending fails with authentication error

**Symptoms:**
```
[ERROR] Failed to send email: (535, b'5.7.8 Username and Password not accepted')
```

**Fix:**
1. Use App Password, not regular password
2. Verify EMAIL_HOST_USER matches DEFAULT_FROM_EMAIL
3. Check EMAIL_USE_TLS=True

### Issue: Email sending fails with connection timeout

**Symptoms:**
```
[ERROR] Failed to send email: [Errno 110] Connection timed out
```

**Fix:**
1. Check EMAIL_HOST is correct (smtp.gmail.com)
2. Check EMAIL_PORT is 587 (not 465 or 25)
3. Verify EMAIL_USE_TLS=True

---

## Verification Checklist

- [ ] Celery worker service exists in Railway
- [ ] Custom start command set: `celery -A autouristv1 worker...`
- [ ] All environment variables copied from web service
- [ ] REDIS_URL linked from Redis service
- [ ] DATABASE_URL linked from Postgres service
- [ ] Worker logs show "celery@worker ready"
- [ ] Gmail App Password generated and set
- [ ] Test contract generation
- [ ] Check worker logs for task execution
- [ ] Email arrives within 10 seconds

---

## Quick Test Command

Once worker is running, test email manually:

```python
# In Railway web service console or Django shell
from contract_manager.tasks import send_verification_email_task

# Queue test email
send_verification_email_task.delay(
    'kyzkyz777@gmail.com',
    '123456',
    'TEST-CONTRACT'
)
```

Check worker logs for execution.

---

## Need Help?

1. Share celery-worker logs
2. Share web service logs showing "Email task queued"
3. Confirm REDIS_URL is set in both services
4. Confirm EMAIL_* variables are set in celery-worker

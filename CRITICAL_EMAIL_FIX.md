# 🚨 CRITICAL: Email Codes Still Not Arriving

## Current Status from Latest Logs

✅ **Article FIXED!** - Now using "ч.1 ст.12.8 КоАП РФ" correctly  
✅ **Passport WORKING!** - Series: 2123, Number: 124214 parsed  
✅ **Contract Generated!** - AV-20251011-77CA1172  
❌ **EMAIL NOT ARRIVING!** - Task queued but never processed

## The Root Cause

```
[INFO] Email task queued for kyzkyz777@gmail.com
```

**This line proves the problem:**
- ✅ Web service queues the task to Redis
- ❌ **NO Celery worker exists to process it**
- ❌ Email will **NEVER** arrive without a worker

---

## YOU MUST ADD CELERY WORKER SERVICE

### This is NOT optional. Without it, emails will NEVER work.

---

## Step-by-Step Fix (5 Minutes)

### 1. Open Railway Dashboard
Go to: https://railway.app/

### 2. Select Your Project
Click on your `autouristv1` project

### 3. Create New Service
Click **"+ New"** button → Select **"Empty Service"**

### 4. Connect Repository
- Select your GitHub repository
- Service name: **`celery-worker`**
- Click **"Create"**

### 5. Configure Build
In celery-worker service → **Settings** → **Build**:
- Builder: **Dockerfile**
- Dockerfile Path: `Dockerfile`

### 6. Set Start Command
In celery-worker service → **Settings** → **Deploy**:

**Custom Start Command:**
```bash
celery -A autouristv1 worker --loglevel=info --concurrency=2
```

### 7. Add Environment Variables
In celery-worker service → **Variables** tab:

**Copy ALL these from your web service:**

```bash
# Database
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (CRITICAL!)
REDIS_URL=${{Redis.REDIS_URL}}

# Django
DEBUG=True
SECRET_KEY=(copy from web service)

# Email (CRITICAL FOR SENDING CODES!)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=kyzkyz777@gmail.com
EMAIL_HOST_PASSWORD=(your Gmail App Password)
DEFAULT_FROM_EMAIL=kyzkyz777@gmail.com

# Telegram
TELEGRAM_BOT_TOKEN=(copy from web service)

# DeepSeek
DEEPSEEK_API_KEY=(copy from web service)
```

### 8. Link Services
In celery-worker **Variables** tab:
- Click **"Add Reference"**
- Link `DATABASE_URL` from Postgres service
- Link `REDIS_URL` from Redis service

### 9. Deploy
- Click **"Deploy"**
- Wait for deployment to complete

### 10. Verify
Check celery-worker logs for:
```
[INFO] Connected to redis://...
[INFO] celery@worker ready
[INFO] Registered tasks:
  - contract_manager.tasks.send_verification_email_task
```

---

## Gmail App Password Setup

### If you don't have an App Password yet:

1. **Enable 2-Factor Authentication:**
   - Go to https://myaccount.google.com/security
   - Turn on 2-Step Verification

2. **Generate App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it: "Railway Autourist"
   - Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

3. **Use in Railway:**
   ```bash
   EMAIL_HOST_USER=kyzkyz777@gmail.com
   EMAIL_HOST_PASSWORD=abcdefghijklmnop  # No spaces!
   DEFAULT_FROM_EMAIL=kyzkyz777@gmail.com
   ```

---

## Test After Setup

### 1. Generate Contract
In Telegram, send: `/start` then provide all data

### 2. Check Web Service Logs
Should see:
```
[INFO] Email task queued for kyzkyz777@gmail.com
```

### 3. Check Celery Worker Logs
Should see:
```
[INFO] === EMAIL TASK STARTED ===
[INFO] Task ID: abc-123-def
[INFO] Recipient: kyzkyz777@gmail.com
[INFO] Contract: AV-20251011-77CA1172
[INFO] Code: 123456
[INFO] Sending email from kyzkyz777@gmail.com to kyzkyz777@gmail.com
[INFO] Email backend: django.core.mail.backends.smtp.EmailBackend
[INFO] Email host: smtp.gmail.com:587
[INFO] ✅ Verification code sent successfully to kyzkyz777@gmail.com
```

### 4. Check Gmail
Email should arrive within 10 seconds with subject:
```
Код подтверждения договора AV-20251011-77CA1172
```

---

## About "Payment Part Blank"

The payment fields in your logs show:
```python
'prepayment': None
'success_fee': None
'docs_prep_fee': 5000
```

**This is CORRECT!** The template has default payment terms that remain when no custom values are provided. The contract will show:
- Total amount: 15,000 or 25,000 руб (depending on template)
- Prepayment: Default from template
- Success fee: Default from template

If you need custom payment terms, they must be provided in the contract data.

---

## Summary

### What's Working ✅
- Article detection: "ч.1 ст.12.8 КоАП РФ"
- Passport parsing: Series 2123, Number 124214
- Contract generation: AV-20251011-77CA1172
- Task queuing: Email task sent to Redis

### What's NOT Working ❌
- **Email delivery: NO CELERY WORKER!**

### The Fix
**Add celery-worker service in Railway (5 minutes)**

### After Fix
- Emails will arrive within 10 seconds
- Users can verify and sign contracts
- System fully functional

---

## Need Help?

If celery-worker still doesn't work after setup:

1. **Share celery-worker logs** - Check for errors
2. **Verify REDIS_URL** - Must match web service
3. **Verify EMAIL_HOST_PASSWORD** - Must be App Password
4. **Check Gmail settings** - 2FA enabled, App Password generated

---

## Architecture

```
┌─────────────┐
│  Telegram   │
│    Bot      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Web Service │ ✅ Running
│  (Gunicorn) │ ✅ Queues email tasks
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Redis    │ ✅ Running
│   (Queue)   │ ✅ Stores tasks
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Celery    │ ❌ MISSING! ← YOU NEED THIS!
│   Worker    │ ❌ Would process tasks
└─────────────┘
       │
       ▼
    📧 Gmail
```

**Without the Celery worker, tasks sit in Redis forever and emails never send!**

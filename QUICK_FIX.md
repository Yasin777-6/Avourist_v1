# Quick Fix - Email Codes Not Arriving

## The Problem
✅ Contract generates successfully  
✅ "Email task queued" appears in logs  
❌ **But email never arrives!**

## Why?
**Celery worker is NOT running in Railway.**

The web service queues the email task to Redis, but there's no worker to process it.

---

## The Solution (5 minutes)

### In Railway Dashboard:

1. **Create New Service**
   - Click "+ New" → "Empty Service"
   - Connect to your GitHub repo
   - Name: `celery-worker`

2. **Set Custom Start Command**
   - Go to service Settings
   - Find "Custom Start Command"
   - Enter: `celery -A autouristv1 worker --loglevel=info --concurrency=2`

3. **Copy Environment Variables**
   - From web service, copy ALL variables to celery-worker
   - Especially: `REDIS_URL`, `DATABASE_URL`, `EMAIL_*` variables

4. **Link Services**
   - In celery-worker Variables tab
   - Link to Postgres database
   - Link to Redis service

5. **Deploy**
   - Save and deploy
   - Check logs for: `celery@worker ready`

---

## Verify It Works

1. Generate contract in Telegram
2. **Web logs:** `Email task queued for kyzkyz777@gmail.com` ✅
3. **Worker logs:** `=== EMAIL TASK STARTED ===` ✅
4. **Worker logs:** `✅ Verification code sent successfully` ✅
5. **Email arrives within 10 seconds** ✅

---

## Full Guide
See `RAILWAY_CELERY_SETUP.md` for detailed instructions.

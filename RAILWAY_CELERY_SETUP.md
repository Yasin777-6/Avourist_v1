# Railway Celery Worker Setup - CRITICAL FIX

## Problem
❌ Email codes NOT arriving because Celery worker isn't running in Railway.

## Solution: Add Separate Celery Worker Service

Railway doesn't support multiple processes from Dockerfile. You need TWO separate services:
1. **Web Service** (already exists)
2. **Celery Worker Service** (needs to be created)

---

## Step-by-Step Setup

### 1. Create Celery Worker Service

In Railway Dashboard:
1. Go to your project
2. Click **"+ New"** → **"Empty Service"**
3. Connect to your GitHub repo
4. Name it: **`celery-worker`**

### 2. Configure Build Settings

In celery-worker service settings:

**Builder:** Dockerfile

**Dockerfile Path:** `Dockerfile`

**Custom Start Command (IMPORTANT):**
```bash
celery -A autouristv1 worker --loglevel=info --concurrency=2
```

### 3. Add Environment Variables

Copy ALL these from your web service:

**Required:**
```bash
# Database
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis
REDIS_URL=${{Redis.REDIS_URL}}

# Django
DEBUG=True
SECRET_KEY=your-secret-key

# Email (CRITICAL for sending codes)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token

# DeepSeek
DEEPSEEK_API_KEY=your-api-key
```

### 4. Link Services

In celery-worker service:
- Click **"Variables"** tab
- Click **"Add Reference"**
- Link `DATABASE_URL` from Postgres
- Link `REDIS_URL` from Redis

### 5. Deploy

1. Save settings
2. Railway will automatically deploy
3. Check logs for: `[INFO] celery@worker ready`

---

## Verification

### Check Celery Worker Logs:
```
[INFO] Connected to redis://...
[INFO] celery@worker ready
[INFO] Registered tasks:
  - contract_manager.tasks.send_verification_email_task
```

### Test Email Flow:
1. Generate contract in Telegram bot
2. Check web service logs: `Email task queued for kyzkyz777@gmail.com`
3. Check celery-worker logs: `=== EMAIL TASK STARTED ===`
4. Email should arrive within 10 seconds

---

## Troubleshooting

### Worker not starting?
- Check Dockerfile exists in repo
- Verify custom start command is set
- Check all environment variables are copied

### Email still not arriving?
1. Check celery-worker logs for task execution
2. Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
3. For Gmail: Use App Password (not regular password)
4. Ensure EMAIL_USE_TLS=True

### Task queued but not executed?
- Verify REDIS_URL is same in both services
- Check Redis service is running
- Restart celery-worker service

---

## Architecture

```
┌─────────────┐
│   Client    │
│  (Telegram) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Web Service │ ← Handles HTTP requests
│  (Gunicorn) │ ← Queues email tasks to Redis
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Redis    │ ← Message broker
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Celery    │ ← Processes email tasks
│   Worker    │ ← Sends emails asynchronously
└─────────────┘
```

## Important Notes

- ❌ `Procfile` doesn't work with Dockerfile deployments in Railway
- ✅ Use **Custom Start Command** instead
- ✅ Each service needs its own deployment
- ✅ Both services share same codebase (same repo)

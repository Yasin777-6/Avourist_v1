# Railway Visual Setup Guide

## Current Architecture (What You Have)

```
┌─────────────────┐
│   Web Service   │ ← Running ✅
│   (Gunicorn)    │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │ Redis  │ ← Running ✅
    └────────┘
         │
         ▼
    📧 Email tasks queued here...
    ❌ But no worker to process them!
```

## What You Need (Target Architecture)

```
┌─────────────────┐
│   Web Service   │ ← Running ✅
│   (Gunicorn)    │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │ Redis  │ ← Running ✅
    └────┬───┘
         │
         ▼
┌─────────────────┐
│ Celery Worker   │ ← MISSING ❌ (You need to add this!)
│   Service       │
└─────────────────┘
         │
         ▼
    📧 Emails sent! ✅
```

---

## Step-by-Step Visual Guide

### Step 1: Your Railway Dashboard

```
┌─────────────────────────────────────────────┐
│  Project: autouristv1                       │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐  ┌──────────────┐       │
│  │ web          │  │ postgres     │       │
│  │ ✅ Running   │  │ ✅ Running   │       │
│  └──────────────┘  └──────────────┘       │
│                                             │
│  ┌──────────────┐                          │
│  │ redis        │                          │
│  │ ✅ Running   │                          │
│  └──────────────┘                          │
│                                             │
│  👉 Click here: [+ New]                    │
└─────────────────────────────────────────────┘
```

### Step 2: Create New Service

```
┌─────────────────────────────────────────────┐
│  New Service                                │
├─────────────────────────────────────────────┤
│                                             │
│  ○ Deploy from GitHub repo                 │
│  ○ Empty Service  👈 Click this            │
│  ○ Database                                 │
│  ○ Template                                 │
│                                             │
└─────────────────────────────────────────────┘
```

### Step 3: Connect Repository

```
┌─────────────────────────────────────────────┐
│  Connect Repository                         │
├─────────────────────────────────────────────┤
│                                             │
│  Select repository:                         │
│  ☑ Yasin777-6/Avourist_v1  👈 Your repo    │
│                                             │
│  Service name:                              │
│  [celery-worker]  👈 Type this             │
│                                             │
│  [Create Service]                           │
└─────────────────────────────────────────────┘
```

### Step 4: Configure Service Settings

```
┌─────────────────────────────────────────────┐
│  celery-worker Settings                     │
├─────────────────────────────────────────────┤
│                                             │
│  ⚙️ Settings                                │
│     ├─ General                              │
│     ├─ Build  👈 Click here                │
│     ├─ Deploy                               │
│     └─ Variables                            │
│                                             │
└─────────────────────────────────────────────┘
```

#### Build Settings:

```
┌─────────────────────────────────────────────┐
│  Build Settings                             │
├─────────────────────────────────────────────┤
│                                             │
│  Builder: [Dockerfile ▼]  👈 Select this   │
│                                             │
│  Dockerfile Path: [Dockerfile]             │
│                                             │
│  Watch Paths: [Leave empty]                │
│                                             │
└─────────────────────────────────────────────┘
```

#### Deploy Settings:

```
┌─────────────────────────────────────────────┐
│  Deploy Settings                            │
├─────────────────────────────────────────────┤
│                                             │
│  Custom Start Command:  👈 CRITICAL!        │
│  ┌───────────────────────────────────────┐ │
│  │ celery -A autouristv1 worker          │ │
│  │ --loglevel=info --concurrency=2       │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Restart Policy: [Always]                  │
│                                             │
└─────────────────────────────────────────────┘
```

### Step 5: Add Variables

```
┌─────────────────────────────────────────────┐
│  Variables                                  │
├─────────────────────────────────────────────┤
│                                             │
│  [+ New Variable]  👈 Click multiple times  │
│                                             │
│  Add these variables:                       │
│  ┌───────────────────────────────────────┐ │
│  │ REDIS_URL = ${{Redis.REDIS_URL}}      │ │
│  │ DATABASE_URL = ${{Postgres.DATABASE...│ │
│  │ DEBUG = True                           │ │
│  │ SECRET_KEY = (copy from web)          │ │
│  │ EMAIL_HOST = smtp.gmail.com           │ │
│  │ EMAIL_PORT = 587                      │ │
│  │ EMAIL_USE_TLS = True                  │ │
│  │ EMAIL_HOST_USER = your@gmail.com      │ │
│  │ EMAIL_HOST_PASSWORD = app-password    │ │
│  │ DEFAULT_FROM_EMAIL = your@gmail.com   │ │
│  │ DEEPSEEK_API_KEY = (copy from web)    │ │
│  │ TELEGRAM_BOT_TOKEN = (copy from web)  │ │
│  └───────────────────────────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
```

### Step 6: Final Dashboard View

```
┌─────────────────────────────────────────────┐
│  Project: autouristv1                       │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐  ┌──────────────┐       │
│  │ web          │  │ postgres     │       │
│  │ ✅ Running   │  │ ✅ Running   │       │
│  └──────────────┘  └──────────────┘       │
│                                             │
│  ┌──────────────┐  ┌──────────────┐       │
│  │ redis        │  │ celery-worker│ 👈 NEW│
│  │ ✅ Running   │  │ ✅ Running   │       │
│  └──────────────┘  └──────────────┘       │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Verification

### Check Celery Worker Logs

Click on `celery-worker` service → Logs tab

You should see:
```
[INFO] Connected to redis://...
[INFO] celery@worker ready
[INFO] Registered tasks:
  - contract_manager.tasks.send_verification_email_task
```

### Test Email

1. Generate contract in Telegram
2. Check web logs: `Email task queued`
3. Check celery-worker logs: `=== EMAIL TASK STARTED ===`
4. Email arrives in Gmail ✅

---

## Troubleshooting

### Service won't start?

**Check logs for errors:**
- Missing environment variables
- Wrong start command
- Build failures

### Service starts but crashes?

**Common causes:**
- REDIS_URL not set
- DATABASE_URL not set
- Missing EMAIL_* variables

**Fix:** Copy ALL variables from web service

### Email still not arriving?

**Check:**
1. Worker logs show task execution
2. EMAIL_HOST_PASSWORD is App Password (not regular password)
3. EMAIL_USE_TLS=True
4. EMAIL_HOST_USER matches DEFAULT_FROM_EMAIL

---

## Summary

You need **4 services total:**

1. ✅ **web** (Gunicorn) - Already have
2. ✅ **postgres** - Already have
3. ✅ **redis** - Already have
4. ❌ **celery-worker** - **YOU NEED TO ADD THIS!**

Without #4, emails will never be sent!

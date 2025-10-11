# 🚨 URGENT: Email Codes Not Arriving

## The Problem

From your logs:
```
[INFO] Email task queued for kyzkyz777@gmail.com
```

✅ Task is queued  
❌ **But NO Celery worker to process it!**

---

## The Solution (5 Minutes)

### You MUST add a Celery worker service in Railway

**Without this, emails will NEVER arrive!**

---

## Quick Steps

1. **Railway Dashboard** → Your project
2. Click **"+ New"** → **"Empty Service"**
3. Connect to your repo
4. Name: **`celery-worker`**
5. Settings → Deploy → Custom Start Command:
   ```
   celery -A autouristv1 worker --loglevel=info --concurrency=2
   ```
6. Copy ALL environment variables from web service
7. Link to Postgres and Redis
8. Deploy

---

## Detailed Guides

- **Visual Guide:** `RAILWAY_VISUAL_SETUP.md`
- **Step-by-Step:** `RAILWAY_CELERY_SETUP.md`
- **Email Debug:** `EMAIL_DEBUG_GUIDE.md`
- **Quick Reference:** `QUICK_FIX.md`

---

## After Setup

Test:
1. Generate contract in Telegram
2. Check celery-worker logs: `=== EMAIL TASK STARTED ===`
3. Email arrives in Gmail within 10 seconds ✅

---

## AI Article Issue Fixed

Also fixed AI using wrong article (ст.27.12 instead of ч.1 ст.12.8).

After adding worker and redeploying, AI will use correct article.

---

## Deploy Changes

```bash
git add .
git commit -m "fix: Improve AI article detection, add email debug guides"
git push
```

Then add celery-worker service in Railway!

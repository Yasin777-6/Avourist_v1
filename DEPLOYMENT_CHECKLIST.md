# Railway Deployment Checklist

## Pre-Deployment

- [x] Celery configured with Redis for async tasks
- [x] Email sending moved to Celery tasks (non-blocking)
- [x] Gunicorn workers reduced to 2 (optimized)
- [x] Detailed logging enabled across all services
- [x] AI prompt improved for better data extraction
- [x] Passport parsing enhanced with multiple fallback strategies
- [x] Null bytes issue fixed in `__init__.py`

## Environment Variables Required

Set these in Railway dashboard:

### Required
```bash
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.railway.app
CSRF_TRUSTED_ORIGINS=https://your-domain.railway.app

# Database (automatically set by Railway Postgres)
DATABASE_URL=postgresql://...

# Redis (automatically set by Railway Redis)
REDIS_URL=redis://...

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_WEBHOOK_URL=https://your-domain.railway.app

# DeepSeek AI
DEEPSEEK_API_KEY=your-deepseek-key

# Email (Gmail example)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# OCR (optional)
OCR_API_KEY=your-ocr-key
```

### Optional (for debugging)
```bash
DJANGO_LOG_LEVEL=DEBUG
DB_LOG_LEVEL=WARNING
```

## Deployment Steps

### 1. Commit and Push
```bash
git add .
git commit -m "feat: Add Celery, improve logging, fix AI parsing"
git push origin main
```

### 2. Railway Auto-Deploy
- Railway will automatically detect changes
- Build will start automatically
- Check build logs for errors

### 3. Set Webhook
After deployment, set the Telegram webhook:
```bash
curl -X POST https://your-domain.railway.app/telegram/set-webhook/
```

Or visit in browser:
```
https://your-domain.railway.app/telegram/set-webhook/
```

### 4. Verify Services

**Check services are running:**
- Web service: `https://your-domain.railway.app/`
- Celery worker: Check Railway logs for "celery worker ready"
- Redis: Check Railway dashboard
- Postgres: Check Railway dashboard

### 5. Test Flow

Send test message to Telegram bot:
```
/start
```

Expected response:
```
Здравствуйте! Я Алексей, юрист АвтоЮрист...
```

### 6. Monitor Logs

In Railway dashboard:
1. Go to your service
2. Click "Deployments"
3. Click latest deployment
4. Watch logs in real-time

Look for:
- `=== TELEGRAM WEBHOOK RECEIVED ===`
- `Processing message through AI`
- `Email task queued for`
- No `[ERROR]` messages

## Common Issues & Solutions

### Issue: Worker failed to boot
**Cause:** Null bytes in Python files
**Solution:** Already fixed - `__init__.py` recreated

### Issue: Email not sending
**Cause:** Blocking SMTP calls
**Solution:** Already fixed - Using Celery async tasks

### Issue: Contract data not parsing
**Cause:** Weak regex patterns
**Solution:** Already fixed - Enhanced parsing with multiple strategies

### Issue: No logs visible
**Solution:** Set `DEBUG=True` in Railway environment

### Issue: Celery worker not starting
**Check:**
- REDIS_URL is set
- Celery service is running in Railway
- Check celery worker logs

## Services Architecture

```
┌─────────────┐
│   Client    │
│  (Telegram) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Web Server │ (Gunicorn, 2 workers)
│   Django    │
└──────┬──────┘
       │
       ├──────────────┐
       │              │
       ▼              ▼
┌─────────────┐  ┌─────────────┐
│  PostgreSQL │  │    Redis    │
│  (Database) │  │   (Broker)  │
└─────────────┘  └──────┬──────┘
                        │
                        ▼
                 ┌─────────────┐
                 │   Celery    │
                 │   Worker    │
                 │ (Async Jobs)│
                 └─────────────┘
```

## Performance Expectations

- **Response time:** < 3 seconds for AI responses
- **Email delivery:** < 10 seconds (async)
- **Contract generation:** < 5 seconds
- **Concurrent users:** Up to 50 simultaneous

## Monitoring

### Key Metrics to Watch
1. Response times in logs
2. Celery task success rate
3. Email delivery success rate
4. Error frequency
5. Memory usage (Railway dashboard)

### Health Check Endpoints
- Main: `https://your-domain.railway.app/`
- Webhook info: `https://your-domain.railway.app/telegram/webhook-info/`

## Rollback Plan

If deployment fails:
1. Check Railway logs for errors
2. Revert to previous deployment in Railway dashboard
3. Fix issues locally
4. Redeploy

## Post-Deployment

- [ ] Test full conversation flow
- [ ] Test contract generation
- [ ] Test email verification
- [ ] Monitor logs for 1 hour
- [ ] Check Celery task queue
- [ ] Verify no memory leaks

## Support

If issues persist:
1. Check `LOGGING_GUIDE.md` for log analysis
2. Check `AI_CONTRACT_PARSING_FIX.md` for parsing issues
3. Review Railway logs for specific errors
4. Check Celery worker logs separately

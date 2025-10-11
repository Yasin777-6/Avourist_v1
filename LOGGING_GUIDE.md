# Detailed Logging Configuration Guide

## Overview

Comprehensive logging has been enabled across the entire application to help debug issues in Railway deployment.

## What's Logged

### 1. **Django Core Logs**
- All HTTP requests and responses
- Database queries (when `DB_LOG_LEVEL=DEBUG`)
- Server startup and shutdown events
- Middleware processing

### 2. **Telegram Bot Logs** (`telegram_bot` app)
- Incoming webhook data (full JSON payload)
- User information (telegram_id, username, name)
- Message text received
- Response sent back to user
- Lead creation/update events

### 3. **AI Engine Logs** (`ai_engine` app)
- Message processing start/end
- Conversation history length
- DeepSeek API calls
- AI response received
- Command extraction and processing
- Contract generation triggers

### 4. **Contract Manager Logs** (`contract_manager` app)
- Contract generation requests
- Data parsing (pipe format and natural language)
- Template selection
- Document generation
- Email task queuing
- Verification code generation

### 5. **Celery Worker Logs**
- Task execution start/end
- Email sending attempts
- Retry attempts
- Task failures

### 6. **Gunicorn Logs**
- Worker startup/shutdown
- Access logs (all HTTP requests)
- Error logs
- Worker health status

## Log Format

```
[LEVEL] TIMESTAMP module.function:line - message
```

**Example:**
```
[INFO] 2025-10-11 13:45:23 telegram_bot views.post:23 - === TELEGRAM WEBHOOK RECEIVED ===
[DEBUG] 2025-10-11 13:45:23 ai_engine conversation.process_message:38 - Conversation history length: 5
[INFO] 2025-10-11 13:45:25 contract_manager services._send_code_via_email:357 - Email task queued for user@example.com
```

## Environment Variables for Log Control

Add these to your Railway environment variables or `.env` file:

### Basic Logging
```bash
# Django log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
DJANGO_LOG_LEVEL=INFO

# Database query logging (set to DEBUG to see all SQL queries)
DB_LOG_LEVEL=WARNING

# Enable debug mode (shows detailed error pages)
DEBUG=True
```

### Production Logging (Railway)
```bash
# Recommended for production
DJANGO_LOG_LEVEL=INFO
DB_LOG_LEVEL=WARNING
DEBUG=False
```

### Debug Logging (Development)
```bash
# Maximum verbosity for debugging
DJANGO_LOG_LEVEL=DEBUG
DB_LOG_LEVEL=DEBUG
DEBUG=True
```

## Viewing Logs in Railway

### 1. **Real-time Logs**
```bash
# In Railway dashboard, go to your service
# Click "Deployments" tab
# Click on the latest deployment
# Logs will stream in real-time
```

### 2. **Filter Logs by Level**
Look for these prefixes:
- `[DEBUG]` - Detailed debugging information
- `[INFO]` - General informational messages
- `[WARNING]` - Warning messages
- `[ERROR]` - Error messages
- `[CRITICAL]` - Critical errors

### 3. **Key Log Patterns to Search**

**Telegram Webhook:**
```
=== TELEGRAM WEBHOOK RECEIVED ===
```

**Contract Generation:**
```
Generating contract for lead
```

**Email Sending:**
```
Email task queued for
```

**AI Processing:**
```
Processing message from lead
```

**Errors:**
```
[ERROR]
```

## Gunicorn Access Logs

Every HTTP request is logged with:
- IP address
- Request method (GET, POST, etc.)
- URL path
- Response status code
- Response time

**Example:**
```
127.0.0.1 - - [11/Oct/2025:13:45:23 +0000] "POST /telegram/webhook/ HTTP/1.1" 200 15 "-" "TelegramBot"
```

## Celery Worker Logs

Celery tasks are logged separately. Look for:
```
[INFO] Task contract_manager.tasks.send_verification_email_task[abc-123] received
[INFO] Task contract_manager.tasks.send_verification_email_task[abc-123] succeeded in 2.5s
```

## Common Log Patterns

### Successful Flow
```
[INFO] === TELEGRAM WEBHOOK RECEIVED ===
[INFO] Message from 123456789 (@username): Hello
[INFO] Processing message through AI for lead 123456789
[DEBUG] Sending 3 messages to DeepSeek API
[INFO] AI response received: Здравствуйте...
[INFO] Found 1 commands in response: ['UPDATE_LEAD_STATUS']
[INFO] Sending response to Telegram: Здравствуйте...
[INFO] === WEBHOOK PROCESSED SUCCESSFULLY ===
```

### Contract Generation Flow
```
[INFO] Found 1 commands in response: ['GENERATE_CONTRACT']
[INFO] Generating contract for lead 123456789 with params: Иванов...
[INFO] Parsed pipe format successfully: {...}
[INFO] Contract generated: AV-20251011-ABC123
[INFO] Email task queued for user@example.com
```

### Error Flow
```
[ERROR] Webhook error: 'NoneType' object has no attribute 'get'
Traceback (most recent call last):
  File "telegram_bot/views.py", line 64, in post
    ...
```

## Troubleshooting with Logs

### Problem: No logs appearing
**Solution:** Check that `DEBUG=True` in Railway environment variables

### Problem: Too many logs
**Solution:** Set `DJANGO_LOG_LEVEL=WARNING` and `DB_LOG_LEVEL=ERROR`

### Problem: Can't find specific issue
**Solution:** Search logs for:
1. User's telegram_id
2. Contract number
3. Email address
4. Error timestamp

### Problem: Email not sending
**Look for:**
```
Email task queued for
Task contract_manager.tasks.send_verification_email_task
Failed to send email to
```

## Log Retention

Railway keeps logs for:
- **Free tier:** Last 7 days
- **Pro tier:** Last 30 days

Export important logs if needed for longer retention.

## Performance Impact

- **DEBUG level:** High verbosity, may impact performance
- **INFO level:** Balanced, recommended for production
- **WARNING level:** Minimal logging, only issues

## Files Modified

1. `autouristv1/settings.py` - Added LOGGING configuration
2. `docker-compose.yml` - Added gunicorn log flags
3. `DockerFile` - Added gunicorn log flags
4. `telegram_bot/views.py` - Added detailed logging
5. `ai_engine/services/conversation.py` - Added detailed logging
6. `contract_manager/services.py` - Already has logging
7. `contract_manager/tasks.py` - Already has logging

## Next Steps

1. Deploy to Railway
2. Trigger a test conversation
3. Check logs in Railway dashboard
4. Adjust log levels as needed

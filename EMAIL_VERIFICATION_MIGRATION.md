# Email Verification Migration - Complete

## ✅ What Was Changed

### 1. **Removed SMS Bot Integration**
   - ❌ Removed `SMS_BOT_TOKEN` from settings
   - ❌ Removed Telegram SMS bot message sending
   - ✅ Replaced with Gmail SMTP email sending

### 2. **Added Email Configuration**
   - **Backend**: `django.core.mail.backends.smtp.EmailBackend`
   - **Host**: `smtp.gmail.com`
   - **Port**: `587`
   - **TLS**: Enabled
   - **Email**: `naamatovichyasin@gmail.com`
   - **App Password**: `wgglgpbphxoycuat`

### 3. **Updated Services**
   - Renamed `SMSVerificationService` → `EmailVerificationService`
   - Added backward compatibility alias
   - Updated all messages to mention email instead of SMS

### 4. **Updated User Messages**
   - "SMS-код отправлен" → "Код подтверждения отправлен на вашу почту"
   - "Введите код из SMS" → "Введите код из email"
   - Added ✅ and ❌ emojis for better UX

## 📧 How It Works Now

```
User provides data
    ↓
Contract generated
    ↓
6-digit code generated
    ↓
Email sent to user's email address
    ↓
User receives email with code
    ↓
User enters code in Telegram
    ↓
Code verified
    ↓
Contract signed ✅
```

## 📝 Email Template

**Subject**: `Код подтверждения договора AV-YYYYMMDD-XXXXXXXX`

**Body**:
```
Здравствуйте!

Ваш код подтверждения договора: 123456

Код действителен 10 минут.

Введите этот код в Telegram-боте для подписания договора.

---
С уважением,
Команда АвтоЮрист
```

## ⚙️ Configuration Files Updated

### 1. `.env`
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=naamatovichyasin@gmail.com
EMAIL_HOST_PASSWORD=wgglgpbphxoycuat
DEFAULT_FROM_EMAIL=naamatovichyasin@gmail.com
```

### 2. `settings.py`
```python
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'naamatovichyasin@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
```

### 3. `contract_manager/services.py`
```python
class EmailVerificationService:
    """Service for handling email verification codes"""
    
    def generate_verification_code(self, contract: Contract):
        # Generate 6-digit code
        code = f"{random.randint(100000, 999999)}"
        
        # Send via email
        self._send_code_via_email(
            email=contract.lead.email,
            code=code,
            contract_number=contract.contract_number
        )
```

### 4. `ai_engine/services/contracts_flow.py`
```python
# New methods
def handle_email_code(self, lead):
    """Resend verification code via email"""
    
def handle_code_verification(self, lead, code: str):
    """Verify entered code"""

# Backward compatibility
handle_sms_code = handle_email_code
handle_sms_verification = handle_code_verification
```

## 🔐 Gmail App Password Setup

To use Gmail SMTP, you need an **App Password** (not your regular Gmail password):

1. Go to Google Account Settings
2. Security → 2-Step Verification (enable it)
3. App Passwords → Generate new
4. Select "Mail" and "Other (Custom name)"
5. Copy the 16-character password
6. Use it in `EMAIL_HOST_PASSWORD`

## 📊 Benefits

✅ **More Reliable** - Email delivery is more stable than Telegram bots  
✅ **Professional** - Users receive official emails  
✅ **No Extra Bot** - Don't need separate SMS bot  
✅ **Better Tracking** - Email logs for verification  
✅ **Spam Protection** - Gmail's built-in spam filtering  

## 🧪 Testing

To test email sending:

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject='Test Email',
    message='This is a test email from АвтоЮрист',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['test@example.com'],
    fail_silently=False,
)
```

## 🚨 Important Notes

1. **Email Required**: Users must provide email address for verification
2. **10 Minute Expiry**: Codes expire after 10 minutes
3. **One-Time Use**: Each code can only be used once
4. **Gmail Limits**: Gmail has sending limits (500 emails/day for free accounts)

## 🔄 Backward Compatibility

All old code using `SMSVerificationService` will continue to work:
- `SMSVerificationService` is now an alias for `EmailVerificationService`
- `handle_sms_code()` calls `handle_email_code()`
- `handle_sms_verification()` calls `handle_code_verification()`

## 📦 Files Modified

1. `.env` - Added email configuration
2. `autouristv1/settings.py` - Added EMAIL_* settings
3. `contract_manager/services.py` - Renamed service, added email sending
4. `ai_engine/services/contracts_flow.py` - Updated messages and methods

---

**Email verification system is now fully operational!** 📧✅

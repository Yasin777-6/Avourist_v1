"""
Test email sending configuration
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autouristv1.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("Testing email configuration...")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print()

try:
    send_mail(
        subject='Test Email from АвтоЮрист',
        message='This is a test email to verify the email configuration is working correctly.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.EMAIL_HOST_USER],  # Send to self for testing
        fail_silently=False,
    )
    print("✅ Email sent successfully!")
    print(f"Check inbox: {settings.EMAIL_HOST_USER}")
except Exception as e:
    print(f"❌ Email sending failed: {e}")

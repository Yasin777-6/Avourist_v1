from django.urls import path
from . import views

app_name = 'telegram_bot'

urlpatterns = [
    path('webhook/', views.TelegramWebhookView.as_view(), name='webhook'),
    path('set-webhook/', views.set_webhook, name='set_webhook'),
    path('webhook-info/', views.webhook_info, name='webhook_info'),
]

from django.contrib import admin
from .models import Lead, Conversation


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'first_name', 'last_name', 'email', 'status', 'case_type', 'region', 'created_at']
    list_filter = ['status', 'case_type', 'region', 'created_at']
    search_fields = ['telegram_id', 'first_name', 'last_name', 'username', 'email']
    readonly_fields = ['telegram_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('telegram_id', 'username', 'first_name', 'last_name', 'phone_number', 'email')
        }),
        ('Lead Classification', {
            'fields': ('status', 'case_type', 'region')
        }),
        ('Case Details', {
            'fields': ('case_description', 'estimated_cost', 'roi_calculation', 'win_probability')
        }),
        ('Assignment', {
            'fields': ('assigned_lawyer',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_interaction'),
            'classes': ('collapse',)
        })
    )


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['lead', 'message_type', 'created_at']
    list_filter = ['message_type', 'created_at']
    search_fields = ['lead__telegram_id', 'user_message', 'ai_response']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lead')

from django.contrib import admin
from .models import ContractTemplate, Contract, SMSVerification


@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'case_type', 'instance', 'representation_type', 'region', 'base_cost', 'is_active']
    list_filter = ['case_type', 'instance', 'representation_type', 'region', 'is_active']
    search_fields = ['name', 'template_file']
    readonly_fields = ['created_at']


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'lead', 'template', 'status', 'created_at']
    list_filter = ['status', 'template__case_type', 'template__region', 'created_at']
    search_fields = ['contract_number', 'lead__telegram_id', 'lead__first_name', 'lead__last_name']
    readonly_fields = ['contract_number', 'created_at', 'sent_at', 'signed_at']
    
    fieldsets = (
        ('Contract Info', {
            'fields': ('contract_number', 'lead', 'template', 'status')
        }),
        ('Legal Services', {
            'fields': ('case_description',),
            'description': 'Editable description of legal services to be provided in the contract'
        }),
        ('Client Data', {
            'fields': ('client_data',),
            'classes': ('collapse',)
        }),
        ('Files', {
            'fields': ('generated_pdf',)
        }),
        ('SMS Verification', {
            'fields': ('verification_code', 'code_sent_at', 'code_verified_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'sent_at', 'signed_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lead', 'template')


@admin.register(SMSVerification)
class SMSVerificationAdmin(admin.ModelAdmin):
    list_display = ['contract', 'telegram_id', 'verification_code', 'sent_at', 'is_used', 'is_expired_status']
    list_filter = ['is_used', 'sent_at']
    search_fields = ['contract__contract_number', 'telegram_id', 'verification_code']
    readonly_fields = ['sent_at', 'verified_at', 'expires_at']
    
    def is_expired_status(self, obj):
        return obj.is_expired()
    is_expired_status.boolean = True
    is_expired_status.short_description = 'Expired'

from django.db import models
from django.utils import timezone
from leads.models import Lead


class ContractTemplate(models.Model):
    """Contract templates for different case types and instances"""
    
    INSTANCE_CHOICES = [
        ('1', '1st Instance'),
        ('2', '2nd Instance'), 
        ('3', '3rd Instance'),
        ('4', '4th Instance'),
    ]
    
    REPRESENTATION_CHOICES = [
        ('WITHOUT_POA', 'Without Power of Attorney'),
        ('WITH_POA', 'With Power of Attorney'),
        ('NO_REPRESENTATION', 'Without Representation'),
        ('WITH_REPRESENTATION', 'With Court Representation'),
    ]
    
    name = models.CharField(max_length=200)
    case_type = models.CharField(max_length=20)  # Links to Lead.CASE_TYPE_CHOICES
    instance = models.CharField(max_length=1, choices=INSTANCE_CHOICES)
    representation_type = models.CharField(max_length=20, choices=REPRESENTATION_CHOICES)
    region = models.CharField(max_length=20)  # MOSCOW or REGIONS
    
    # File path to the PDF template
    template_file = models.CharField(max_length=500)
    
    # Pricing information
    base_cost = models.DecimalField(max_digits=10, decimal_places=2)
    success_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Template fields that need to be filled
    required_fields = models.JSONField(default=list)  # List of field names
    
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['case_type', 'instance', 'representation_type', 'region']
        
    def __str__(self):
        return f"{self.name} - {self.instance} inst. - {self.region}"


class Contract(models.Model):
    """Generated contracts for leads"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent to Client'),
        ('SMS_SENT', 'SMS Code Sent'),
        ('SIGNED', 'Signed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='contracts')
    template = models.ForeignKey(ContractTemplate, on_delete=models.CASCADE)
    
    # Contract details
    contract_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Client information filled in contract
    client_data = models.JSONField(default=dict)  # Stores all filled fields
    case_description = models.TextField(blank=True, null=True, help_text="Description of legal services to be provided")
    
    # Files
    generated_pdf = models.FileField(upload_to='contracts/generated/', blank=True, null=True)
    
    # SMS verification
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    code_sent_at = models.DateTimeField(blank=True, null=True)
    code_verified_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(blank=True, null=True)
    signed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Contract {self.contract_number} - {self.lead.telegram_id} - {self.status}"
    
    def generate_contract_number(self):
        """Generate unique contract number"""
        import uuid
        return f"AV-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"


class SMSVerification(models.Model):
    """SMS verification codes for contract signing"""
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='sms_verifications')
    telegram_id = models.BigIntegerField()
    verification_code = models.CharField(max_length=6)
    
    sent_at = models.DateTimeField(default=timezone.now)
    verified_at = models.DateTimeField(blank=True, null=True)
    is_used = models.BooleanField(default=False)
    
    # Expiry time (default 10 minutes)
    expires_at = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"SMS {self.verification_code} - {self.telegram_id}"

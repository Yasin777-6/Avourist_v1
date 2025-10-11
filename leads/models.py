from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Lead(models.Model):
    """Lead model for tracking potential clients"""
    
    STATUS_CHOICES = [
        ('HOT', 'Hot Lead'),
        ('WARM', 'Warm Lead'), 
        ('COLD', 'Cold Lead'),
        ('CONVERTED', 'Converted'),
        ('CONSULTATION', 'Consultation Only'),
        ('FOLLOW_UP', 'Follow-up Required'),
    ]
    
    CASE_TYPE_CHOICES = [
        ('DUI', 'DUI/Drunk Driving'),
        ('SPEEDING', 'Speeding Violation'),
        ('LICENSE_SUSPENSION', 'License Suspension'),
        ('ACCIDENT', 'Traffic Accident'),
        ('PARKING', 'Parking Violation'),
        ('OTHER', 'Other Traffic Violation'),
        ('CRIMINAL', 'Criminal Case (264.1 УК РФ)'),
    ]
    
    REGION_CHOICES = [
        ('MOSCOW', 'Moscow'),
        ('REGIONS', 'Other Regions'),
    ]
    
    # Basic Info
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    
    # Lead Classification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WARM')
    case_type = models.CharField(max_length=20, choices=CASE_TYPE_CHOICES, blank=True, null=True)
    region = models.CharField(max_length=20, choices=REGION_CHOICES, default='REGIONS')
    
    # Case Details
    case_description = models.TextField(blank=True, null=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    roi_calculation = models.TextField(blank=True, null=True)
    win_probability = models.IntegerField(blank=True, null=True, help_text="Percentage chance of winning")
    
    # Assignment
    assigned_lawyer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_interaction = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Lead {self.telegram_id} - {self.status} - {self.case_type or 'Unknown'}"


class Conversation(models.Model):
    """Store AI conversation history for each lead"""
    
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='conversations')
    message_id = models.CharField(max_length=100)
    user_message = models.TextField()
    ai_response = models.TextField()
    message_type = models.CharField(max_length=50, default='text')  # text, photo, document
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['created_at']
        
    def __str__(self):
        return f"Conversation {self.lead.telegram_id} - {self.created_at}"

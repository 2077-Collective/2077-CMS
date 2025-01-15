from django.db import models
from apps.common.models import BaseModel
from django.conf import settings
from django.utils import timezone

# Create your models here.
class Subscriber(BaseModel):
    email = models.EmailField(unique=True)    
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    beehiiv_id = models.CharField(max_length=255, blank=True, null=True)
    synced_to_beehiiv = models.BooleanField(default=False)
    sync_error = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.email

class Newsletter(BaseModel):
    """Model for storing newsletters."""
    subject = models.CharField(max_length=255)    
    content = models.TextField()
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_sent = models.DateTimeField(blank=True, null=True)    
    scheduled_send_time = models.DateTimeField(blank=True, null=True)
        
    def __str__(self):
        return self.subject
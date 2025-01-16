from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from apps.common.models import BaseModel
from .services import BeehiivService

class Subscriber(BaseModel):
    email = models.EmailField(unique=True)    
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

@receiver(post_save, sender=Subscriber)
def sync_subscriber_to_beehiiv(sender, instance, created, **kwargs):
    beehiiv = BeehiivService()
    
    try:
        if created:
            # New subscriber
            beehiiv.create_subscriber(instance.email, instance.is_active)
        else:
            # Updated subscriber
            beehiiv.update_subscriber_status(instance.email, instance.is_active)
    except Exception as e:
        # Log the error but don't prevent the save
        print(f"Failed to sync subscriber {instance.email} to Beehiiv: {str(e)}")

@receiver(post_delete, sender=Subscriber)
def delete_subscriber_from_beehiiv(sender, instance, **kwargs):
    beehiiv = BeehiivService()
    
    try:
        beehiiv.delete_subscriber(instance.email)
    except Exception as e:
        # Log the error but don't prevent the delete
        print(f"Failed to delete subscriber {instance.email} from Beehiiv: {str(e)}")

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
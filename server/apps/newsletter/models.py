from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.common.models import BaseModel
from .services import BeehiivService
import logging
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_beehiiv_service():
    return BeehiivService()

class Subscriber(BaseModel):
    email = models.EmailField(unique=True)    
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
@receiver(post_save, sender=Subscriber)
def sync_subscriber_to_beehiiv(sender, instance, created, **kwargs):
    beehiiv = get_beehiiv_service()
    
    try:
        if created:
            # New subscriber
            beehiiv.create_subscriber(instance.email, instance.is_active)
        else:
            # Updated subscriber
            beehiiv.update_subscriber_status(instance.email, instance.is_active)
    except Exception as e:
        logger.error("Failed to sync subscriber %s to Beehiiv: %s", instance.email, str(e))
        raise  # Re-raise the exception to trigger retry

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
@receiver(post_delete, sender=Subscriber)
def delete_subscriber_from_beehiiv(sender, instance, **kwargs):
    beehiiv = get_beehiiv_service()
    
    try:
        beehiiv.delete_subscriber(instance.email)
    except Exception as e:
        if 'not found' in str(e).lower():
            logger.warning("Subscriber %s not found in Beehiiv, skipping deletion", instance.email)
            return
        logger.error("Failed to delete subscriber %s from Beehiiv: %s", instance.email, str(e))
        raise  # Re-raise the exception to trigger retry

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
from celery import shared_task
from celery.exceptions import Retry
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html
from .models import Newsletter, Subscriber
from .services import BeehiivService
import logging
import time

logger = logging.getLogger(__name__)

@shared_task
def send_newsletter_via_email():
    """
    Send newsletters to active subscribers.
    """
    now = timezone.now()
    newsletters = Newsletter.objects.filter(scheduled_send_time__lte=now, is_sent=False)

    for newsletter in newsletters:
        subscribers = Subscriber.objects.filter(is_active=True)

        for subscriber in subscribers:
            try:
                unsubscribe_link = format_html(
                    '{}/newsletter/unsubscribe/{}/',
                    settings.SITE_URL, 
                    subscriber.email
                )
                
                content = newsletter.content.replace('{unsubscribe_link}', unsubscribe_link)
                
                send_mail(
                    subject=newsletter.subject,
                    message='',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.email],
                    html_message=content
                )               
                
            except Exception as e:
                logger.error(f"Error sending email to {subscriber.email}: {e}")

        newsletter.is_sent = True
        newsletter.last_sent = timezone.now()
        newsletter.save()

    subscriber_count = Subscriber.objects.filter(is_active=True).count()
    logger.info(f'Newsletter sent to {subscriber_count} subscribers')

@shared_task(bind=True, max_retries=3)
def sync_to_beehiiv_task(self, email: str):
    """
    Sync a subscriber to Beehiiv.
    """
    beehiiv = BeehiivService()
    try:
        response = beehiiv.create_subscriber(email, is_active=True)
        logger.info(f"Beehiiv API response for {email}: {response}")
    except ValueError as e:
        logger.warning(f"Beehiiv sync warning for {email}: {str(e)}")
    except Exception as e:
        logger.error(f"Error syncing {email} to Beehiiv: {str(e)}")
        raise self.retry(exc=e, countdown=60) from e
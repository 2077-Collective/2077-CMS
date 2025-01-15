from celery import shared_task
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from .models import Newsletter, Subscriber
from django.utils import timezone
from django.utils.html import format_html
import logging
from .beehiiv import BeehiivClient

logger = logging.getLogger(__name__)

@shared_task
def send_newsletter_via_email():
    now = timezone.now()
    # Get newsletters that need to be sent
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

        # Mark newsletter as sent
        newsletter.is_sent = True
        newsletter.last_sent = timezone.now()
        newsletter.save()

    # Return a success message
    subscriber_count = Subscriber.objects.filter(is_active=True).count()
    logger.info(f'Newsletter sent to {subscriber_count} subscribers')

@shared_task(bind=True, max_retries=3)
def sync_subscriber_to_beehiiv(self, subscriber_id):
    try:
        subscriber = Subscriber.objects.get(id=subscriber_id)
    except Subscriber.DoesNotExist:
        logger.error(f"Subscriber with id {subscriber_id} does not exist.")
        return

    if subscriber.synced_to_beehiiv:
        return

    try:
        client = BeehiivClient()
        response = client.create_subscriber(subscriber.email)
        
        subscriber.beehiiv_id = response.get('id')
        subscriber.synced_to_beehiiv = True
        subscriber.sync_error = None
        subscriber.save()
        
        logger.info(f"Successfully synced subscriber {subscriber.email} to Beehiiv")
        
    except Exception as e:
        logger.error(f"Failed to sync subscriber {subscriber_id} to Beehiiv: {str(e)}")
        if 'subscriber' in locals():
            subscriber.sync_error = str(e)
            subscriber.save()
        retry_countdown = 60 * (2 ** self.request.retries)
        raise self.retry(exc=e, countdown=retry_countdown) from e

@shared_task
def bulk_sync_subscribers_to_beehiiv():
    unsynced = Subscriber.objects.filter(
        is_active=True,
        synced_to_beehiiv=False
    )[:settings.BEEHIIV_SYNC_BATCH_SIZE]
    
    for subscriber in unsynced:
        sync_subscriber_to_beehiiv.delay(subscriber.id)
    
    return len(unsynced)

@shared_task
def retry_failed_beehiiv_syncs():
    failed_syncs = Subscriber.objects.filter(
        is_active=True,
        synced_to_beehiiv=False,
        sync_error__isnull=False
    )
    
    for subscriber in failed_syncs:
        sync_subscriber_to_beehiiv.delay(subscriber.id)
    
    return len(failed_syncs)
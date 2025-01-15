from celery import shared_task
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from .models import Newsletter, Subscriber
from django.utils import timezone
from django.utils.html import format_html

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
                print(f"Error sending email to {subscriber.email}: {e}")

        # Mark newsletter as sent
        newsletter.is_sent = True
        newsletter.last_sent = timezone.now()
        newsletter.save()

    # Return a success message
    subscriber_count = Subscriber.objects.filter(is_active=True).count()
    print(f'Newsletter sent to {subscriber_count} subscribers')
from __future__ import absolute_import, unicode_literals
import os
from django.conf import settings
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

# Ensure DJANGO_SETTINGS_MODULE is set
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    raise ValueError('DJANGO_SETTINGS_MODULE environment variable is not set')

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('DJANGO_SETTINGS_MODULE'))

app = Celery('core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Celery Beat schedule configuration
app.conf.beat_schedule = {
    'publish-scheduled-articles-every-minute': {
        'task': 'apps.research.tasks.publish_scheduled_articles',
        'schedule': crontab(minute='*/1'),
    },
    
    'send-scheduled-newsletter': {
        'task': 'apps.newsletter.tasks.send_newsletter_via_email',
        'schedule': crontab(minute='*/1'),
    },
    
    'sync-subscribers-to-beehiiv': {
        'task': 'apps.newsletter.tasks.bulk_sync_subscribers_to_beehiiv',
        'schedule': crontab(minute=0, hour='*/1'),
        'options': {'queue': 'beehiiv'}
    },
    
    'retry-failed-beehiiv-syncs': {
        'task': 'apps.newsletter.tasks.retry_failed_beehiiv_syncs',
        'schedule': crontab(minute=30, hour='*/6'),
        'options': {'queue': 'beehiiv'}
    },
}

@app.task(bind=True)
def debug_task(self):
    """Debug task to test the celery worker."""
    if settings.DEBUG:
        print(f'Request: {self.request!r}')
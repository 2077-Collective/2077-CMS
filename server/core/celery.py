from __future__ import absolute_import, unicode_literals
import os
from django.conf import settings
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('DJANGO_SETTINGS_MODULE', 'core.config.production'))

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
        'schedule': crontab(minute='*/1'),  # Runs every minute
    },
    
    'send-scheduled-newsletter': {
        'task': 'apps.newsletter.tasks.send_newsletter_via_email',
        'schedule': crontab(minute='*/1'),  # Runs every minute
    },
}

@app.task(bind=True)
def debug_task(self):
    """Debug task to test the celery worker."""
    if settings.DEBUG:
        print(f'Request: {self.request!r}')

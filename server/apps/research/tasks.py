from celery import shared_task
from django.utils import timezone
from django.db import transaction
from .models import Article
import logging

logger = logging.getLogger(__name__)

# TODO: Implement Querying the Articles in chunks in case of very large dataset
@shared_task(name='apps.research.tasks.publish_scheduled_articles')
def publish_scheduled_articles():
    """
    Update status of draft articles that have reached their scheduled publish time
    """
    try:
        with transaction.atomic():
            updated = Article.objects.filter(
                status='draft',
                scheduled_publish_time__isnull=False,
                scheduled_publish_time__lte=timezone.now()
            ).update(status='ready')
            
            if updated:
                logger.info(f"Updated {updated} articles to ready status")
            
            return updated
            
    except Exception as e:
        logger.error(f"Error publishing scheduled articles: {e}")
        raise
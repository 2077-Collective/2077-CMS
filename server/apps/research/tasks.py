from celery import shared_task
from django.utils import timezone
from .models import Article

# TODO: Implement Querying the Articles in chunks in case of very large dataset
@shared_task
def publish_scheduled_articles():
    """Publish articles that are scheduled to be published."""
    now = timezone.now()
    articles_to_publish = Article.objects.filter(status='draft', scheduled_publish_time__lte=now)
    articles_to_publish.update(status='ready')
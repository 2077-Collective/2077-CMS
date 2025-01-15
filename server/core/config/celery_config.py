# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Redis as a broker
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Task routing for Beehiiv
CELERY_TASK_ROUTES = {
    'apps.newsletter.tasks.sync_subscriber_to_beehiiv': {'queue': 'beehiiv'},
    'apps.newsletter.tasks.bulk_sync_subscribers_to_beehiiv': {'queue': 'beehiiv'},
    'apps.newsletter.tasks.retry_failed_beehiiv_syncs': {'queue': 'beehiiv'},
}

# Queue configurations
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_QUEUES = {
    'default': {},
    'beehiiv': {
        'rate_limit': '30/m'  # 30 requests per minute for Beehiiv API
    }
}

# Task execution settings
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_TASK_IGNORE_RESULT = True

# Rate limiting annotations
CELERY_TASK_ANNOTATIONS = {
    'apps.newsletter.tasks.sync_subscriber_to_beehiiv': {
        'rate_limit': '30/m'
    }
}
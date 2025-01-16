# beehiiv.py
from decouple import config
from django.core.exceptions import ImproperlyConfigured

# Beehiiv API Key
BEEHIIV_API_KEY = config('BEEHIIV_API_KEY', default='')
if not BEEHIIV_API_KEY:
    raise ImproperlyConfigured('BEEHIIV_API_KEY must be configured in environment variables or .env file.')

# Beehiiv Publication ID
BEEHIIV_PUBLICATION_ID = config('BEEHIIV_PUBLICATION_ID', default='')
if not BEEHIIV_PUBLICATION_ID:
    raise ImproperlyConfigured('BEEHIIV_PUBLICATION_ID must be configured in environment variables or .env file.')

# Beehiiv Configuration
BEEHIIV_CONFIG = {
    'API_KEY': BEEHIIV_API_KEY,
    'PUBLICATION_ID': BEEHIIV_PUBLICATION_ID,
}
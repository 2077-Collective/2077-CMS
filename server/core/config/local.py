from .base import *

MEDIA_URL = '/media/'

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://127.0.0.1:8001', #staging
    'http://localhost:8000',
    'http://localhost:4321',
]
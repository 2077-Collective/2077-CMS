"""
ASGI config for main2077cms project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Ensure DJANGO_SETTINGS_MODULE is set
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    raise ValueError('DJANGO_SETTINGS_MODULE environment variable is not set')

# Set the default Django settings module for the ASGI application.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('DJANGO_SETTINGS_MODULE'))

from django.core.asgi import get_asgi_application

application = get_asgi_application()
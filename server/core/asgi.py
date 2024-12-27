"""
ASGI config for main2077cms project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from dotenv import load_dotenv

load_dotenv()

from django.core.asgi import get_asgi_application

settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'core.config.production')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_asgi_application()
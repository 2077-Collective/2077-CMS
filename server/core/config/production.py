from .base import *

MEDIA_URL = 'https://cms.2077.xyz/media/'

DEBUG = bool(config('DJANGO_DEBUG', default=False))

ALLOWED_HOSTS = ['74.119.195.253', 'cms.2077.xyz']

CSRF_TRUSTED_ORIGINS = []
for host in ALLOWED_HOSTS:
    CSRF_TRUSTED_ORIGINS.append(f"https://{host}")
    CSRF_TRUSTED_ORIGINS.append(f"http://{host}")

CORS_ALLOWED_ORIGINS = [
    "https://cms.2077.xyz", # Https version of Django
    "http://74.119.195.253", # Http version of Astro
    "http://127.0.0.1:4321", # Local Dev
    "http://localhost:4321", # Local Dev
    ]

CORS_ALLOW_CREDENTIALS = True

#REDISCLOUD_URL = config("REDISCLOUD_URL")

STATIC_URL = 'staticfiles/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASS'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

CSP_DEFAULT_SRC = ("self",)

CSP_STYLE_SRC = ("self",)

CSP_SCRIPT_SRC = ("self",)

CSP_IMG_SRC = ("self", "http://cms.2077.xyz", "https://cms.2077.xyz", "http://74.119.195.253")

CSP_FONT_SRC = ("self",)

CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_HSTS_PRELOAD = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = True

#PROXY_SETTING for Astro server
PROXY_ASTERISK = True
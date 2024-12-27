from .base import *

# Development-specific settings
DEBUG = True

# Media settings
MEDIA_URL = '/media/'

# Development hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# CSRF settings for local development
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

CORS_ALLOW_CREDENTIALS = True

# Database settings (you might want to use SQLite for local development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='your_local_db_name'),
        'USER': config('DB_USER', default='your_local_db_user'),
        'PASSWORD': config('DB_PASS', default='your_local_db_password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Security settings appropriate for development
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Content Security Policy settings for development
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "blob:")
CSP_IMG_SRC = ("'self'", "blob:")
CSP_MEDIA_SRC = ("'self'", "blob:")
CSP_CONNECT_SRC = ("'self'", "blob:")
CSP_FONT_SRC = ("'self'",)

# Static files
STATIC_URL = 'static/'

# File upload settings
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB
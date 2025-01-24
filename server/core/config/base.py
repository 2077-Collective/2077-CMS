"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# cloudinary
import cloudinary
import cloudinary.uploader

# third party imports
from .celery_config import (CELERY_BROKER_URL, CELERY_RESULT_BACKEND, CELERY_ACCEPT_CONTENT, CELERY_TASK_SERIALIZER, CELERY_RESULT_SERIALIZER, CELERY_TIMEZONE)
from .mail import (SITE_URL, EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, DEFAULT_FROM_EMAIL, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_USE_SSL, EMAIL_BACKEND)

load_dotenv()
from decouple import config
from .cloudinary import CLOUDINARY_DOMAIN, CLOUDINARY_STORAGE
from .beehiiv import BEEHIIV_CONFIG
from .algolia import ALGOLIA

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
print(BASE_DIR)
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(config('DJANGO_DEBUG', default=True))

ALLOWED_HOSTS = ["*"]

# Application definition

DJANGO_APPS = [    
    'admin_interface',
    'colorfield',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.syndication',
    'rest_framework',
]

LOCAL_APPS = [
    'apps.common',
    'apps.research',
    'apps.newsletter',
]

THIRD_PARTY_APPS = [
    'corsheaders',
    'django_celery_beat',
    'tinymce',
    'cloudinary_storage',
    'cloudinary',
    'algoliasearch_django',   
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    "NON_FIELD_ERRORS_KEY": "error",

}
# Possible Permissions to explore based on use case
# 'rest_framework.permissions.AllowAny',
# 'rest_framework.permissions.IsAuthenticated',
# 'rest_framework.permissions.IsAdminUser',
# 'rest_framework.permissions.IsAuthenticatedOrReadOnly',

CORS_ALLOW_ALL_ORIGINS = True

# This needs be false when not CORS_ALLOW_ALL_ORIGINS = True
# If we need to allow credentials, we must specify the origin
CORS_ALLOW_CREDENTIALS = False

ROOT_URLCONF = 'core.urls'

# configured to serve static files
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # Tinymce Api Context
                'core.config.tinymce.tinymce_api_key',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True


USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SILENCED_SYSTEM_CHECKS = [
    "staticfiles.W004"
]

# django-admin-interface config
X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

# Tinymce API Config
TINYMCE_API_KEY = config('TINYMCE_API_KEY')

# OpenAI API Config
OPENAI_API_KEY = config('OPENAI_API_KEY', default=None)

# Beehiiv Settings
BEEHIIV_API_KEY = BEEHIIV_CONFIG['API_KEY']
BEEHIIV_PUBLICATION_ID = BEEHIIV_CONFIG['PUBLICATION_ID']

# Algolia
ALGOLIA = ALGOLIA
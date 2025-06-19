from .base import *

DEBUG = False

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


ALLOWED_HOSTS = []
# # Seguridad para producción
SECURE_HSTS_SECONDS = 3600
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

from .base import *

DEBUG = False

ALLOWED_HOSTS = ['tudominio.com']

# Seguridad para producción
SECURE_HSTS_SECONDS = 3600
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

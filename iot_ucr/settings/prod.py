from .base import *

DEBUG = False

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
# Para que Django detecte que detrás del proxy la petición fue HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Para que Django respete el Host que llega en el header
USE_X_FORWARDED_HOST = False

# Debes incluir aquí tu dominio con esquema, para que pase el check de CSRF
# Debes incluir aquí tu dominio con esquema, para que pase el check de CSRF
CSRF_TRUSTED_ORIGINS = [
    "https://iotlab201.eie.ucr.ac.cr/",
    # agrega aquí más orígenes si usas otros subdominios…
]


ALLOWED_HOSTS = ["iotlab201.eie.ucr.ac.cr", "127.0.0.1", "localhost"]
# # Seguridad para producción
SECURE_HSTS_SECONDS = 3600
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

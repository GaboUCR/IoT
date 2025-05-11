import os

from django.core.asgi import get_asgi_application
from channels.routing      import ProtocolTypeRouter, URLRouter
from channels.auth         import AuthMiddlewareStack

# Importa tus rutas WebSocket
from sensors.routing       import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iot_ucr.settings.dev')

# ASGI app para manejar HTTP
django_asgi_app = get_asgi_application()

# Este es tu ASGI application que maneja HTTP **y** WebSockets
application = ProtocolTypeRouter({
    # Manejo normal de HTTP
    "http": django_asgi_app,

    # Manejo de WebSocket con autenticación Django
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatsite.settings")
django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from chat.routing import websocket_urlpatterns

django_asgi_app = get_asgi_application()
# print("DJANGO_SETTINGS_MODULE:", os.getenv("DJANGO_SETTINGS_MODULE"))

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
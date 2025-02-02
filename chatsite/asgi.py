import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatsite.settings")
django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from django.core.asgi import get_asgi_application
from chat.routing import websocket_urlpatterns
import chat.consumers as consumers

django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
        "channel": ChannelNameRouter({
            'background-tasks': consumers.BackgroundTaskConsumer().as_asgi(),
        }), 
    }
)

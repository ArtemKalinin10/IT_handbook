from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

from education.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
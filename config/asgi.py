import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import apps.routing  # sizning websocket routelar joylashgan fayl

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            apps.routing.websocket_urlpatterns
        )
    ),
})

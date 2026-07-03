"""
ASGI config for CampusVisa project.

Supports HTTP and WebSocket protocols via Django Channels.
"""

import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from django.core.asgi import get_asgi_application  # noqa: E402

# Collect WebSocket URL patterns from app routing modules.
websocket_urlpatterns = []

try:
    from apps.chat.routing import websocket_urlpatterns as chat_ws
    websocket_urlpatterns += chat_ws
except ImportError:
    pass

try:
    from apps.notifications.routing import websocket_urlpatterns as notifications_ws
    websocket_urlpatterns += notifications_ws
except ImportError:
    pass

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})

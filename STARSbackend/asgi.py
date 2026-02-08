import os
from django.core.asgi import get_asgi_application

# 1. Set settings before importing anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'STARSbackend.settings')

# 2. Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from strawberry.channels.handlers.ws_handler import GraphQLWSConsumer
from STARS.graphql.schema import schema

# 3. Define the WebSocket routing explicitly
websocket_urlpatterns = [
    # Matches ws://yourdomain/graphql or ws://yourdomain/graphql/
    re_path(r"^graphql/?$", GraphQLWSConsumer.as_asgi(schema=schema)),
]

application = ProtocolTypeRouter({
    # 4. Standard HTTP requests go to Django
    "http": django_asgi_app,

    # 5. WebSocket requests go through Auth middleware, then URL routing
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
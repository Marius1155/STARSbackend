import os
from django.core.asgi import get_asgi_application

# Set the settings module BEFORE anything else.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "STARSbackend.settings")

# This call also helps initialize Django.
django_asgi_app = get_asgi_application()

# Now, import your Channels and Strawberry components.
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from strawberry.channels import GraphQLProtocolTypeRouter
from STARS.graphql.schema import schema

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        GraphQLProtocolTypeRouter(schema)
    ),
})
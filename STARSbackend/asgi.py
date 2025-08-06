import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from strawberry.channels import GraphQLProtocolTypeRouter
from STARS.graphql.schema import schema

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yourproject.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        GraphQLProtocolTypeRouter(schema)
    ),
})
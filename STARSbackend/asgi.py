import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "STARSbackend.settings")

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from strawberry.channels import GraphQLProtocolTypeRouter
from STARS.graphql.schema import schema

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        GraphQLProtocolTypeRouter(schema)
    ),
})
# STARSbackend/asgi.py

import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "STARSbackend.settings")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
# Add re_path to the imports
from django.urls import path, re_path
from strawberry.asgi import GraphQL
from STARS.graphql.schema import schema

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": URLRouter([
        path("graphql/", GraphQL(schema)),
        # Use re_path to create a "catch-all" for any other path.
        # This will correctly hand off requests for static files (or any
        # other Django URL) to the main Django app.
        re_path(r"", django_asgi_app),
    ]),
})
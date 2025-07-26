"""
ASGI config for STARSbackend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

# STARSbackend/asgi.py

import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "STARSbackend.settings")
django.setup()

# Now it's safe to import the rest
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from strawberry.asgi import GraphQL
from STARS.graphql.schema import schema

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": URLRouter([
        # Remove the optimizer_enabled argument from this line
        path("graphql/", GraphQL(schema)),

        path("", django_asgi_app),
    ]),
})
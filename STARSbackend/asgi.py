"""
ASGI config for STARSbackend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""
# STARSbackend/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from strawberry.django.views import GraphQL

# Corrected import path from your 'STARS' app
from STARS.graphql.schema import schema

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "STARSbackend.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": URLRouter([
        path("graphql/", GraphQL(schema, optimizer_enabled=True)),
        path("", django_asgi_app),
    ]),
})
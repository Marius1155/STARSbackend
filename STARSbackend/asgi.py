"""
ASGI config for STARSbackend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

# --- IMPORTANT ---
# Set the settings module and run django.setup() BEFORE importing any other
# components that might need the settings (like your schema or views).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "STARSbackend.settings")
django.setup()
# -----------------

# Now it's safe to import the rest
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from strawberry.asgi import GraphQL
from STARS.graphql.schema import schema

# This function can now be called safely
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": URLRouter([
        path("graphql/", GraphQL(schema, optimizer_enabled=True)),
        path("", django_asgi_app),
    ]),
})
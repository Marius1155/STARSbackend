# STARSbackend/asgi.py

# STARSbackend/asgi.py

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "STARSbackend.settings")
django.setup()

from django.core.asgi import get_asgi_application
from strawberry_django.views import AsyncGraphQLView
from STARS.graphql.schema import schema

# The main Django ASGI application will handle all routing.
# We will add the GraphQL path to our urls.py file instead.
application = get_asgi_application()
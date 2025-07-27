# STARSbackend/asgi.py
import os
import django
from django.core.asgi import get_asgi_application

# This block is the critical fix. It ensures everything is ready.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "STARSbackend.settings")
django.setup()

# Now that Django is set up, the rest of the application can be loaded safely.
application = get_asgi_application()
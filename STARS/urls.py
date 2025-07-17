# STARS/urls.py

from django.urls import path

# stars/urls.py
from django.urls import path
from .views import load_data_view

urlpatterns = [
    path('load-data/', load_data_view),  # TEMPORARY
]
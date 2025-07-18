# stars/views.py
from django.core.management import call_command
from django.http import HttpResponse
from django.conf import settings
import os

def load_data_view(request):
    json_path = os.path.join(settings.BASE_DIR, 'data.json')  # adjust filename if needed
    if os.path.exists(json_path):
        call_command('loaddata', json_path)
        return HttpResponse("Data loaded into the database.")
    else:
        return HttpResponse("data.json not found at expected path.", status=404)
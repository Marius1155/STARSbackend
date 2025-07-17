from django.shortcuts import render

# Create your views here.
# stars/views.py
from django.core.management import call_command
from django.http import HttpResponse

def load_data_view(request):
    call_command('loaddata', 'data.json')
    return HttpResponse("Data loaded into the database.")
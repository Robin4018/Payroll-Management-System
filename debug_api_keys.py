
import os
import django
import sys
import json

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth.models import User

# Get a user
user = User.objects.get(username='robin') # Admin user
client = APIClient()
client.force_authenticate(user=user)

response = client.get('/api/employees/')
if response.status_code == 200:
    data = response.json()
    if isinstance(data, list) and len(data) > 0:
        print("API Keys:", list(data[0].keys()))
        print("First Item Values:", {k: data[0][k] for k in ['id', 'first_name', 'last_name', 'employee_code'] if k in data[0]})
    elif isinstance(data, dict) and 'results' in data and len(data['results']) > 0:
        print("API Keys:", list(data['results'][0].keys()))
        print("First Item Values:", {k: data['results'][0][k] for k in ['id', 'first_name', 'last_name', 'employee_code'] if k in data['results'][0]})
else:
    print("Error:", response.status_code)

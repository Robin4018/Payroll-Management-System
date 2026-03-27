
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
    item = data[0] if isinstance(data, list) else data['results'][0]
    for k in item.keys():
        print(f"Key: {k}")
else:
    print("Error:", response.status_code)


import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()

from django.urls import resolve
from django.test import Client
from django.contrib.auth.models import User

try:
    path = '/api/consolidated-reports/'
    match = resolve(path)
    print(f"Path {path} resolves to: {match.func}")
except Exception as e:
    print(f"Resolve failed: {e}")

client = Client()
username = 'api_tester'
user, _ = User.objects.get_or_create(username=username, defaults={'is_superuser': True, 'is_staff': True})
client.force_login(user)

url = '/api/consolidated-reports/?type=master&month=2026-02&format=excel'
response = client.get(url)
print(f"Response status: {response.status_code}")
print(f"Response content: {response.content}")

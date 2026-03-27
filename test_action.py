
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()

from django.test import Client
from django.contrib.auth.models import User

client = Client()
username = 'api_tester'
user, _ = User.objects.get_or_create(username=username, defaults={'is_superuser': True, 'is_staff': True})
client.force_login(user)

url = '/api/payroll/consolidated-report/?type=master&month=2026-02&format=excel'
print(f"Testing Action URL: {url}")
response = client.get(url)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("SUCCESS!")
    print(response.json())
else:
    print(f"Content: {response.content}")


import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()

from django.test import Client

client = Client()
url = '/api/test-routing/'
response = client.get(url)
print(f"Sanity Check Status: {response.status_code}")
print(f"Content: {response.content}")

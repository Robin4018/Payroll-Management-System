
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()

from django.test import Client

client = Client()
url = '/api/v2/reports/?type=master&month=2026-02&format=excel'
print(f"Testing FBV URL: {url}")
response = client.get(url)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("SUCCESS!")
    print(response.json())
else:
    print(f"Content: {response.content}")

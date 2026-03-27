
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import resolve

client = Client()
user = User.objects.filter(is_superuser=True).first()
client.force_login(user)

url = '/api/payroll/consolidated-report/?type=master&month=2026-02&format=excel'
print(f"Verifying Final URL: {url}")
try:
    match = resolve(url)
    print(f"View mapping: {match.func}")
    response = client.get(url)
    print(f"Final Status: {response.status_code}")
    if response.status_code == 200:
        print("Architecture Verified: Success!")
        print(response.json())
except Exception as e:
    print(f"Verification Failed: {e}")

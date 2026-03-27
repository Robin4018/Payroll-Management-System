
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()

from payroll.views import PayrollLedgerViewSet
from django.urls import resolve

print(f"Has consolidated_report: {hasattr(PayrollLedgerViewSet, 'consolidated_report')}")

from django.test import Client
from django.contrib.auth.models import User
client = Client()
user = User.objects.filter(is_superuser=True).first()
client.force_login(user)

url = '/api/payroll/consolidated-report/'
try:
    match = resolve(url)
    print(f"Resolved {url} to {match.func}")
except Exception as e:
    print(f"Resolve failed for {url}: {e}")

response = client.get(url)
print(f"Status: {response.status_code}")

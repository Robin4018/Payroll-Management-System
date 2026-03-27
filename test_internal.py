import os
import sys
sys.path.append(os.getcwd())
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from payroll.models import PayrollLedger

client = Client()
user = User.objects.filter(is_superuser=True).first()
client.force_login(user)

from datetime import date
ledgers = PayrollLedger.objects.all()
print(f"Total Ledgers: {ledgers.count()}")
if ledgers.exists():
    l = ledgers.first()
    print(f"Ledger ID: {l.id}, Month: {l.month}")

url = "/api/payroll/consolidated-report/?type=monthly&month=2024-02&export_format=pdf"
res = client.get(url)
print("Status:", res.status_code)
if res.status_code == 500:
    print("500 Error detected")
else:
    print("Body:", res.content.decode()[:500])

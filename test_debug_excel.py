import os
import sys
sys.path.append(os.getcwd())
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from payroll.models import PayrollLedger
from payroll.utils import generate_payroll_excel

user = User.objects.filter(is_superuser=True).first()
from datetime import date
ledgers = PayrollLedger.objects.filter(month=date(2024, 2, 1))
print(f"Found {ledgers.count()} ledgers")

try:
    path = generate_payroll_excel(ledgers)
    print(f"Success: {path}")
except Exception as e:
    import traceback
    print("Caught Error in generate_payroll_excel:")
    traceback.print_exc()
    if ledgers.exists():
        l = ledgers.first()
        print(f"Ledger __dict__: {l.__dict__.keys()}")

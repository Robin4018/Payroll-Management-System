import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from payroll.models import PayrollLedger
from datetime import datetime

month_date = datetime(2026, 2, 1).date()
l = PayrollLedger.objects.filter(month__year=2026, month__month=2).first()
if l:
    print(f"Month field: {l.month}")
    print(f"Type: {type(l.month)}")
else:
    print("No ledger found for Feb 2026 using year/month filter")

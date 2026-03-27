import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from payroll.models import PayrollLedger
from datetime import datetime

month_date = datetime(2026, 2, 1).date()
ledgers = PayrollLedger.objects.filter(month=month_date)
print(f"Total ledgers for Feb 2026: {ledgers.count()}")
for l in ledgers:
    print(f"- {l.employee.first_name} {l.employee.last_name} (Tenant ID: {l.employee.tenant_id})")

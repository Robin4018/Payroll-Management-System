
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from payroll.models import PayrollLedger
from payroll.serializers import PayrollLedgerSerializer
import json

l = PayrollLedger.objects.filter(employee__employee_code='EMP0002', month='2026-02-01').first()
if l:
    data = PayrollLedgerSerializer(l).data
    print(json.dumps(data, indent=2))
else:
    print("Ledger for EMP0002 not found")

print("\n--- EMP0007 (Working) ---")
l7 = PayrollLedger.objects.filter(employee__employee_code='EMP0007', month='2026-02-01').first()
if l7:
    data7 = PayrollLedgerSerializer(l7).data
    print(json.dumps(data7, indent=2))

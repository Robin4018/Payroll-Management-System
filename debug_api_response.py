
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from payroll.models import PayrollLedger
from payroll.serializers import PayrollLedgerSerializer

print("API Response Debug:")
ledgers = PayrollLedger.objects.filter(month='2026-02-01').order_by('employee__employee_code')
for l in ledgers:
    data = PayrollLedgerSerializer(l).data
    bank = data.get('bank_details')
    bank_name = bank.get('bank_name') if bank else "MISSING"
    print(f"{l.employee.employee_code}: {l.employee.first_name} -> Bank: {bank_name}, Status: {l.status}")

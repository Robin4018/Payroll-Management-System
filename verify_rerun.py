
import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee
from payroll.services import PayrollCalculator
from payroll.models import PayrollLedger
from payroll.serializers import PayrollLedgerSerializer

e = Employee.objects.get(employee_code='EMP0002')
calc = PayrollCalculator(e.tenant)
d = date(2026, 2, 1)

print(f"Re-running payroll for {e.first_name} for {d}...")
ledger = calc.calculate_employee_salary(e, d)

print(f"Ledger ID: {ledger.id}")
serializer = PayrollLedgerSerializer(ledger)
data = serializer.data

print("Serialized Data (Bank Info):")
print(f"bank_details: {data.get('bank_details')}")
print(f"bank_name: {data.get('bank_name')}")
print(f"bank_account: {data.get('bank_account')}")

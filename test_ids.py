
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from payroll.models import PayrollLedger
from employees.models import Employee

print("Comparison Check:")
l = PayrollLedger.objects.filter(employee__employee_code='EMP0002', month='2026-02-01').first()
e = Employee.objects.get(employee_code='EMP0002')

print(f"Ledger Emp ID: {l.employee_id}")
print(f"Actual Emp ID: {e.id}")
print(f"Has bank_details on ledger.employee: {hasattr(l.employee, 'bank_details')}")
if hasattr(l.employee, 'bank_details'):
    print(f"Bank Name: {l.employee.bank_details.bank_name}")


import os
import django
from decimal import Decimal
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee
from payroll.services import PayrollCalculator
from payroll.models import PayrollLedger

e = Employee.objects.get(employee_code='EMP0002')
tenant = e.tenant
calc = PayrollCalculator(tenant)

print(f"Running payroll for {e.first_name} (EMP0002)...")
d = date(2026, 2, 1)
ledger = calc.calculate_employee_salary(e, d)

print(f"Result: Net Pay = {ledger.net_pay}")
print(f"Earnings: {ledger.calculations_breakdown['earnings']}")
print(f"Deductions (Structural): {ledger.calculations_breakdown.get('statutory', {})}")

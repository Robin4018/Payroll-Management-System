
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee
from payroll.models import PayrollLedger

codes = ['EMP0001', 'EMP0002', 'EMP0003', 'EMP0004', 'EMP0005', 'EMP0006', 'EMP0007']
print("Employee Bank Details Check:")
for code in codes:
    try:
        e = Employee.objects.get(employee_code=code)
        bank = e.bank_details.bank_name if hasattr(e, 'bank_details') else "None"
        print(f"{code}: {bank}")
    except Employee.DoesNotExist:
        print(f"{code}: Not Found")

print("\nPayroll Ledger Check (Feb 2026):")
ledger_recs = PayrollLedger.objects.filter(month='2026-02-01', employee__employee_code__in=codes)
for l in ledger_recs:
    print(f"{l.employee.employee_code}: Status={l.status}, Net={l.net_pay}, UTR={l.utr_number}")

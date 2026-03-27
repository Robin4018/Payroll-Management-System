
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee

print("Current Bank Details Repository:")
for e in Employee.objects.all().order_by('employee_code'):
    bank = "None"
    if hasattr(e, 'bank_details'):
        bank = f"{e.bank_details.bank_name} ({e.bank_details.account_number})"
    print(f"{e.employee_code}: {e.first_name} {e.last_name} -> {bank}")

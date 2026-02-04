
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from tenants.models import Tenant
from employees.models import Employee
from payroll.models import SalaryComponent

print("Tenants:")
for t in Tenant.objects.all():
    print(f"ID: {t.id}, Name: {t.name}, Type: {t.type}")

print("\nSalary Components:")
for c in SalaryComponent.objects.all():
    print(f"ID: {c.id}, Name: {c.name}, Tenant: {c.tenant_id}")

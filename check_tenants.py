
import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee
from tenants.models import Tenant
from django.db.models import Count

print("--- Employees per Tenant ---")
tenants = Tenant.objects.annotate(emp_count=Count('employees'))
for t in tenants:
    print(f"Tenant ID: {t.id}, Name: {t.name}, Count: {t.emp_count}")

from django.contrib.auth.models import User
print("\n--- Users and their Tenants ---")
for u in User.objects.all():
    tenant_name = "N/A"
    if hasattr(u, 'employee'):
        tenant_name = u.employee.tenant.name
    print(f"User: {u.username}, Tenant: {tenant_name}")

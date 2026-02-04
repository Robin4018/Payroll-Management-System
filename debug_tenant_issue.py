import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payroll_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from employees.models import Employee

User = get_user_model()

print("--- Debugging Tenant Resolution ---")

# 1. Check Tenants
tenants = Tenant.objects.all()
print(f"Total Tenants: {tenants.count()}")
for t in tenants:
    print(f"Tenant: ID={t.id}, Name={t.name}, Type={t.type}")

# 2. Check User 'robin'
try:
    robin = User.objects.get(username='robin')
    print(f"\nUser 'robin' found. ID={robin.id}, Superuser={robin.is_superuser}")
    
    if hasattr(robin, 'employee'):
        emp = robin.employee
        print(f"Linked Employee: {emp}")
        if emp.tenant:
            print(f"Employee Tenant: ID={emp.tenant.id}, Name={emp.tenant.name}")
        else:
            print("Employee has NO Tenant linked.")
    else:
        print("User 'robin' has NO Employee record.")

    # Simulate View Logic
    tenant_id = None
    if hasattr(robin, 'employee') and robin.employee.tenant:
        tenant_id = robin.employee.tenant.id
        print(f"Logic Path A: Found from Employee -> {tenant_id}")
    else:
        fallback = Tenant.objects.filter(type='EDUCATION').first() or Tenant.objects.first()
        if fallback:
            tenant_id = fallback.id
            print(f"Logic Path B: Fallback -> {tenant_id}")
        else:
            print("Logic Path C: No Tenant found at all.")

except User.DoesNotExist:
    print("User 'robin' not found.")

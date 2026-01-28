
import os
import django
import sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee
from tenants.models import Tenant

# Check all users
print("=== All Users ===")
users = User.objects.all()
for u in users:
    print(f"Username: {u.username}, Email: {u.email}, Is Staff: {u.is_staff}, Is Superuser: {u.is_superuser}")
    emp = Employee.objects.filter(user=u).first()
    if emp:
        print(f"  -> Has Employee: {emp.first_name} {emp.last_name} (Tenant: {emp.tenant})")
    else:
        print(f"  -> No Employee record")
    print()

# Check tenants
print("\n=== All Tenants ===")
tenants = Tenant.objects.all()
for t in tenants:
    print(f"Tenant: {t.name} (Type: {t.type})")
    emp_count = Employee.objects.filter(tenant=t).count()
    print(f"  -> Employees: {emp_count}")

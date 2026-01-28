
import os
import django
import sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee, Department
from tenants.models import Tenant

# Get the robin user
user = User.objects.filter(username='robin').first()
if not user:
    print("Error: robin user not found")
    exit(1)

# Get the tenant with employees (should be the college)
tenants = Tenant.objects.all()
tenant = None
for t in tenants:
    emp_count = Employee.objects.filter(tenant=t).count()
    print(f"Tenant: {t.name}, Employees: {emp_count}")
    if emp_count > 0:
        tenant = t
        break

if not tenant:
    # Fallback to first tenant
    tenant = Tenant.objects.first()
    
if not tenant:
    print("Error: No tenant found")
    exit(1)

print(f"\nUsing Tenant: {tenant.name}")
print(f"User: {user.username}")

# Check if employee already exists
existing_emp = Employee.objects.filter(user=user).first()
if existing_emp:
    print(f"Employee already exists: {existing_emp}")
    print(f"  Tenant: {existing_emp.tenant}")
    exit(0)

# Get a department (any department will do for admin)
dept = Department.objects.filter(tenant=tenant).first()

# Create employee record for robin
emp = Employee.objects.create(
    user=user,
    tenant=tenant,
    first_name="Robin",
    last_name="Admin",
    email=user.email if user.email else "robin.admin@college.edu",
    phone="9999999999",
    department=dept,
    designation="System Administrator",
    employment_type='PERMANENT',
    date_of_joining='2024-01-01'
)

print(f"\nCreated employee record:")
print(f"  ID: {emp.employee_code}")
print(f"  Name: {emp.first_name} {emp.last_name}")
print(f"  Email: {emp.email}")
print(f"  Tenant: {emp.tenant}")
print(f"  Department: {emp.department}")
print("\n✓ Dashboard should now work! Please refresh the page.")

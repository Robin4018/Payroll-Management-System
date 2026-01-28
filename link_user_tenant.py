import os
import django
import sys
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.getcwd())
django.setup()

from django.contrib.auth import get_user_model
from employees.models import Employee
from tenants.models import Tenant

User = get_user_model()

def link_user():
    # 1. Get User
    try:
        user = User.objects.get(username='robin')
        print(f"Found User: {user.username}")
    except User.DoesNotExist:
        print("User 'robin' not found!")
        return

    # 2. Get Tenant
    # Assuming we want the Education tenant
    tenant = Tenant.objects.filter(type='EDUCATION').first()
    if not tenant:
        print("No Education Tenant found!")
        return
    print(f"Found Tenant: {tenant.name} ({tenant.type})")

    # 3. Check if link exists
    if hasattr(user, 'employee'):
        emp = user.employee
        print(f"User {user.username} is linked to Employee: {emp}")
        print(f"  -> Employee Tenant: {emp.tenant if emp.tenant else 'NONE'}")
        if emp.tenant:
            print(f"  -> Tenant Type: {emp.tenant.type}")
        
        # Check if we should update it
        if not emp.tenant or emp.tenant.type != 'EDUCATION':
            print("WARNING: Tenant is missing or not EDUCATION type.")
            # Optional: Uncomment to force update
            # emp.tenant = tenant
            # emp.save()
            # print("UPDATED tenant to Education.")

    else:
        print("Creating new Employee profile...")
        emp = Employee(
            user=user,
            tenant=tenant,
            first_name='College',
            last_name='Admin',
            email='admin@college.com',  # Dummy email
            phone='9999999999',
            date_of_joining=date.today(),
            designation='Administrator', # Fallback field
            employment_type='PERMANENT'
        )
        emp.save()
        print(f"Successfully linked {user.username} to {tenant.name}. Employee Code: {emp.employee_code}")

if __name__ == '__main__':
    link_user()

import os
import django
import sys
from django.db import transaction

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee, UserProfile
from django.contrib.auth.models import User
from tenants.models import Tenant

def create_staff_logins():
    employees = Employee.objects.filter(user__isnull=True)
    created_count = 0
    
    print(f"Found {employees.count()} employees without login credentials.")
    
    # Check if we have tenants to determine type
    # For this script, we'll try to guess based on tenant type or default to COLLEGE
    
    for emp in employees:
        try:
            with transaction.atomic():
                # 1. Create User
                username = emp.email
                if User.objects.filter(username=username).exists():
                    print(f"Skipping {emp.email}: User already exists with this username.")
                    continue
                
                # Default password
                password = "Welcome@123"
                
                user = User.objects.create_user(
                    username=username,
                    email=emp.email,
                    password=password,
                    first_name=emp.first_name,
                    last_name=emp.last_name
                )
                
                # 2. Link User to Employee
                emp.user = user
                emp.save()
                
                # 3. Create UserProfile
                # Determine Org Type
                org_type = 'COLLEGE' # Default
                if emp.tenant.type == 'CORPORATE':
                    org_type = 'COMPANY'
                elif emp.tenant.type == 'EDUCATION':
                    # Heuristic: if name contains School, SCHOOL, else COLLEGE
                    if 'school' in emp.tenant.name.lower():
                        org_type = 'SCHOOL'
                    else:
                        org_type = 'COLLEGE'
                
                UserProfile.objects.create(
                    user=user,
                    organization_type=org_type,
                    organization_name=emp.tenant.name
                )
                
                created_count += 1
                if created_count % 10 == 0:
                    print(f"Created {created_count} logins...")

        except Exception as e:
            print(f"Error creating login for {emp.email}: {str(e)}")

    print(f"\nSuccessfully created {created_count} staff logins.")
    print("Default Password for all: Welcome@123")
    
    # Print a few examples
    print("\n--- Example Credentials ---")
    for emp in Employee.objects.filter(user__isnull=False).order_by('-id')[:5]:
        print(f"User: {emp.first_name} {emp.last_name}")
        print(f"Email/Username: {emp.email}")
        print(f"Password: Welcome@123")
        print("-" * 30)

if __name__ == "__main__":
    create_staff_logins()

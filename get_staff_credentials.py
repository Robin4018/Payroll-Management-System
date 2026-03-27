import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee

print("=" * 60)
print("STAFF LOGIN CREDENTIALS")
print("=" * 60)

# Get employees with user accounts
employees_with_login = Employee.objects.filter(user__isnull=False).order_by('first_name')[:10]

if employees_with_login.exists():
    print(f"\nFound {employees_with_login.count()} staff members with login credentials:\n")
    
    for i, emp in enumerate(employees_with_login, 1):
        print(f"{i}. {emp.first_name} {emp.last_name}")
        print(f"   Email/Username: {emp.email}")
        print(f"   Password: Welcome@123")
        dept_name = emp.department.name if emp.department else 'N/A'
        desig_name = emp.designation_fk.name if emp.designation_fk else (emp.designation or 'N/A')
        print(f"   Department: {dept_name}")
        print(f"   Designation: {desig_name}")
        print("-" * 60)
else:
    print("\n❌ No staff members have login credentials yet.")
    print("Run: python create_staff_logins.py")

print("\n" + "=" * 60)
print("ADMIN LOGIN CREDENTIALS")
print("=" * 60)
print("Username: robin")
print("Password: robin 2003")
print("=" * 60)

print("\n📝 TESTING INSTRUCTIONS:")
print("1. Clear browser cache (Ctrl+Shift+R)")
print("2. Go to: http://127.0.0.1:8000/")
print("3. Login with any staff email above")
print("4. You should be redirected to: /dashboard/staff/")
print("\n✅ If you see the staff dashboard, restoration is successful!")

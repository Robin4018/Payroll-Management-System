import os
import django
import sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee
from django.contrib.auth.models import User

print("\n" + "="*70)
print("CHECKING STAFF LOGIN STATUS")
print("="*70)

# Check total employees
total_employees = Employee.objects.count()
employees_with_user = Employee.objects.filter(user__isnull=False).count()

print(f"\nTotal Employees: {total_employees}")
print(f"Employees with Login: {employees_with_user}")

if employees_with_user == 0:
    print("\n❌ NO STAFF LOGINS EXIST!")
    print("Run: python create_staff_logins.py")
else:
    print(f"\n✅ {employees_with_user} staff members have login credentials")
    
    # Show first 3 examples
    print("\n" + "="*70)
    print("SAMPLE STAFF CREDENTIALS (First 3):")
    print("="*70)
    
    for emp in Employee.objects.filter(user__isnull=False)[:3]:
        print(f"\nName: {emp.first_name} {emp.last_name}")
        print(f"Email: {emp.email}")
        print(f"Username: {emp.user.username}")
        print(f"Has Password: {emp.user.has_usable_password()}")
        print(f"Is Active: {emp.user.is_active}")
        print("-"*70)

print("\n" + "="*70)
print("ADMIN CREDENTIALS:")
print("="*70)
print("Username: robin")
print("Password: robin 2003")
print("="*70)

print("\n📝 TO TEST:")
print("1. Go to: http://127.0.0.1:8000/")
print("2. Login with staff email above")
print("3. Password: Welcome@123")
print("4. Should redirect to /dashboard/staff/")

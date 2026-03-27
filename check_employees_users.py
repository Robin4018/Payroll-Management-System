import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee
from django.contrib.auth.models import User

def check_employees():
    employees = Employee.objects.all()
    total_employees = employees.count()
    employees_with_user = employees.filter(user__isnull=False).count()
    employees_without_user = employees.filter(user__isnull=True).count()
    
    print(f"Total Employees: {total_employees}")
    print(f"Employees with User account: {employees_with_user}")
    print(f"Employees WITHOUT User account: {employees_without_user}")
    
    if employees_without_user > 0:
        print("\n--- Example Employees without User ---")
        for emp in employees.filter(user__isnull=True)[:5]:
            print(f"ID: {emp.id}, Name: {emp.first_name} {emp.last_name}, Email: {emp.email}")

if __name__ == "__main__":
    check_employees()

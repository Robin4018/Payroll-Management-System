import os
import django
import sys

# Add the project directory to sys.path
sys.path.append(r'd:\Project\Payroll Management System\universal-payroll-system')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee

active_count = Employee.objects.filter(is_active=True).count()
total_count = Employee.objects.all().count()

print(f"Total Employees: {total_count}")
print(f"Active Employees: {active_count}")

for emp in Employee.objects.filter(is_active=True)[:10]:
    print(f"ID: {emp.id}, Code: {emp.employee_code}, Name: {emp.first_name} {emp.last_name}, Active: {emp.is_active}")

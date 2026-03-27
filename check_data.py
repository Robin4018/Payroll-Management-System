
import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee

print("--- First 5 Employees ---")
for emp in Employee.objects.all()[:5]:
    print(f"ID: {emp.id}, First: '{emp.first_name}', Last: '{emp.last_name}', Code: '{emp.employee_code}'")

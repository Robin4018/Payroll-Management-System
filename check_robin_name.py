
import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee
try:
    emp = Employee.objects.get(id=224)
    print(f"ID: {emp.id}, First: '{emp.first_name}', Last: '{emp.last_name}'")
except:
    print("Employee 224 not found")

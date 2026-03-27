
import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee

print("--- Searching for Choose Employee ---")
for emp in Employee.objects.filter(first_name__icontains='Choose'):
    print(f"ID: {emp.id}, Name: {emp.first_name} {emp.last_name}")
for emp in Employee.objects.filter(last_name__icontains='Choose'):
    print(f"ID: {emp.id}, Name: {emp.first_name} {emp.last_name}")

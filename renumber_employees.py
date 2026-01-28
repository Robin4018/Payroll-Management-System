
import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee
from tenants.models import Tenant

def renumber_employees():
    tenant = Tenant.objects.first()
    if not tenant:
        print("Error: No tenant found.")
        return

    # Get all employees ordered by creation date
    employees = Employee.objects.filter(tenant=tenant).order_by('created_at', 'id')
    
    print(f"Found {employees.count()} employees to renumber...")
    
    # Temporarily set all to unique temp codes to avoid conflicts
    print("Step 1: Setting temporary codes...")
    for emp in employees:
        emp.employee_code = f"TEMP{emp.id}"
        emp.save()
    
    # Now renumber from 1
    print("Step 2: Renumbering from EMP0001...")
    employees = Employee.objects.filter(tenant=tenant).order_by('created_at', 'id')
    for idx, emp in enumerate(employees, start=1):
        new_code = f"EMP{idx:04d}"
        emp.employee_code = new_code
        emp.save()
        print(f"  {emp.first_name} {emp.last_name}: {new_code}")
    
    print(f"\nSuccessfully renumbered {employees.count()} employees!")

if __name__ == "__main__":
    renumber_employees()

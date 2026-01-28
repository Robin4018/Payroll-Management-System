import os
import django
import sys
from django.db.models import Count

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.getcwd())
django.setup()

from employees.models import Employee
from tenants.models import Tenant

def count_employees():
    print("--- Employee Counts by Tenant ---")
    total_global = Employee.objects.count()
    print(f"Total: {total_global}")
    
    counts = Employee.objects.all().values('tenant__name').annotate(count=Count('id'))
    for c in counts:
        t_name = c['tenant__name'] or "None"
        print(f"Tenant: '{t_name}' = {c['count']}")
        
    print("\n--- Unlinked Employees ---")
    unlinked = Employee.objects.filter(tenant__isnull=True).count()
    print(f"Employees with NO Tenant: {unlinked}")

if __name__ == '__main__':
    count_employees()

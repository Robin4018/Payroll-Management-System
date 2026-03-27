import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from employees.models import Employee
for emp in Employee.objects.all():
    print(f"Emp: {emp.first_name} {emp.last_name}, Email: {emp.email}, User: {emp.user.username if emp.user else 'NONE'}, Tenant: {emp.tenant.name if emp.tenant else 'NONE'}")

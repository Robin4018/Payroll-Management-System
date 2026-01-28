
import os
import django
import sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee

# Check admin user
u = User.objects.filter(username='robin').first()
print(f'Admin user: {u}')
print(f'Has employee attr: {hasattr(u, "employee")}')

# Check employee record
emp = Employee.objects.filter(user=u).first() if u else None
print(f'Employee record: {emp}')

if emp:
    print(f'Employee tenant: {emp.tenant}')
    print(f'Employee name: {emp.first_name} {emp.last_name}')
else:
    print('No employee record linked to admin user!')

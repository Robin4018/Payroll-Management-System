import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from django.contrib.auth.models import User
from employees.models import Employee

users = User.objects.all()[:10]
for u in users:
    print(f"User: {u.username}")
    if hasattr(u, 'employee'):
        print(f"  Tenant ID: {u.employee.tenant_id}")
    else:
        print("  No employee profile")

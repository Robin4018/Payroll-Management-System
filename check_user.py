import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from django.contrib.auth.models import User
from employees.models import Employee

try:
    user = User.objects.get(username='college_admin') # Or search for any admin
    print(f"User: {user.username}")
    if hasattr(user, 'employee'):
        print(f"Employee Tenant ID: {user.employee.tenant_id}")
    else:
        print("User has no employee profile")
except User.DoesNotExist:
    # Try to find any user with 'admin' in name
    admins = User.objects.filter(username__icontains='admin')
    for a in admins:
        print(f"Found user: {a.username}")
        if hasattr(a, 'employee'):
            print(f"  Employee Tenant ID: {a.employee.tenant_id}")
        else:
             print("  No employee profile")

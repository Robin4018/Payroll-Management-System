import os, django, sys
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from django.contrib.auth.models import User
from employees.models import Employee
from employees.models import UserProfile

try:
    u = User.objects.get(username='mr-g-paul-suthan@example.com')
    print(f"User: {u.username}")
    print(f"Has Employee: {hasattr(u, 'employee')}")
    if hasattr(u, 'employee'):
        print(f"Employee Name: {u.employee.first_name} {u.employee.last_name}")
    
    print(f"Has UserProfile: {hasattr(u, 'profile')}")
    if hasattr(u, 'profile'):
        print(f"Org Type: {u.profile.organization_type}")
except Exception as e:
    print(f"Error: {e}")

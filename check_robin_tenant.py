
import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
u = User.objects.get(username='robin')
print(f"User: {u.username}")
if hasattr(u, 'employee'):
    print(f"  Employee ID: {u.employee.id}")
    print(f"  Tenant: {u.employee.tenant.name} (ID: {u.employee.tenant.id})")
else:
    print("  No linked Employee record.")

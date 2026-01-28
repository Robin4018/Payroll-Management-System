import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.getcwd())
django.setup()

from django.contrib.auth import get_user_model
from employees.models import Employee

User = get_user_model()

def diagnose():
    print("--- User Diagnosis ---")
    users = User.objects.all()
    for u in users:
        emp = getattr(u, 'employee', None)
        tenant = emp.tenant if emp else None
        print(f"User: {u.username} (Superuser: {u.is_superuser})")
        print(f"  -> Employee: {emp}")
        print(f"  -> Tenant: {tenant}")
        if not emp:
            print("  -> WARNING: No Employee Record linked!")

if __name__ == '__main__':
    diagnose()

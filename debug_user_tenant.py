import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import sys
sys.path.append(os.getcwd())
django.setup()

from django.contrib.auth import get_user_model
from employees.models import Employee
# from authentication.models import Tenant - Wait, authentication might be the app name but the model is in tenants?
# The error was "No module named 'authentication'". 
# The script had `from authentication.models import Tenant`.
# Let's check where Tenant model is.

from tenants.models import Tenant

User = get_user_model()

print("--- USERS ---")
for u in User.objects.all():
    emp = getattr(u, 'employee', None)
    tenant = emp.tenant if emp else None
    print(f"User: {u.username} | Employee: {emp} | Tenant: {tenant}")

print("--- TENANTS ---")
for t in Tenant.objects.all():
    print(f"ID: {t.id} | Name: {t.name} | Type: {t.type}")



import os
import django
import sys
import datetime

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee
from tenants.models import Tenant
from django.contrib.auth.models import User

# Ensure a tenant exists
tenant, _ = Tenant.objects.get_or_create(name="Test Tenant", type='CORPORATE')

# Create a test employee without code
try:
    emp = Employee.objects.create(
        tenant=tenant,
        first_name="Auto",
        last_name="Gen",
        email=f"autogen{datetime.datetime.now().timestamp()}@test.com",
        phone="1234567890",
        date_of_joining=datetime.date.today()
    )
    print(f"SUCCESS: Created Employee. Code: {emp.employee_code}")
    
    # Create another to verify sequence
    emp2 = Employee.objects.create(
        tenant=tenant,
        first_name="Auto2",
        last_name="Gen2",
        email=f"autogen2{datetime.datetime.now().timestamp()}@test.com",
        phone="1234567890",
        date_of_joining=datetime.date.today()
    )
    print(f"SUCCESS: Created Employee 2. Code: {emp2.employee_code}")

except Exception as e:
    print(f"FAILED: {e}")

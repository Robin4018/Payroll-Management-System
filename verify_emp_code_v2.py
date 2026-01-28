
import os
import django
import sys
import datetime

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
try:
    django.setup()
    print("Django setup complete.")
except Exception as e:
    print(f"Django setup failed: {e}")
    sys.exit(1)

from employees.models import Employee
from tenants.models import Tenant

def run():
    print("Finding tenant...")
    tenant = Tenant.objects.first()
    if not tenant:
        print("Creating tenant...")
        tenant = Tenant.objects.create(name="Test Tenant 2", subdomain="test2", schema_name="test2", email="test2@example.com", phone="000")
    
    print(f"Using tenant: {tenant}")

    try:
        print("Creating employee 1...")
        emp = Employee.objects.create(
            tenant=tenant,
            first_name="Auto",
            last_name="Gen",
            email=f"autogen{datetime.datetime.now().timestamp()}@test.com",
            phone="1234567890",
            date_of_joining=datetime.date.today()
        )
        print(f"SUCCESS 1: {emp.employee_code}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FAILED 1: {e}")

if __name__ == "__main__":
    run()

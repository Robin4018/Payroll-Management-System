import os
import django
import json
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee
from django.contrib.auth import get_user_model

User = get_user_model()

def test_full_flow():
    # 1. Login
    session = requests.Session()
    login_url = 'http://127.0.0.1:8000/api/login/'  # Assuming this exists or using session login
    # Wait, api_login_view is at /api/login/ ? Need to check urls.py but usually yes.
    # Actually, let's just use the logic from the view directly to get a token if we can't hit the valid URL from here 
    # (since the server is running, we SHOULD hit the URL).
    
    # Let's try to authenticate manually first to get tokens
    user = User.objects.get(username='robin') # Adjust if needed
    print(f"Testing as User: {user.username}")
    
    # 2. Get Employee to update
    # Logic in view:
    # if hasattr(request.user, 'employee') and request.user.employee.tenant:
    #     employees = Employee.objects.filter(tenant=request.user.employee.tenant)
    # elif request.user.is_superuser:
    #     tenant = Tenant.objects.filter(type='EDUCATION').first() or Tenant.objects.first()
    #     employees = Employee.objects.filter(tenant=tenant)
        
    # Let's see what the view SEES
    if hasattr(user, 'employee') and user.employee.tenant:
        target_employees = Employee.objects.filter(tenant=user.employee.tenant)
        print(f"User bound to tenant: {user.employee.tenant}")
    elif user.is_superuser:
        from tenants.models import Tenant
        tenant = Tenant.objects.filter(type='EDUCATION').first() or Tenant.objects.first()
        target_employees = Employee.objects.filter(tenant=tenant)
        print(f"Superuser fallback to tenant: {tenant}")
    else:
        target_employees = Employee.objects.all()
        print("No tenant binding. All employees.")

    if not target_employees.exists():
        print("CRITICAL: No employees found for this user context!")
        return

    emp = target_employees.first()
    print(f"Target Employee: {emp.id} - {emp.first_name}")

    # 3. Simulate Payload
    # Status: HOLIDAY, Times: None
    updates = [{
        "employee": emp.id,
        "date": "2023-11-05", # Arbitrary date
        "status": "HOLIDAY",
        "check_in": None,
        "check_out": None
    }]
    
    print(f"Payload: {json.dumps(updates, indent=2)}")

    # 4. Perform Request
    # We need to authenticate. Since we are running local script, we can mock the request or use Client
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_authenticate(user=user)
    
    response = client.post(
        '/api/attendance/mark_attendance/',
        updates,
        format='json'
    )
    
    print(f"Response Code: {response.status_code}")
    print(f"Response Data: {response.data}")

    if response.status_code != 200:
        print("FAILED: API Error")
        return

    # 5. Verify DB
    from attendance.models import Attendance
    att = Attendance.objects.get(employee=emp, date="2023-11-05")
    print(f"DB Record: Status={att.status}, In={att.check_in}, Out={att.check_out}")
    
    if att.status == 'HOLIDAY' and att.check_in is None:
        print("SUCCESS: Full flow verification passed.")
    else:
        print("FAILURE: DB does not match payload.")

if __name__ == "__main__":
    test_full_flow()

import os
import django
import json
import sys

# Add project root to path
sys.path.append(os.getcwd())

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
try:
    django.setup()
except Exception as e:
    print(f"Setup failed: {e}")
    sys.exit(1)

from django.test import RequestFactory
from attendance.views import AttendanceViewSet
from attendance.models import Attendance
from employees.models import Employee

# Get an employee
emp = Employee.objects.first()
if not emp:
    print("No employees found")
    sys.exit(1)

print(f"Testing with Employee: {emp.first_name} {emp.last_name} ({emp.id})")

# Prepare Data
data = [
    {
        "employee": emp.id,
        "date": "2026-01-24",
        "status": "HOLIDAY",
        "check_in": "09:00",
        "check_out": "17:00"
    }
]

print("Sending Request...")
# Create Request
factory = RequestFactory()
request = factory.post(
    '/api/attendance/mark_attendance/',
    data=json.dumps(data),
    content_type='application/json'
)

# Call View
try:
    view = AttendanceViewSet.as_view({'post': 'mark_attendance'})
    response = view(request)

    print(f"Response Code: {response.status_code}")
    print(f"Response Data: {response.data}")
except Exception as e:
    print(f"View Error: {e}")

# Check DB
att = Attendance.objects.filter(employee=emp, date="2026-01-24").first()
if att:
    print(f"DB Record Found: Status={att.status}, In={att.check_in}, ID={att.id}")
else:
    print("Record NOT found in DB")

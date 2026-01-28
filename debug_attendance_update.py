import os
import django
import json
import sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

try:
    django.setup()
except Exception as e:
    print(f"Setup failed: {e}")
    sys.exit(1)

from rest_framework.test import APIRequestFactory
from attendance.views import AttendanceViewSet
from attendance.models import Attendance
from employees.models import Employee

# 1. Setup Data
emp = Employee.objects.first()
if not emp:
    print("No employees found")
    sys.exit(1)

date_str = "2026-02-01" # Future date to avoid conflicts

# Ensure clean slate
Attendance.objects.filter(employee=emp, date=date_str).delete()

# 2. Create Initial Record (e.g. Present)
init_att = Attendance.objects.create(
    employee=emp,
    date=date_str,
    status='PRESENT',
    check_in='09:00',
    check_out='17:00'
)
print(f"Created Initial Record: ID={init_att.id}, Status={init_att.status}")

# 3. Simulate Update Request (Set to HOLIDAY)
# Note: The view logic finds the existing record and calls serializer(instance, data=item, partial=True)
data = [
    {
        "employee": emp.id,
        "date": date_str,
        "status": "HOLIDAY",
        "check_in": "00:00",
        "check_out": "00:00"
    }
]

print("\n--- Sending Update Request ---")
factory = APIRequestFactory()
request = factory.post(
    '/api/attendance/mark_attendance/',
    data=data,
    format='json'
)

# Call View
try:
    view = AttendanceViewSet.as_view({'post': 'mark_attendance'})
    response = view(request)

    print(f"Response Code: {response.status_code}")
    print(f"Response Data: {response.data}")
except Exception as e:
    print(f"View Error: {e}")

# 4. Verify DB
final_att = Attendance.objects.get(id=init_att.id)
print(f"\nFinal DB Record: Status={final_att.status}")

if final_att.status == 'HOLIDAY':
    print("SUCCESS: Update persisted.")
else:
    print("FAILURE: Update did not persist.")

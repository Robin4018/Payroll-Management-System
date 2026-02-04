import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from attendance.models import Attendance, Employee
from rest_framework.test import APIRequestFactory
from attendance.views import AttendanceViewSet

def test_save_holiday():
    employee = Employee.objects.first()
    if not employee:
        print("No employee found")
        return

    print(f"Testing with Employee: {employee} (ID: {employee.id})")
    
    # Payload simulating 'Mark Holiday' -> Save
    payload = [{
        "employee": employee.id,
        "date": "2023-11-01",
        "status": "HOLIDAY",
        "check_in": None,
        "check_out": None
    }]
    
    factory = APIRequestFactory()
    request = factory.post('/api/attendance/mark_attendance/', payload, format='json')
    view = AttendanceViewSet.as_view({'post': 'mark_attendance'})
    
    response = view(request)
    print(f"API Response Code: {response.status_code}")
    print(f"API Response Data: {response.data}")
    
    # Verify DB
    att = Attendance.objects.filter(employee=employee, date="2023-11-01").first()
    if att:
        print(f"DB Record -> Status: {att.status}, CheckIn: {att.check_in}, CheckOut: {att.check_out}")
        if att.status == 'HOLIDAY' and att.check_in is None:
            print("SUCCESS: Record updated correctly.")
        else:
            print("FAILURE: Record mismatch.")
    else:
        print("FAILURE: Record not found in DB.")

if __name__ == "__main__":
    test_save_holiday()

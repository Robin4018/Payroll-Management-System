import os
import django
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from attendance.models import Attendance
from employees.models import Employee
from django.contrib.auth.models import User
from django.utils import timezone

def test_attendance_api():
    print("Testing Attendance models and query logic...")
    emp = Employee.objects.first()
    if not emp:
        print("No employees found in DB to test with.")
        return
    
    today = timezone.now().date()
    print(f"Testing for Employee: {emp}, Date: {today}")
    
    # Check if we can create/update
    attendance, created = Attendance.objects.update_or_create(
        employee=emp,
        date=today,
        defaults={'status': 'PRESENT'}
    )
    print(f"Attendance recorded: {attendance.status}, Created: {created}")
    
    # Test filtering logic from views
    qs = Attendance.objects.filter(employee=emp, date=today)
    print(f"Queryset count: {qs.count()}")
    
    month = today.month
    year = today.year
    presence_count = Attendance.objects.filter(
        employee=emp,
        date__month=month,
        date__year=year,
        status='PRESENT'
    ).count()
    print(f"Presence count for month {month}: {presence_count}")

if __name__ == "__main__":
    test_attendance_api()

import os
import sys
import django
from decimal import Decimal
from datetime import date, time

# Add project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from tenants.models import Tenant
from employees.models import Employee
from payroll.models import PayrollAdjustment
from attendance.models import Attendance
from payroll.services import PayrollCalculator
from django.contrib.auth.models import User

def test_bonus_calculation():
    print("Setting up test data...")
    tenant, _ = Tenant.objects.get_or_create(
        name="Test Bonus Tenant",
        defaults={'email': 'bonus_test@example.com'}
    )
    
    username = "test_bonus_user"
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        if hasattr(user, 'employee'):
             user.employee.delete()
    else:
        user = User.objects.create(username=username)
    
    employee = Employee.objects.create(
        user=user,
        tenant=tenant,
        first_name="Bonus",
        last_name="Earner",
        email="bonus.earner@example.com",
        date_of_joining=date(2023, 1, 1),
        designation="Star Performer"
    )

    # 1. Setup Attendance (Perfect Attendance - NO ABSENT records)
    # We don't even need to create PRESENT records for this specific logic, 
    # as it checks for EXISTENCE of ABSENT records.
    # But let's create one PRESENT record to be realistic.
    
    test_date = date.today().replace(day=1) 
    Attendance.objects.create(
        employee=employee,
        date=test_date,
        status='PRESENT'
    )
    print("Attendance Created: 1 Day Present, 0 Absent.")

    # 2. Run Payroll
    print("Running Payroll Calculation...")
    calc = PayrollCalculator(tenant)
    calc.calculate_employee_salary(employee, test_date)
    
    # 3. Verify Bonus Adjustment
    adjustments = PayrollAdjustment.objects.filter(
        employee=employee, 
        month__year=test_date.year, 
        month__month=test_date.month,
        type='BONUS',
        is_auto_generated=True
    )
    
    if adjustments.exists():
        adj = adjustments.first()
        print(f"SUCCESS: Auto-generated Bonus found: {adj.amount}")
        if adj.amount == Decimal('1000.00'):
            print("Amount matches expected ₹1000.")
        else:
            print(f"Amount mismatch. Got {adj.amount}")
    else:
        print("FAILURE: No auto-generated Bonus found.")

    # 4. Negative Test: Mark Absent and Re-run
    print("\nRunning Negative Test (Adding 1 Absent Day)...")
    Attendance.objects.create(
        employee=employee,
        date=test_date.replace(day=2),
        status='ABSENT'
    )
    
    calc.calculate_employee_salary(employee, test_date)
    
    adjustments = PayrollAdjustment.objects.filter(
        employee=employee, 
        month__year=test_date.year, 
        month__month=test_date.month,
        type='BONUS',
        is_auto_generated=True
    )
    
    if not adjustments.exists():
        print("SUCCESS: Bonus correctly removed/not awarded due to absenteeism.")
    else:
        print(f"FAILURE: Bonus still exists despite absenteeism! {adjustments.first().amount}")

if __name__ == "__main__":
    test_bonus_calculation()

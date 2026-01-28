import os
import django
import sys
from decimal import Decimal
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.getcwd())
django.setup()

from tenants.models import Tenant
from employees.models import Employee, Department
from payroll.models import SalaryComponent, EmployeeSalaryStructure, PayrollLedger
from attendance.models import Attendance, LeaveRequest, LeaveType
from payroll.services import PayrollCalculator

def verify_leave_logic():
    print("--- Verifying Leave & LOP Logic ---")
    
    # 1. Setup Tenant & Employee
    tenant = Tenant.objects.filter(type='EDUCATION').first() or Tenant.objects.first()
    if not tenant:
        print("ERROR: No tenant found.")
        return

    # Cleanup previous test data
    Employee.objects.filter(first_name="Leave", last_name="Tester").delete()
    
    emp = Employee.objects.create(
        tenant=tenant,
        first_name="Leave",
        last_name="Tester",
        email="leave.tester@test.com",
        phone="1234567890",
        date_of_joining=date(2023, 1, 1), # Joined last year
        employment_type='PERMANENT'
    )
    print(f"Created Employee: {emp}")

    # 2. Setup Salary Structure
    # Ensure Basic Component exists
    basic_comp, _ = SalaryComponent.objects.get_or_create(
        tenant=tenant, 
        name="Basic Salary",
        defaults={
            'type': SalaryComponent.ComponentType.EARNING,
            'calculation_type': SalaryComponent.CalculationType.FLAT,
            'is_taxable': True
        }
    )
    
    EmployeeSalaryStructure.objects.create(
        employee=emp,
        component=basic_comp,
        amount=Decimal('26000.00') # 1000 per day (assuming 26 days)
    )
    print("Set Salary: Basic = 26000")

    # 3. Add Attendance
    # Scenario: Jan 2024. 
    # Working Days = 26 (Hardcoded in service for now)
    # Absent Dates: Jan 2, Jan 3. 
    # Leave Request: Jan 3 (Paid).
    # expected LOP: 1 day (Jan 2).
    
    Attendance.objects.create(employee=emp, date=date(2024, 1, 2), status=Attendance.Status.ABSENT)
    Attendance.objects.create(employee=emp, date=date(2024, 1, 3), status=Attendance.Status.ABSENT)
    Attendance.objects.create(employee=emp, date=date(2024, 1, 4), status=Attendance.Status.PRESENT)
    print("Added Attendance: 2 Absent, 1 Present")

    # 4. Add Leave Request (Paid)
    sick_leave, _ = LeaveType.objects.get_or_create(
        tenant=tenant,
        name="Sick Leave",
        defaults={'is_paid': True, 'max_days_allowed': 10}
    )
    
    LeaveRequest.objects.create(
        employee=emp,
        start_date=date(2024, 1, 3),
        end_date=date(2024, 1, 3),
        leave_type=sick_leave,
        status=LeaveRequest.Status.APPROVED,
        reason="Fever"
    )
    print("Added Approved Paid Leave for Jan 3")

    # 5. Run Payroll
    calculator = PayrollCalculator(tenant)
    month = date(2024, 1, 1)
    
    print("\nRunning Payroll for Jan 2024...")
    ledger = calculator.calculate_employee_salary(emp, month)
    
    # 6. Verify Results
    print("\n--- Results ---")
    print(f"Total Earnings: {ledger.total_earnings}")
    print(f"Total Deductions: {ledger.total_deductions}")
    print(f"Net Pay: {ledger.net_pay}")
    
    breakdown = ledger.calculations_breakdown
    lop_data = breakdown.get('lop', {})
    print(f"LOP Days: {lop_data.get('days')}")
    print(f"LOP Amount: {lop_data.get('amount')}")
    
    # Assertions
    expected_lop_days = 1.0
    expected_lop_amount = 1000.00 # 26000 / 26 * 1
    
    # Allow some floating point tolerance if needed, but Decimal should be precise
    # Note: Logic in service: daily_salary = earnings / 26
    
    if float(lop_data.get('days')) == expected_lop_days:
        print("PASS: LOP Days Check")
    else:
        print(f"FAIL: LOP Days Expected {expected_lop_days}, Got {lop_data.get('days')}")

    if abs(float(lop_data.get('amount')) - expected_lop_amount) < 1.0:
        print("PASS: LOP Amount Check")
    else:
        print(f"FAIL: LOP Amount Expected {expected_lop_amount}, Got {lop_data.get('amount')}")

    # Check Statutory (PF might be calcualted automatically)
    print(f"PF Amount: {ledger.pf_amount}")
    
    # Cleanup
    # emp.delete() # Optional, keep for inspection if needed

if __name__ == '__main__':
    verify_leave_logic()

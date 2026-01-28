import os
import sys
import django
from decimal import Decimal
from datetime import date, time, timedelta

# Add project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from tenants.models import Tenant
from employees.models import Employee
from payroll.models import SalaryComponent, EmployeeSalaryStructure, PayrollAdjustment
from attendance.models import Attendance
from payroll.services import PayrollCalculator
from django.contrib.auth.models import User

def test_overtime_calculation():
    print("Setting up test data...")
    tenant, _ = Tenant.objects.get_or_create(
        name="Test OT Tenant",
        defaults={'email': 'ot_test@example.com'}
    )
    
    username = "test_ot_user"
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        if hasattr(user, 'employee'):
             user.employee.delete()
    else:
        user = User.objects.create(username=username)
    
    employee = Employee.objects.create(
        user=user,
        tenant=tenant,
        first_name="OT",
        last_name="Tester",
        date_of_joining=date(2023, 1, 1),
        designation="Tester"
    )

    # 1. Setup Salary Structure
    # Basic = 10000, DA = 5000 -> Total 15000.
    # Hourly Rate = 15000 / 26 / 8 = 72.11
    # OT Rate = 72.11 * 1.5 = 108.17 per hour
    
    basic_comp, _ = SalaryComponent.objects.get_or_create(
        tenant=tenant, name="Basic Salary", 
        defaults={'type': 'EARNING', 'calculation_type': 'FLAT_AMOUNT'}
    )
    da_comp, _ = SalaryComponent.objects.get_or_create(
        tenant=tenant, name="Dearness Allowance", 
        defaults={'type': 'EARNING', 'calculation_type': 'FLAT_AMOUNT'}
    )
    
    EmployeeSalaryStructure.objects.create(employee=employee, component=basic_comp, amount=10000)
    EmployeeSalaryStructure.objects.create(employee=employee, component=da_comp, amount=5000)
    
    print("Salary Structure Created.")

    # 2. Setup Attendance (1 Day with 12 Hours work)
    # 9 AM to 9 PM = 12 Hours.
    # OT = 12 - 9 = 3 Hours.
    # Expected OT Amount = 3 * 108.17 = 324.51 (approx)
    
    test_date = date.today().replace(day=1) # 1st of current month
    Attendance.objects.create(
        employee=employee,
        date=test_date,
        status='PRESENT',
        check_in=time(9, 0),
        check_out=time(21, 0) # 12 hours
    )
    print(f"Attendance Created: {test_date} 9AM-9PM (12 Hours)")

    # 3. Run Payroll
    print("Running Payroll Calculation...")
    calc = PayrollCalculator(tenant)
    ledger = calc.calculate_employee_salary(employee, test_date)
    
    # 4. Verify Adjustment
    adjustments = PayrollAdjustment.objects.filter(
        employee=employee, 
        month__year=test_date.year, 
        month__month=test_date.month,
        type='OVERTIME',
        is_auto_generated=True
    )
    
    if adjustments.exists():
        adj = adjustments.first()
        print(f"SUCCESS: Auto-generated Adjustment found: {adj.amount}")
        print(f"Description: {adj.description}")
        
        # Verify amount logic
        # 15000 / 26 / 8 = 72.11538...
        # * 1.5 = 108.173...
        # * 3 = 324.519... -> 324.52
        expected = Decimal('324.52')
        if abs(adj.amount - expected) < Decimal('1.00'):
            print("Amount matches expected range.")
        else:
            print(f"Amount mismatch. Expected ~{expected}, Got {adj.amount}")
    else:
        print("FAILURE: No auto-generated OT adjustment found.")

    # 5. Verify Ledger
    # Gross Earnings should be Basic + DA + OT = 15000 + 324.52 = 15324.52
    print(f"Ledger Earnings: {ledger.total_earnings}")
    
    if ledger.total_earnings > 15000:
        print("SUCCESS: Ledger reflects increased earnings.")
    else:
        print("FAILURE: Ledger earnings do not include OT.")

if __name__ == "__main__":
    test_overtime_calculation()

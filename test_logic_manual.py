import os
import django
from datetime import date
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from tenants.models import Tenant
from employees.models import Employee
from payroll.models import SalaryComponent, EmployeeSalaryStructure, PayrollLedger
from payroll.services import PayrollCalculator

def run_test():
    print("Setting up test data...")
    # Clean up
    EmployeeSalaryStructure.objects.all().delete()
    PayrollLedger.objects.all().delete()
    Employee.objects.all().delete()
    SalaryComponent.objects.all().delete()
    Tenant.objects.all().delete()

    # 1. Create Tenant
    tenant = Tenant.objects.create(name="Test Corp", type="CORPORATE")
    
    # 2. Create Components
    basic = SalaryComponent.objects.create(
        tenant=tenant, 
        name="Basic", 
        type="EARNING", 
        calculation_type="FLAT"
    )
    hra = SalaryComponent.objects.create(
        tenant=tenant, 
        name="HRA", 
        type="EARNING", 
        calculation_type="FORMULA",
        formula="Basic * 0.40"
    )
    pf = SalaryComponent.objects.create(
        tenant=tenant, 
        name="PF", 
        type="DEDUCTION", 
        calculation_type="FORMULA",
        formula="Basic * 0.12"
    )
    
    # 3. Create Employee
    employee = Employee.objects.create(
        tenant=tenant,
        first_name="Test",
        last_name="User",
        email="test@example.com",
        date_of_joining=date(2023, 1, 1),
        employee_code="E001"
    )
    
    # 4. Assign Structure (Basic = 10000)
    EmployeeSalaryStructure.objects.create(employee=employee, component=basic, amount=10000)
    EmployeeSalaryStructure.objects.create(employee=employee, component=hra)
    EmployeeSalaryStructure.objects.create(employee=employee, component=pf)

    print("Running calculation...")
    calculator = PayrollCalculator(tenant)
    ledgers = calculator.run_payroll_for_tenant(date(2023, 10, 1))
    
    if not ledgers:
        print("FAIL: No ledgers generated")
        return

    ledger = ledgers[0]
    
    print(f"Earnings: {ledger.total_earnings}, Deductions: {ledger.total_deductions}, Net: {ledger.net_pay}")

    assert ledger.total_earnings == Decimal('14000.00'), f"Expected 14000.00, got {ledger.total_earnings}"
    assert ledger.total_deductions == Decimal('1200.00'), f"Expected 1200.00, got {ledger.total_deductions}"
    assert ledger.net_pay == Decimal('12800.00'), f"Expected 12800.00, got {ledger.net_pay}"
    
    print("\nSUCCESS: Manual Logic Test Passed!")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"\nERROR: {e}")

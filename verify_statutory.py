import os
import django
import sys
from decimal import Decimal
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.getcwd())
django.setup()

from tenants.models import Tenant
from employees.models import Employee
from payroll.models import SalaryComponent, EmployeeSalaryStructure
from payroll.services import PayrollCalculator
from compliance.models import StatutoryRate

def verify_statutory():
    print("--- Verifying Statutory Deductions ---")
    
    tenant = Tenant.objects.filter(type='EDUCATION').first() or Tenant.objects.first()
    
    # ensure components exist
    basic_comp, _ = SalaryComponent.objects.get_or_create(
        tenant=tenant, 
        name="Basic Salary",
        defaults={'type': SalaryComponent.ComponentType.EARNING, 'calculation_type': SalaryComponent.CalculationType.FLAT}
    )
    hra_comp, _ = SalaryComponent.objects.get_or_create(
        tenant=tenant, 
        name="HRA",
        defaults={'type': SalaryComponent.ComponentType.EARNING, 'calculation_type': SalaryComponent.CalculationType.FLAT}
    )

    # Scenarios to Test
    scenarios = [
        {
            "name": "Scenario A (High Salary - EPF Only)",
            "basic": 25000, "hra": 10000, "gross": 35000,
            "expected_pf": 3000, # 12% of 25000
            "expected_esi": 0,   # > 21000
        },
        {
            "name": "Scenario B (Low Salary - EPF + ESI)",
            "basic": 10000, "hra": 5000, "gross": 15000,
            "expected_pf": 1200, # 12% of 10000
            "expected_esi": 113, # 0.75% of 15000 = 112.5 -> 113
        }
    ]

    calc = PayrollCalculator(tenant)

    for sc in scenarios:
        print(f"\nTesting {sc['name']}...")
        
        # Cleanup
        Employee.objects.filter(email=f"test.{sc['name'].split()[1].lower()}@test.com").delete()
        
        emp = Employee.objects.create(
            tenant=tenant,
            first_name="Test", last_name=sc['name'].split()[1],
            email=f"test.{sc['name'].split()[1].lower()}@test.com",
            phone="9999999999",
            date_of_joining=date(2023, 1, 1),
            employment_type='PERMANENT'
        )
        
        # Structure
        EmployeeSalaryStructure.objects.create(employee=emp, component=basic_comp, amount=sc['basic'])
        EmployeeSalaryStructure.objects.create(employee=emp, component=hra_comp, amount=sc['hra'])
        
        # Run Payroll (Jan - Not PT month usually)
        ledger = calc.calculate_employee_salary(emp, date(2024, 1, 1))
        
        print(f"  Gross: {ledger.total_earnings}")
        print(f"  PF: {ledger.pf_amount} (Expected: {sc['expected_pf']})")
        print(f"  ESI: {ledger.esi_amount} (Expected: {sc['expected_esi']}")
        
        if float(ledger.pf_amount) == sc['expected_pf']:
            print("  ✅ PF Correct")
        else:
            print(f"  ❌ PF Mismatch: Got {ledger.pf_amount}")

        if float(ledger.esi_amount) == sc['expected_esi']:
            print("  ✅ ESI Correct")
        else:
            print(f"  ❌ ESI Mismatch: Got {ledger.esi_amount}")
            
    # PT Scenario (Sept run)
    print("\nTesting Scenario C (PT Deduction in Sept)...")
    emp = Employee.objects.filter(email__contains="high").first() # Reuse High Salary
    if emp:
        # High Salary Gross = 35000. 
        # Half Yearly = 35000 * 6 = 210,000. 
        # Slab > 75000 -> 1250 PT.
        
        ledger_sept = calc.calculate_employee_salary(emp, date(2024, 9, 1))
        print(f"  Month: Sept, PT: {ledger_sept.pt_amount}")
        
        if float(ledger_sept.pt_amount) == 1250:
             print("  ✅ PT Correct (1250)")
        else:
             print(f"  ❌ PT Mismatch: Got {ledger_sept.pt_amount}, Expected 1250")

if __name__ == '__main__':
    verify_statutory()

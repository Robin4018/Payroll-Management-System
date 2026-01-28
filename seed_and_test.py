import os
import django
import sys

# Setup Django Environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from tenants.models import Tenant
from employees.models import Employee
from payroll.models import SalaryComponent, EmployeeSalaryStructure
from datetime import date
from decimal import Decimal

# 1. Create Tenant
tenant, _ = Tenant.objects.get_or_create(
    name="Tech Corp",
    defaults={'type': Tenant.TenantType.CORPORATE, 'email': 'hr@techcorp.com', 'phone': '1234567890'}
)
print(f"Tenant Created: {tenant}")

# 2. Create Components
basic, _ = SalaryComponent.objects.get_or_create(
    tenant=tenant, 
    name="Basic", 
    defaults={'type': SalaryComponent.ComponentType.EARNING, 'calculation_type': SalaryComponent.CalculationType.FLAT}
)

hra, _ = SalaryComponent.objects.get_or_create(
    tenant=tenant, 
    name="HRA", 
    defaults={
        'type': SalaryComponent.ComponentType.EARNING, 
        'calculation_type': SalaryComponent.CalculationType.FORMULA,
        'formula': 'basic * 0.40'
    }
)

pf, _ = SalaryComponent.objects.get_or_create(
    tenant=tenant, 
    name="PF", 
    defaults={
        'type': SalaryComponent.ComponentType.DEDUCTION, 
        'calculation_type': SalaryComponent.CalculationType.FORMULA,
        'formula': 'basic * 0.12'
    }
)
print("Components Created")

# 3. Create Employee
emp, _ = Employee.objects.get_or_create(
    tenant=tenant,
    email="alice@techcorp.com",
    defaults={
        'first_name': 'Alice', 'last_name': 'Smith', 
        'phone': '9876543210', 'date_of_joining': date.today(),
        'employee_code': 'EMP001', 'designation': 'Software Engineer'
    }
)
print(f"Employee Created: {emp}")

# 4. Assign Salary
EmployeeSalaryStructure.objects.get_or_create(employee=emp, component=basic, defaults={'amount': Decimal('50000')})
# Formulas don't need amounts in structure usually, but our logic might expect flat entries to trigger components. 
# Our current logic iterates through structure to apply.
# Let's add HRA/PF to structure with 0 amount just to enable them.
EmployeeSalaryStructure.objects.get_or_create(employee=emp, component=hra, defaults={'amount': Decimal('0')})
EmployeeSalaryStructure.objects.get_or_create(employee=emp, component=pf, defaults={'amount': Decimal('0')})
print("Salary Structure Assigned")

# 5. Run Calculation (Direct Service Call for testing)
from payroll.services import PayrollCalculator
calc = PayrollCalculator(tenant)
ledger = calc.calculate_employee_salary(emp, date.today())

print(f"Payroll Generated: {ledger}")
print(f"Earnings: {ledger.total_earnings}, Deductions: {ledger.total_deductions}, Net: {ledger.net_pay}")

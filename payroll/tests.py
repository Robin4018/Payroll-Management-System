from django.test import TestCase
from tenants.models import Tenant
from employees.models import Employee
from payroll.models import SalaryComponent, EmployeeSalaryStructure
from payroll.services import PayrollCalculator
from datetime import date
from decimal import Decimal

class PayrollLogicTestCase(TestCase):
    def setUp(self):
        # 1. Create Tenant
        self.tenant = Tenant.objects.create(name="Test Corp", type="CORPORATE")
        
        # 2. Create Components
        self.basic = SalaryComponent.objects.create(
            tenant=self.tenant, 
            name="Basic", 
            type="EARNING", 
            calculation_type="FLAT"
        )
        self.hra = SalaryComponent.objects.create(
            tenant=self.tenant, 
            name="HRA", 
            type="EARNING", 
            calculation_type="FORMULA",
            formula="Basic * 0.40"
        )
        self.pf = SalaryComponent.objects.create(
            tenant=self.tenant, 
            name="PF", 
            type="DEDUCTION", 
            calculation_type="FORMULA",
            formula="Basic * 0.12"
        )
        
        # 3. Create Employee
        self.employee = Employee.objects.create(
            tenant=self.tenant,
            first_name="Test",
            last_name="User",
            email="test@example.com",
            date_of_joining=date(2023, 1, 1),
            employee_code="E001"
        )
        
        # 4. Assign Structure (Basic = 10000)
        EmployeeSalaryStructure.objects.create(
            employee=self.employee,
            component=self.basic,
            amount=10000
        )
        EmployeeSalaryStructure.objects.create(employee=self.employee, component=self.hra)
        EmployeeSalaryStructure.objects.create(employee=self.employee, component=self.pf)

    def test_payroll_calculation_formulas(self):
        """
        Verify that formulas are calculated correctly.
        Basic = 10000
        HRA = 10000 * 0.4 = 4000
        PF = 10000 * 0.12 = 1200
        Total Earnings = 14000
        Total Deductions = 1200
        Net Pay = 12800
        """
        calculator = PayrollCalculator(self.tenant)
        ledgers = calculator.run_payroll_for_tenant(date(2023, 10, 1))
        
        ledger = ledgers[0]
        
        self.assertEqual(ledger.total_earnings, Decimal('14000.00'))
        self.assertEqual(ledger.total_deductions, Decimal('1200.00'))
        self.assertEqual(ledger.net_pay, Decimal('12800.00'))
        print("\nTest Payroll Logic: SUCCESS")

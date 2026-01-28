from django.core.management.base import BaseCommand
from payroll.models import SalaryComponent
from tenants.models import Tenant

class Command(BaseCommand):
    help = 'Seeds default salary components (Earnings and Deductions)'

    def handle(self, *args, **kwargs):
        tenant = Tenant.objects.first()
        if not tenant:
            self.stdout.write(self.style.ERROR('No tenants found. Create a tenant first.'))
            return

        earnings = [
            'Basic Pay', 'DA (Dearness Allowance)', 'HRA', 'TA', 
            'Special Allowance', 'Other Allowances'
        ]
        
        deductions = [
            'PF', 'ESI', 'Professional Tax', 'Income Tax', 'Loan Deduction'
        ]

        # Create Earnings
        for name in earnings:
            SalaryComponent.objects.get_or_create(
                tenant=tenant,
                name=name,
                defaults={
                    'type': SalaryComponent.ComponentType.EARNING,
                    'calculation_type': SalaryComponent.CalculationType.FLAT,
                    'is_taxable': True
                }
            )
            self.stdout.write(self.style.SUCCESS(f'Created/Checked Earning: {name}'))

        # Create Deductions
        for name in deductions:
            SalaryComponent.objects.get_or_create(
                tenant=tenant,
                name=name,
                defaults={
                    'type': SalaryComponent.ComponentType.DEDUCTION,
                    'calculation_type': SalaryComponent.CalculationType.FLAT,
                    'is_taxable': False
                }
            )
            self.stdout.write(self.style.SUCCESS(f'Created/Checked Deduction: {name}'))

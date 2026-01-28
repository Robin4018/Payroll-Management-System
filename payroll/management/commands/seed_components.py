from django.core.management.base import BaseCommand
from payroll.models import SalaryComponent
from tenants.models import Tenant

class Command(BaseCommand):
    help = 'Seeds standard salary components based on LOGICS.txt'

    def handle(self, *args, **options):
        # Assuming single tenant or we loop through all
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found."))
            return

        components = [
            # EARNINGS
            {
                'name': 'Basic Salary', 
                'type': SalaryComponent.ComponentType.EARNING, 
                'calculation_type': SalaryComponent.CalculationType.FORMULA,
                'formula': 'ctc * 0.40', # Default rule
                'is_taxable': True
            },
            {
                'name': 'House Rent Allowance', 
                'type': SalaryComponent.ComponentType.EARNING, 
                'calculation_type': SalaryComponent.CalculationType.FORMULA,
                'formula': 'basic * 0.50',
                'is_taxable': True
            },
            {
                'name': 'Dearness Allowance', 
                'type': SalaryComponent.ComponentType.EARNING, 
                'calculation_type': SalaryComponent.CalculationType.FORMULA,
                'formula': 'basic * 0.00', # Default 0
                'is_taxable': True
            },
            {
                'name': 'Transport Allowance', 
                'type': SalaryComponent.ComponentType.EARNING, 
                'calculation_type': SalaryComponent.CalculationType.FLAT,
                'formula': '1600',
                'is_taxable': True # Partially exempt rule handled elsewhere?
            },
            {
                'name': 'Medical Allowance', 
                'type': SalaryComponent.ComponentType.EARNING, 
                'calculation_type': SalaryComponent.CalculationType.FLAT,
                'formula': '1250',
                'is_taxable': True
            },
            {
                'name': 'Special Allowance', 
                'type': SalaryComponent.ComponentType.EARNING, 
                'calculation_type': SalaryComponent.CalculationType.FORMULA,
                'formula': '0', # Balancing
                'is_taxable': True
            },
            # DEDUCTIONS
            {
                'name': 'Provident Fund', 
                'type': SalaryComponent.ComponentType.DEDUCTION, 
                'calculation_type': SalaryComponent.CalculationType.FORMULA,
                'formula': '(basic + da) * 0.12',
                'is_taxable': False
            },
            {
                'name': 'Employee State Insurance', 
                'type': SalaryComponent.ComponentType.DEDUCTION, 
                'calculation_type': SalaryComponent.CalculationType.FORMULA,
                'formula': 'gross * 0.0075',
                'is_taxable': False
            },
            {
                'name': 'Professional Tax', 
                'type': SalaryComponent.ComponentType.DEDUCTION, 
                'calculation_type': SalaryComponent.CalculationType.FORMULA,
                'formula': '0', # State dependent
                'is_taxable': False
            },
            {
                'name': 'TDS', 
                'type': SalaryComponent.ComponentType.DEDUCTION, 
                'calculation_type': SalaryComponent.CalculationType.FORMULA,
                'formula': '0', # Complex
                'is_taxable': False
            },
        ]

        for tenant in tenants:
            self.stdout.write(f"Seeding for tenant: {tenant.name}")
            for comp_data in components:
                obj, created = SalaryComponent.objects.get_or_create(
                    tenant=tenant,
                    name=comp_data['name'],
                    defaults={
                        'type': comp_data['type'],
                        'calculation_type': comp_data['calculation_type'],
                        'formula': comp_data['formula'],
                        'is_taxable': comp_data['is_taxable']
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  Created {obj.name}"))
                else:
                    self.stdout.write(f"  Exists {obj.name}")

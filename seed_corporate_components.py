import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from payroll.models import SalaryComponent
from tenants.models import Tenant

def seed_corporate_components():
    tenant = Tenant.objects.filter(type='CORPORATE').first()
    if not tenant:
        print("No CORPORATE tenant found.")
        return

    components = [
        # Earnings
        {'name': 'Basic Salary', 'type': 'EARNING', 'calculation_type': 'FLAT_AMOUNT', 'is_taxable': True},
        {'name': 'House Rent Allowance (HRA)', 'type': 'EARNING', 'calculation_type': 'FORMULA', 'formula': 'basic * 0.4', 'is_taxable': True},
        {'name': 'Special Allowance', 'type': 'EARNING', 'calculation_type': 'FLAT_AMOUNT', 'is_taxable': True},
        
        # Deductions
        {'name': 'Provident Fund (PF)', 'type': 'DEDUCTION', 'calculation_type': 'FORMULA', 'formula': 'basic * 0.12', 'is_taxable': False},
        {'name': 'Professional Tax', 'type': 'DEDUCTION', 'calculation_type': 'FLAT_AMOUNT', 'is_taxable': False},
    ]

    for comp_data in components:
        comp, created = SalaryComponent.objects.get_or_create(
            tenant=tenant,
            name=comp_data['name'],
            defaults={
                'type': comp_data['type'],
                'calculation_type': comp_data['calculation_type'],
                'formula': comp_data.get('formula'),
                'is_taxable': comp_data['is_taxable']
            }
        )
        if created:
            print(f"Created component: {comp.name}")
        else:
            print(f"Component already exists: {comp.name}")

if __name__ == "__main__":
    seed_corporate_components()

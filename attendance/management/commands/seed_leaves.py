from django.core.management.base import BaseCommand
from attendance.models import LeaveType
from tenants.models import Tenant

class Command(BaseCommand):
    help = 'Seeds Leave Types from LOGICS.txt'

    def handle(self, *args, **options):
        # Assumption: Seed for all tenants or first tenant
        tenants = Tenant.objects.all()
        
        for tenant in tenants:
            self.stdout.write(f"Seeding for {tenant.name}...")
            
            # 1. Casual Leave (CL)
            # Typically 12 days/year -> 1 per month
            LeaveType.objects.get_or_create(
                tenant=tenant, 
                name='Casual Leave',
                defaults={'max_days_allowed': 12, 'is_paid': True, 'description': 'Monthly accrual of 1 day'}
            )
            
            # 2. Sick Leave (SL)
            # Typically 12 days/year
            LeaveType.objects.get_or_create(
                tenant=tenant, 
                name='Sick Leave',
                defaults={'max_days_allowed': 12, 'is_paid': True, 'description': 'Medical leave'}
            )
            
            # 3. Privilege Leave (PL) / Earned Leave (EL)
            # Typically 15-18 days/year, accrued after probation
            LeaveType.objects.get_or_create(
                tenant=tenant, 
                name='Earned Leave',
                defaults={'max_days_allowed': 15, 'is_paid': True, 'description': 'Accrues 1.25 per month'}
            )
            
        self.stdout.write(self.style.SUCCESS("Leaves seeded"))

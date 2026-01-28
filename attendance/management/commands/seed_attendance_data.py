from django.core.management.base import BaseCommand
from attendance.models import LeaveType
from tenants.models import Tenant

class Command(BaseCommand):
    help = 'Seeds default Leave Types'

    def handle(self, *args, **kwargs):
        tenant = Tenant.objects.first()
        if not tenant:
            self.stdout.write(self.style.ERROR('No tenant found'))
            return

        types = ['CL', 'SL', 'EL', 'LOP']
        for name in types:
            obj, created = LeaveType.objects.get_or_create(
                tenant=tenant,
                name=name,
                defaults={
                    'max_days_allowed': 12,
                    'is_paid': name != 'LOP',
                    'description': f'Default {name}'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created {name}'))
            else:
                self.stdout.write(f'{name} exists')

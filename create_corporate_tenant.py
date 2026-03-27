import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from tenants.models import Tenant

def ensure_corporate_tenant():
    corporate_tenant, created = Tenant.objects.get_or_create(
        type='CORPORATE',
        defaults={
            'name': 'Corporate Enterprise Solutions',
            'short_name': 'CES',
            'email': 'admin@corporate.local',
            'phone': '1234567890',
            'is_active': True
        }
    )
    if created:
        print(f"Created CORPORATE tenant: {corporate_tenant.name}")
    else:
        print(f"CORPORATE tenant already exists: {corporate_tenant.name}")

if __name__ == "__main__":
    ensure_corporate_tenant()

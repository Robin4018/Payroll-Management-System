import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from tenants.models import Tenant

if not Tenant.objects.exists():
    tenant = Tenant.objects.create(
        name="Default College",
        type=Tenant.TenantType.EDUCATION,
        email="info@college.edu",
        phone="1234567890"
    )
    print(f"Created Tenant: {tenant.name} (ID: {tenant.id})")
else:
    t = Tenant.objects.first()
    print(f"Tenant exists: {t.name} (ID: {t.id})")

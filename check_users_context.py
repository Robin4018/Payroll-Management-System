import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import UserProfile

print("--- Users ---")
for user in User.objects.all():
    profile = UserProfile.objects.filter(user=user).first()
    org_type = profile.organization_type if profile else "NONE"
    print(f"User: {user.username}, Super: {user.is_superuser}, Staff: {user.is_staff}, Profile: {org_type}")

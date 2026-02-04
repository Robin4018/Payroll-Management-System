import os
import django
import sys

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Designation

count = Designation.objects.count()
print(f"Total Designations: {count}")

try:
    print(f"Sample: {Designation.objects.first()}")
except:
    pass

# Verify fields
try:
    d = Designation.objects.first()
    print(f"Has min_ctc: {hasattr(d, 'estimated_min_ctc')}")
except:
    pass

import os
import sys
sys.path.append(os.getcwd())
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.urls import reverse
url1 = reverse('payroll-consolidated-report')
print(f"URL1: |{url1}|")
url2 = reverse('payroll-consolidated-report', kwargs={'format': 'json'})
print(f"URL2: |{url2}|")

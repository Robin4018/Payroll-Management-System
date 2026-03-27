import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.urls import reverse

try:
    url = reverse('report-analytics-list')
    print(f"URL for report-analytics-list: {url}")
except Exception as e:
    print(f"Error reversing report-analytics-list: {e}")

try:
    # Try with format suffix pattern if it exists
    url = reverse('report-analytics-list', kwargs={'format': 'json'})
    print(f"URL with format JSON: {url}")
except Exception as e:
    print(f"Error reversing with format: {e}")

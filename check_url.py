
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()

from django.urls import reverse, resolve

try:
    url = reverse('report-analytics')
    print(f"Reversed URL: {url}")
    match = resolve(url)
    print(f"Resolved to: {match.func}")
except Exception as e:
    print(f"Error: {e}")

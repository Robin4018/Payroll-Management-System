
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()

from django.urls import get_resolver

resolver = get_resolver()
print("URL Patterns registered:")
for pattern in resolver.url_patterns:
    print(f" - {pattern}")

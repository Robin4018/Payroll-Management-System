import os
import sys
import django

# Add the project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth.models import User
from payroll.views import ReportViewSet

factory = APIRequestFactory()
try:
    user = User.objects.get(username='robin')
    view = ReportViewSet.as_view({'get': 'list'})

    request = factory.get('/api/report-analytics/', {'type': 'monthly', 'month': '2026-02', 'format': 'excel'})
    force_authenticate(request, user=user)

    response = view(request)
    print(f"Status: {response.status_code}")
    print(f"Data: {response.data}")
except Exception as e:
    import traceback
    print(traceback.format_exc())

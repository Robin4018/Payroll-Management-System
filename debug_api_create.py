
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from payroll.views import SalaryComponentViewSet
# Removed direct import of inner classes

factory = APIRequestFactory()

data = {
    "name": "Test Component Script",
    "type": "EARNING", 
    "calculation_type": "FLAT_AMOUNT",
    "description": "Debug",
    "is_taxable": True,
    "is_active": True,
    "tenant": 9
}

print("Attempting to create component with data:", data)

request = factory.post('/api/components/', data, format='json')
view = SalaryComponentViewSet.as_view({'post': 'create'})
response = view(request)

print("Status Code:", response.status_code)
print("Response Data:", response.data)


import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from payroll.models import PayrollLedger
from payroll.serializers import PayrollLedgerSerializer
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()
request = factory.get('/api/payroll/')
# Mock user if needed, but here we just want to see serialization
# PayrollLedgerViewSet expects authenticated user.

from django.contrib.auth.models import User
admin = User.objects.filter(is_superuser=True).first()

ledgers = PayrollLedger.objects.filter(month='2026-02-01').order_by('employee__employee_code')
serializer = PayrollLedgerSerializer(ledgers, many=True)
data = serializer.data

for item in data:
    emp_code = item.get('employee_code')
    bank = item.get('bank_details')
    print(f"{emp_code}: Bank Object Presence = {bank is not None}")
    if bank:
        print(f"  Bank Name: {bank.get('bank_name')}")

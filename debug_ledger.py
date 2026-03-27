
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from payroll.models import PayrollLedger
from payroll.serializers import PayrollLedgerSerializer

ledger = PayrollLedger.objects.first()
if ledger:
    serializer = PayrollLedgerSerializer(ledger)
    print(serializer.data)
else:
    print("No ledgers found")

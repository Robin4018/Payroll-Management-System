
import os
import pandas as pd
from django.conf import settings
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from payroll.models import PayrollLedger
from datetime import datetime

month_date = datetime(2026, 2, 1).date()
ledgers = PayrollLedger.objects.filter(month=month_date)
print(f"Found {ledgers.count()} ledgers")

fname = f"test_master_{month_date}.xlsx"
fpath = os.path.join(settings.BASE_DIR, 'media', 'reports', fname)
os.makedirs(os.path.dirname(fpath), exist_ok=True)

try:
    with pd.ExcelWriter(fpath, engine='openpyxl') as writer:
        df = pd.DataFrame([{"Test": "Success"}])
        df.to_excel(writer, sheet_name="Test", index=False)
    print(f"Successfully wrote to {fpath}")
except Exception as e:
    print(f"Failed: {str(e)}")

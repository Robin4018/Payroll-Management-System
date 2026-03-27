import os
import django
import sys
from django.db.models import Sum
from datetime import date

# Add the project directory to sys.path
sys.path.append(r'd:\Project\Payroll Management System\universal-payroll-system')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from payroll.models import PayrollLedger
from tenants.models import Tenant

# Assuming we are looking at the 'EDUCATION' tenant or the first one, similar to the view logic
tenant = Tenant.objects.filter(type='EDUCATION').first() or Tenant.objects.first()
print(f"Tenant: {tenant.name} (ID: {tenant.id})")

# 1. Calendar Year 2026 Stats
print("\n--- Calendar Year 2026 ---")
cy_net = PayrollLedger.objects.filter(employee__tenant=tenant, month__year=2026).aggregate(Sum('net_pay'))['net_pay__sum'] or 0
cy_gross = PayrollLedger.objects.filter(employee__tenant=tenant, month__year=2026).aggregate(Sum('total_earnings'))['total_earnings__sum'] or 0
print(f"Net Pay Sum: {cy_net}")
print(f"Gross Pay Sum: {cy_gross}")

# 2. Fiscal Year Calculation (Apr 2025 - Mar 2026) -> Current Date is Feb 2026
print("\n--- Fiscal Year 2025-26 (Apr 2025 - Mar 2026) ---")
start_date = date(2025, 4, 1)
end_date = date(2026, 3, 31)
fy_net = PayrollLedger.objects.filter(employee__tenant=tenant, month__range=[start_date, end_date]).aggregate(Sum('net_pay'))['net_pay__sum'] or 0
fy_gross = PayrollLedger.objects.filter(employee__tenant=tenant, month__range=[start_date, end_date]).aggregate(Sum('total_earnings'))['total_earnings__sum'] or 0
print(f"Net Pay Sum: {fy_net}")
print(f"Gross Pay Sum: {fy_gross}")

import os
import django
import sys
from datetime import date
from django.db.models import Sum, Count
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.getcwd())
django.setup()

from django.contrib.auth import get_user_model
from employees.models import Employee
from payroll.models import PayrollLedger
from tenants.models import Tenant

User = get_user_model()

def test_logic():
    print("--- Testing Dashboard Stats Logic ---")
    try:
        user = User.objects.get(username='robin')
        print(f"User: {user}")
    except User.DoesNotExist:
        print("User robin not found")
        return

    if not hasattr(user, 'employee'):
        print("User has no employee!")
        return
    
    tenant = user.employee.tenant
    print(f"Tenant: {tenant} (ID: {tenant.id})")

    try:
        # 1. Overview Stats
        total_employees = Employee.objects.filter(tenant=tenant).count()
        print(f"Total Employees: {total_employees}")

        active_employees = Employee.objects.filter(tenant=tenant, is_active=True).count()
        print(f"Active Employees: {active_employees}")
        
        # Financials
        last_ledger_entry = PayrollLedger.objects.filter(employee__tenant=tenant).order_by('-month').first()
        print(f"Last Ledger Entry: {last_ledger_entry}")
        
        current_month_cost = 0
        last_payroll_date = None
        
        if last_ledger_entry:
            last_payroll_date = last_ledger_entry.month
            print(f"Last Payroll Date: {last_payroll_date}")
            current_month_cost = PayrollLedger.objects.filter(
                employee__tenant=tenant,
                month=last_payroll_date
            ).aggregate(Sum('net_pay'))['net_pay__sum'] or 0
        
        print(f"Current Month Cost: {current_month_cost}")
        
        # YTD
        current_year = timezone.now().year
        ytd_payroll = PayrollLedger.objects.filter(
            employee__tenant=tenant,
            month__year=current_year
        ).aggregate(Sum('net_pay'))['net_pay__sum'] or 0
        print(f"YTD Payroll: {ytd_payroll}")
        
        # Charts - Department
        dept_dist_qs = Employee.objects.filter(tenant=tenant).values('department__name').annotate(count=Count('id'))
        print("Dept Dist:")
        for d in dept_dist_qs:
            print(f" - {d}")

    except Exception as e:
        print(f"EXCEPTION OCCURRED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_logic()

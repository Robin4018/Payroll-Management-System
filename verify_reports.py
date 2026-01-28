import os
import django
import sys
from decimal import Decimal
from datetime import date
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.getcwd())
django.setup()

from tenants.models import Tenant
from employees.models import Employee
from payroll.models import PayrollLedger
from rest_framework.test import APIRequestFactory, force_authenticate
from payroll.views import PayrollLedgerViewSet, ReportViewSet
from django.contrib.auth import get_user_model

User = get_user_model()

def verify_reports():
    print("--- Verifying Payroll Reports ---")
    
    # Setup Context
    tenant = Tenant.objects.filter(type='EDUCATION').first()
    user = User.objects.get(username='robin') # Admin user we fixed earlier
    
    # Validate user linkage
    if not hasattr(user, 'employee'):
        print("ERROR: Admin user not linked to employee. Run 'create_admin_employee.py' first.")
        return

    # 1. Run Payroll
    print("\n1. Running Payroll for Feb 2024...")
    factory = APIRequestFactory()
    
    # Create request for run_payroll
    # Endpoint: /api/payroll/run/
    view_run = PayrollLedgerViewSet.as_view({'post': 'run_payroll'})
    request_run = factory.post('/api/payroll/run/', {'month': '2024-02-01', 'tenant_id': tenant.id}, format='json')
    force_authenticate(request_run, user=user)
    
    response_run = view_run(request_run)
    print(f"Run Payroll Status: {response_run.status_code}")
    if response_run.status_code != 200:
        print(f"Error: {response_run.data}")
        return

    # 2. Verify Ledger Created
    ledgers = PayrollLedger.objects.filter(month=date(2024, 2, 1), employee__tenant=tenant)
    count = ledgers.count()
    print(f"Generated {count} ledger entries.")
    
    if count == 0:
        print("ERROR: No ledgers generated.")
        return

    # 3. Fetch Monthly Report
    print("\n2. Fetching Monthly Report...")
    # Endpoint: /api/reports/?type=monthly&month=2024-02
    view_report = ReportViewSet.as_view({'get': 'list'})
    request_report = factory.get('/api/reports/', {'type': 'monthly', 'month': '2024-02'})
    force_authenticate(request_report, user=user)
    
    response_report = view_report(request_report)
    print(f"Report Status: {response_report.status_code}")
    
    if response_report.status_code == 200:
        data = response_report.data
        print(f"Report Items: {len(data)}")
        
        # Validate Data Structure
        if len(data) > 0:
            first = data[0]
            print(f"Sample Row: {first}")
            
            # Check Keys
            required_keys = ['Employee', 'Code', 'Earnings', 'Deductions', 'Net Pay']
            missing = [k for k in required_keys if k not in first]
            if missing:
                print(f"❌ Missing Columns in Report: {missing}")
            else:
                print("✅ Report Structure Correct")
                
            # Verify Total vs Ledger
            report_net_total = sum(float(row['Net Pay']) for row in data)
            ledger_net_total = sum(l.net_pay for l in ledgers)
            
            print(f"Report Total Net: {report_net_total}")
            print(f"Ledger Total Net: {ledger_net_total}")
            
            if abs(report_net_total - float(ledger_net_total)) < 1.0:
                print("✅ Totals Match")
            else:
                print("❌ Totals Mismatch")
                
    # 4. Verify Payslip Generation (HTML/PDF)
    print("\n3. Testing Payslip Generation...")
    # Pick first employee ledger
    ledger = ledgers.first()
    
    # Endpoint logic based on PayrollLedgerViewSet
    # usually /api/payroll/ledgers/{pk}/download_payslip/
    
    request_payslip = factory.get(f'/api/payroll/ledgers/{ledger.id}/download_payslip/')
    force_authenticate(request_payslip, user=user)
    
    view_ps = PayrollLedgerViewSet.as_view({'get': 'download_payslip'})
    
    try:
        response_ps = view_ps(request_payslip, pk=ledger.id)
        if response_ps.status_code == 200:
            ctype = response_ps.get('Content-Type', 'unknown')
            print(f"✅ Payslip Generated (Content Type: {ctype})")
        else:
            print(f"❌ Payslip Error: {response_ps.status_code} - {response_ps.data}")
    except Exception as e:
        print(f"❌ Payslip Exception: {e}")
                
    # 4. Verify Payslip Generation (HTML/PDF)
    print("\n3. Testing Payslip Generation...")
    # Pick first employee ledger
    ledger = ledgers.first()
    # Endpoint: /api/payroll/download-payslip/?ledger_id=...
    # view_payslip = PayrollLedgerViewSet.as_view({'get': 'download_payslip'}) # This is likely a custom action
    
    # Let's check the url for print: /payroll/print-payslip/<id>/ usually?
    # Or API: /api/payroll/ledgers/{id}/download_payslip/
    
    # Based on standard DRF action:
    # url: /api/payroll/ledgers/<pk>/download_payslip/
    
    request_payslip = factory.get(f'/api/payroll/ledgers/{ledger.id}/download_payslip/')
    force_authenticate(request_payslip, user=user)
    
    # We need to instantiate the viewset with the action
    view_ps = PayrollLedgerViewSet.as_view({'get': 'download_payslip'})
    
    try:
        response_ps = view_ps(request_payslip, pk=ledger.id)
        if response_ps.status_code == 200:
            print(f"✅ Payslip Generated (Content Type: {response_ps['Content-Type']})")
        else:
            print(f"❌ Payslip Error: {response_ps.status_code}")
    except Exception as e:
        print(f"❌ Payslip Exception: {e}")

    else:
        print(f"Error fetching output: {response_report.data}")

if __name__ == '__main__':
    verify_reports()

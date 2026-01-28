import os
import django
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.getcwd())
django.setup()

from django.test import RequestFactory
from rest_framework.test import force_authenticate
from django.contrib.auth import get_user_model
from payroll.api_stats import DashboardStatsView
from employees.models import Employee

User = get_user_model()

def test_fallback():
    print("--- Testing Superuser Fallback ---")
    
    # 1. Get User
    try:
        user = User.objects.get(username='robin')
    except User.DoesNotExist:
        print("User robin not found")
        return

    # 2. TEMPORARILY Break Link (Simulate user deleting their record)
    original_emp = getattr(user, 'employee', None)
    if original_emp:
        print("Breaking link for testing...")
        original_emp.user = None
        original_emp.save()
        user.refresh_from_db()
        print(f"User has employee? {hasattr(user, 'employee')}")
    else:
        print("User already unlinked.")

    # 3. Test View
    factory = RequestFactory()
    request = factory.get('/api/payroll/dashboard/stats/')
    request.user = user
    force_authenticate(request, user=user)
    
    view = DashboardStatsView.as_view()
    response = view(request)
    
    print(f"Response Code: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS: Data returned even without Employee record!")
        print(f"Stats: {response.data.get('stats', {}).get('total_employees')} employees found.")
    else:
        print("FAILURE: View returned error.")
        print(response.data)

    # 4. Restore Link
    if original_emp:
        print("Restoring link...")
        original_emp.user = user
        original_emp.save()
        print("Link restored.")

if __name__ == '__main__':
    test_fallback()

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from attendance.models import LeaveType, LeaveBalance, LeaveRequest
from employees.models import Employee
from tenants.models import Tenant

def seed_leaves():
    # 1. Ensure Leave Types exist for each tenant
    tenants = Tenant.objects.all()
    if not tenants.exists():
        print("No tenants found.")
        return

    leave_types_data = [
        {'name': 'Casual Leave', 'max_days': 12},
        {'name': 'Sick Leave', 'max_days': 10},
        {'name': 'Earned Leave', 'max_days': 20},
    ]

    for tenant in tenants:
        for lt_data in leave_types_data:
            lt, created = LeaveType.objects.get_or_create(
                tenant=tenant,
                name=lt_data['name'],
                defaults={'max_days_allowed': lt_data['max_days']}
            )
            if created:
                print(f"Created LeaveType {lt.name} for tenant {tenant.name}")

    # 2. Initialize Balances for all employees
    employees = Employee.objects.all()
    for employee in employees:
        tenant_leave_types = LeaveType.objects.filter(tenant=employee.tenant)
        for lt in tenant_leave_types:
            lb, created = LeaveBalance.objects.get_or_create(
                employee=employee,
                leave_type=lt,
                defaults={
                    'balance': lt.max_days_allowed,
                    'accrued': lt.max_days_allowed,
                    'used': 0
                }
            )
            if created:
                print(f"Initialized {lt.name} balance for {employee.first_name} {employee.last_name}")
            else:
                # Optionally update balance to match max if currently zero and requested by user
                # For now let's just ensure they exist.
                pass

    print("Seeding completed.")

if __name__ == "__main__":
    seed_leaves()

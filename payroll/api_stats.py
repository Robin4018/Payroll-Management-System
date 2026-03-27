from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from django.utils import timezone
from employees.models import Employee
from .models import PayrollLedger

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month_param = request.query_params.get('month')
        
        # Get tenant from logged-in user
        tenant = None
        if hasattr(request.user, 'employee') and request.user.employee.tenant:
            tenant = request.user.employee.tenant
        elif request.user.is_superuser:
            from tenants.models import Tenant
            org_type = getattr(request.user.profile, 'organization_type', 'COMPANY') if hasattr(request.user, 'profile') else 'COMPANY'
            tenant_type = 'CORPORATE' if org_type == 'COMPANY' else 'EDUCATION'
            tenant = Tenant.objects.filter(type=tenant_type).first() or Tenant.objects.first()
        
        if not tenant:
            return Response({"error": "No tenant found for user"}, status=400)
        
        # 1. Overview Stats - Filter by tenant
        employee_qs = Employee.objects.filter(tenant=tenant)
        ledger_qs = PayrollLedger.objects.filter(employee__tenant=tenant)

        if month_param:
            # If a specific month is selected, we filter by it
            total_employees = employee_qs.count()
            active_employees = employee_qs.filter(is_active=True).count()
            
            month_ledger = ledger_qs.filter(month=month_param)
            current_month_cost = month_ledger.aggregate(Sum('net_pay'))['net_pay__sum'] or 0
            last_payroll_date = month_param
        else:
            # Default behavior: Latest month stats
            total_employees = employee_qs.count()
            active_employees = employee_qs.filter(is_active=True).count()
            
            last_ledger_entry = ledger_qs.order_by('-month').first()
            current_month_cost = 0
            last_payroll_date = None
            
            if last_ledger_entry:
                last_payroll_date = last_ledger_entry.month
                current_month_cost = ledger_qs.filter(month=last_payroll_date).aggregate(Sum('net_pay'))['net_pay__sum'] or 0

        # YTD (Current Calendar Year) for this tenant
        current_year = timezone.now().year
        ytd_payroll = PayrollLedger.objects.filter(
            employee__tenant=tenant,
            month__year=current_year
        ).aggregate(Sum('net_pay'))['net_pay__sum'] or 0

        avg_salary = 0
        if active_employees > 0 and current_month_cost > 0:
            avg_salary = current_month_cost / active_employees

        # 2. Charts Data
        
        # Department Distribution - Filter by tenant
        dept_dist_qs = Employee.objects.filter(tenant=tenant).values('department__name').annotate(count=Count('id'))
        dept_labels = []
        dept_counts = []
        for item in dept_dist_qs:
            dept_labels.append(item['department__name'] or 'Unknown')
            dept_counts.append(item['count'])

        # Salary Trend (Last 6 Months) - Filter by tenant
        trend_qs = PayrollLedger.objects.filter(
            employee__tenant=tenant
        ).values('month').annotate(total=Sum('net_pay')).order_by('-month')[:6]
        trend_labels = []
        trend_values = []
        
        # Reverse to show oldest -> newest
        for item in reversed(trend_qs):
            lbl = item['month'].strftime('%b %Y') if item['month'] else 'Unknown'
            trend_labels.append(lbl)
            trend_values.append(item['total'])

        # 3. Pending Approvals - Filter by tenant
        from attendance.models import LeaveRequest
        from .models import Loan, Reimbursement
        pending_leaves = LeaveRequest.objects.filter(employee__tenant=tenant, status='PENDING').count()
        pending_loans = Loan.objects.filter(employee__tenant=tenant, status='PENDING').count()
        pending_reimbursements = Reimbursement.objects.filter(employee__tenant=tenant, status='PENDING').count()
        pending_total = pending_leaves + pending_loans + pending_reimbursements

        return Response({
            "stats": {
                "total_employees": int(total_employees),
                "active_employees": int(active_employees),
                "inactive_employees": int(total_employees - active_employees),
                "last_month_payroll": float(current_month_cost),
                "total_monthly_salary": float(current_month_cost), # Compatibility
                "ytd_payroll": float(ytd_payroll),
                "total_year_spend": float(ytd_payroll), # Compatibility
                "avg_salary": float(avg_salary),
                "last_run_date": last_payroll_date,
                "pending_approvals": int(pending_total)
            },
            "charts": {
                "dept_distribution": {
                    "labels": dept_labels,
                    "data": [int(x) for x in dept_counts]
                },
                "salary_trend": {
                    "labels": trend_labels,
                    "data": [float(x) for x in trend_values]
                }
            }
        })

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
        # Get tenant from logged-in user
        # Get tenant from logged-in user
        tenant = None
        if hasattr(request.user, 'employee') and request.user.employee.tenant:
            tenant = request.user.employee.tenant
        elif request.user.is_superuser:
            # Fallback for superuser: Use the first available tenant (or specifically Education if available)
            # This prevents dashboard breakage if the superuser deletes their own Employee record.
            from tenants.models import Tenant
            tenant = Tenant.objects.filter(type='EDUCATION').first() or Tenant.objects.first()
        
        if not tenant:
            return Response({"error": "No tenant found for user"}, status=400)
        
        # 1. Overview Stats - Filter by tenant
        total_employees = Employee.objects.filter(tenant=tenant).count()
        active_employees = Employee.objects.filter(tenant=tenant, is_active=True).count()
        
        # Financials
        # Get the latest month where payroll was run for this tenant
        last_ledger_entry = PayrollLedger.objects.filter(employee__tenant=tenant).order_by('-month').first()
        current_month_cost = 0
        last_payroll_date = None
        
        if last_ledger_entry:
            last_payroll_date = last_ledger_entry.month
            # Aggregate all ledgers for this specific month and tenant
            current_month_cost = PayrollLedger.objects.filter(
                employee__tenant=tenant,
                month=last_payroll_date
            ).aggregate(Sum('net_pay'))['net_pay__sum'] or 0

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

        return Response({
            "stats": {
                "total_employees": total_employees,
                "active_employees": active_employees,
                "inactive_employees": total_employees - active_employees,
                "last_month_payroll": current_month_cost,
                "ytd_payroll": ytd_payroll,
                "avg_salary": avg_salary,
                "last_run_date": last_payroll_date
            },
            "charts": {
                "dept_distribution": {
                    "labels": dept_labels,
                    "data": dept_counts
                },
                "salary_trend": {
                    "labels": trend_labels,
                    "data": trend_values
                }
            }
        })

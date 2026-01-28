from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PayrollLedgerViewSet, SalaryComponentViewSet, EmployeeSalaryStructureViewSet, PayrollAdjustmentViewSet
from .api_stats import DashboardStatsView

router = DefaultRouter()
# Specific basename to avoid conflicts
router.register(r"run", PayrollLedgerViewSet, basename='payroll-run') # Keep 'run' if frontend uses it, or just use 'payroll'
router.register(r"", PayrollLedgerViewSet, basename='payroll') # Default /api/payroll/

router.register(r"components", SalaryComponentViewSet, basename='components')
router.register(r"salary-structures", EmployeeSalaryStructureViewSet, basename='salary-structures')
router.register(r"adjustments", PayrollAdjustmentViewSet, basename='adjustments')
from .views import SalaryTemplateViewSet, LoanViewSet, ReportViewSet, ReimbursementViewSet
router.register(r"templates", SalaryTemplateViewSet, basename='templates')
router.register(r"loans", LoanViewSet, basename='loans')
router.register(r"reimbursements", ReimbursementViewSet, basename='reimbursements')
router.register(r"report-analytics", ReportViewSet, basename='report-analytics')

urlpatterns = [
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
] + router.urls

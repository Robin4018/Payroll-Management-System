from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payroll.views import PayrollLedgerViewSet, SalaryComponentViewSet, EmployeeSalaryStructureViewSet, PayrollAdjustmentViewSet, ReportViewSet
from employees.views import EmployeeViewSet, DepartmentViewSet, DesignationViewSet, EmployeeBankDetailsViewSet, EmployeeDocumentViewSet, RoleViewSet

from attendance.views import AttendanceViewSet, LeaveTypeViewSet, LeaveRequestViewSet

router = DefaultRouter()
router.register(r'employees/departments', DepartmentViewSet, basename='department')
router.register(r'employees/designations', DesignationViewSet, basename='designation')
router.register(r'bank-details', EmployeeBankDetailsViewSet, basename='employee-bank-details')
router.register(r'employee-documents', EmployeeDocumentViewSet, basename='employee-documents')
router.register(r'employees', EmployeeViewSet)
router.register(r'roles', RoleViewSet, basename='roles')
router.register(r'payroll', PayrollLedgerViewSet)
router.register(r'components', SalaryComponentViewSet)
router.register(r'salary-structures', EmployeeSalaryStructureViewSet) # Renamed to match frontend
router.register(r'adjustments', PayrollAdjustmentViewSet)
from payroll.views import SalaryTemplateViewSet, LoanViewSet, ReimbursementViewSet
router.register(r'payroll/templates', SalaryTemplateViewSet, basename='salary-templates')
router.register(r'loans', LoanViewSet, basename='loans')
router.register(r'reimbursements', ReimbursementViewSet, basename='reimbursements')
router.register(r'report-analytics', ReportViewSet, basename='report-analytics')
router.register(r'attendance', AttendanceViewSet)
router.register(r'leave-types', LeaveTypeViewSet)
router.register(r'leave-requests', LeaveRequestViewSet)

from notifications.views import NotificationViewSet
router.register(r'notifications', NotificationViewSet, basename='notifications')
from notifications.views import ApprovalsViewSet
router.register(r'approvals', ApprovalsViewSet, basename='approvals')

from audit_logs.views import AuditLogViewSet
router.register(r'audit-logs', AuditLogViewSet)

from compliance.views import StatutoryRateViewSet, TaxSlabViewSet, TaxDeclarationViewSet
router.register(r'compliance/rates', StatutoryRateViewSet, basename='compliance-rates')
router.register(r'compliance/tax-slabs', TaxSlabViewSet, basename='compliance-tax-slabs')
router.register(r'compliance/declarations', TaxDeclarationViewSet, basename='compliance-declarations')

from support.views import SupportTicketViewSet
router.register(r'support/tickets', SupportTicketViewSet, basename='support-tickets')

from tenants.views import TenantSettingsViewSet
router.register(r'tenant-settings', TenantSettingsViewSet, basename='tenant-settings')

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from employees.views import UserInfoView, RegisterView, SetProfileView
from payroll.api_stats import DashboardStatsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/me/', UserInfoView.as_view(), name='user-info'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/set-profile/', SetProfileView.as_view(), name='set-profile'),
    path('api/payroll/dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include('frontend.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from .views import (
    login_view, logout_view, signup_view, dashboard_view, select_entity_view, 
    dashboard_school_view, dashboard_college_view, dashboard_company_view,
    school_employees_view, school_payroll_view, school_structure_view, 
    school_reports_view, school_settings_view, college_employees_view,
    college_departments_view, college_designations_view, college_salary_structure_view,
    college_attendance_view, college_payroll_view, college_payslips_view,
    college_compliance_view, college_bank_payments_view, college_reports_view,
    college_notifications_view, college_audit_view, college_settings_view,
    college_employee_detail_view, college_tax_declarations_view, college_loans_view, college_reimbursements_view,
    college_compliance_settings_view, college_help_view, college_roles_view, college_profile_view,
    api_login_view, staff_dashboard_view, staff_profile_view, staff_leaves_view, staff_payslips_view,
    staff_attendance_view, staff_tax_view, staff_reimbursements_view, staff_help_view, staff_announcements_view,
    company_employees_view, company_employee_detail_view, company_departments_view, company_salary_structure_view, company_attendance_view,
    company_payroll_view, company_reimbursements_view, company_reimbursement_detail_view, company_payments_view, company_reports_view,
    company_staff_dashboard_view
)
from .debug_views import auto_login

urlpatterns = [
    path('auto-login/', auto_login, name='auto-login'),
    path('api/login-session/', api_login_view, name='api-login-session'),
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup_view, name='signup'),
    path('dashboard/', dashboard_school_view, name='dashboard-default'), # Fallback
    path('dashboard/school/', dashboard_school_view, name='dashboard-school'),
    path('dashboard/college/', dashboard_college_view, name='dashboard-college'),
    path('dashboard/company/', dashboard_company_view, name='dashboard-company'),
    path('select-entity/', select_entity_view, name='select-entity'),

    # School Modules
    path('dashboard/school/employees/', school_employees_view, name='school-employees'),
    path('dashboard/school/payroll/', school_payroll_view, name='school-payroll'),
    path('dashboard/school/structure/', school_structure_view, name='school-structure'),
    path('dashboard/school/reports/', school_reports_view, name='school-reports'),
    path('dashboard/school/settings/', school_settings_view, name='school-settings'),

    # College Modules
    path('dashboard/college/employees/', college_employees_view, name='college-employees'),
    path('dashboard/college/employees/<int:id>/', college_employee_detail_view, name='college-employee-detail'),
    path('dashboard/college/departments/', college_departments_view, name='college-departments'),
    path('dashboard/college/designations/', college_designations_view, name='college-designations'),
    path('dashboard/college/salary-structure/', college_salary_structure_view, name='college-salary-structure'),
    path('dashboard/college/attendance/', college_attendance_view, name='college-attendance'),
    path('dashboard/college/payroll-processing/', college_payroll_view, name='college-payroll'),
    path('dashboard/college/payslips/', college_payslips_view, name='college-payslips'),
    path('dashboard/college/compliance/', college_compliance_view, name='college-compliance'),
    path('dashboard/college/bank-payments/', college_bank_payments_view, name='college-bank-payments'),
    path('dashboard/college/reports/', college_reports_view, name='college-reports'),
    path('dashboard/college/tax/', college_tax_declarations_view, name='college-tax'),
    path('dashboard/college/loans/', college_loans_view, name='college-loans'),
    path('dashboard/college/reimbursements/', college_reimbursements_view, name='college-reimbursements'),
    path('dashboard/college/notifications/', college_notifications_view, name='college-notifications'),
    path('dashboard/college/audit/', college_audit_view, name='college-audit'),
    path('dashboard/college/profile/', college_profile_view, name='college-profile'),
    path('dashboard/college/settings/', college_settings_view, name='college-settings'),
    path('dashboard/college/compliance-settings/', college_compliance_settings_view, name='college-compliance-settings'),
    path('dashboard/college/help/', college_help_view, name='college-help'),
    path('dashboard/college/roles/', college_roles_view, name='college-roles'),
    
    # Staff Dashboard
    path('dashboard/staff/', staff_dashboard_view, name='staff-dashboard'),
    path('dashboard/staff/profile/', staff_profile_view, name='staff-profile'),
    path('dashboard/staff/leaves/', staff_leaves_view, name='staff-leaves'),
    path('dashboard/staff/payslips/', staff_payslips_view, name='staff-payslips'),
    path('dashboard/staff/attendance/', staff_attendance_view, name='staff-attendance'),
    path('dashboard/staff/tax/', staff_tax_view, name='staff-tax'),
    path('dashboard/staff/reimbursements/', staff_reimbursements_view, name='staff-reimbursements'),
    path('dashboard/staff/help/', staff_help_view, name='staff-help'),
    path('dashboard/staff/announcements/', staff_announcements_view, name='staff-announcements'),
    
    # Corporate Employee Portal
    path('dashboard/company/staff/', company_staff_dashboard_view, name='company-staff-dashboard'),
    path('dashboard/company/staff/profile/', staff_profile_view, name='company-staff-profile'),
    path('dashboard/company/staff/leaves/', staff_leaves_view, name='company-staff-leaves'),
    path('dashboard/company/staff/payslips/', staff_payslips_view, name='company-staff-payslips'),
    path('dashboard/company/staff/attendance/', staff_attendance_view, name='company-staff-attendance'),
    path('dashboard/company/staff/reimbursements/', staff_reimbursements_view, name='company-staff-reimbursements'),
    path('dashboard/company/staff/help/', staff_help_view, name='company-staff-help'),
    path('dashboard/company/staff/announcements/', staff_announcements_view, name='company-staff-announcements'),
    
    # Corporate Admin Portal
    path('dashboard/company/employees/', company_employees_view, name='company-employees'),
    path('dashboard/company/employees/<int:id>/', company_employee_detail_view, name='company-employee-detail'),
    path('dashboard/company/departments/', company_departments_view, name='company-departments'),
    path('dashboard/company/salary-structure/', company_salary_structure_view, name='company-salary-structure'),
    path('dashboard/company/attendance/', company_attendance_view, name='company-attendance'),
    path('dashboard/company/payroll-processing/', company_payroll_view, name='company-payroll'),
    path('dashboard/company/reimbursements/', company_reimbursements_view, name='company-reimbursements'),
    path('dashboard/company/reimbursements/<int:id>/', company_reimbursement_detail_view, name='company-reimbursement-detail'),
    path('dashboard/company/payments/', company_payments_view, name='company-payments'),
    path('dashboard/company/reports/', company_reports_view, name='company-reports'),
]

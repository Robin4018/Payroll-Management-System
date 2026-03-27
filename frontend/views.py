from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from django.contrib.auth.models import User

from django.shortcuts import redirect

def login_required(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # If not authenticated, redirect to login page
            # instead of forcing an identity
            return redirect('login')
        return f(request, *args, **kwargs)
    return decorated_function

import json
from rest_framework_simplejwt.tokens import RefreshToken


@csrf_exempt
def api_login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user) # Creates Session
                
                # Generate JWT
                refresh = RefreshToken.for_user(user)
                
                # Defaults
                employee_name = user.first_name or user.username
                employee_id = None
                
                # Determine role and redirect
                if user.is_superuser or user.is_staff:
                    role = 'admin'
                    from employees.models import UserProfile
                    profile = UserProfile.objects.filter(user=user).first()
                    if profile:
                        org_type = profile.organization_type.lower()
                    else:
                        # NEW: If no profile, don't force one yet, let them choose if it's the first time
                        # or default to COMPANY if it's a superuser login
                        org_type = 'company'
                    
                    redirect_url = f'/dashboard/{org_type}/'
                else:
                    role = 'employee'
                    if not hasattr(user, 'profile'):
                        redirect_url = '/select-entity/'
                    else:
                        org_type = user.profile.organization_type.lower()
                        if org_type == 'company':
                            redirect_url = '/dashboard/company/staff/'
                        else:
                            redirect_url = '/dashboard/staff/'
                    
                if hasattr(user, 'employee'):
                    employee = user.employee
                    employee_name = f"{employee.first_name} {employee.last_name}"
                    employee_id = employee.id
                    if not hasattr(user, 'profile'):
                         redirect_url = '/select-entity/'
                    elif not user.is_superuser:
                         role = 'employee'
                         org_type = user.profile.organization_type.lower()
                         if org_type == 'company':
                             redirect_url = '/dashboard/company/staff/'
                         else:
                             redirect_url = '/dashboard/staff/'
                
                return JsonResponse({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'username': user.username,
                    'role': role,
                    'is_superuser': user.is_superuser,
                    'is_new_user': not hasattr(user, 'profile'),
                    'employee_name': employee_name,
                    'employee_id': employee_id,
                    'redirect': redirect_url
                })
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def login_view(request):
    if request.user.is_authenticated:
        # Already logged in? Take them to their correct dashboard
        if hasattr(request.user, 'profile'):
            org_type = request.user.profile.organization_type.lower()
            return redirect(f'dashboard-{org_type}')
        return redirect('dashboard-default')
    return render(request, 'frontend/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def signup_view(request):
    return render(request, 'frontend/signup.html')

@login_required
def dashboard_view(request):
    return render(request, 'frontend/dashboard.html')

@login_required
def select_entity_view(request):
    # Allow superusers to switch even if they have a profile
    return render(request, 'frontend/select_entity.html')

@login_required
def dashboard_school_view(request):
    return render(request, 'frontend/dashboard_school.html')

@login_required
def dashboard_college_view(request):
    return render(request, 'frontend/dashboard_college.html')

@login_required
def dashboard_company_view(request):
    return render(request, 'frontend/dashboard_company.html')

def school_employees_view(request):
    return render(request, 'frontend/school_employees.html')

def school_payroll_view(request):
    return render(request, 'frontend/school_payroll.html')

def school_structure_view(request):
    return render(request, 'frontend/school_structure.html')

def school_reports_view(request):
    return render(request, 'frontend/school_reports.html')

def school_settings_view(request):
    return render(request, 'frontend/school_settings.html')

def college_employees_view(request):
    return render(request, 'frontend/college_employees.html')

def college_employee_detail_view(request, id):
    return render(request, 'frontend/college_employee_detail.html')

def college_departments_view(request):
    return render(request, 'frontend/college_departments.html')

def college_designations_view(request):
    return render(request, 'frontend/college_designations.html')

def college_salary_structure_view(request):
    tenant_id = None
    if hasattr(request.user, 'employee') and request.user.employee.tenant:
        tenant_id = request.user.employee.tenant.id
    else:
        # Fallback for superuser/admin without employee record
        from tenants.models import Tenant
        tenant = Tenant.objects.filter(type='EDUCATION').first() or Tenant.objects.first()
        if tenant:
            tenant_id = tenant.id
            
    return render(request, 'frontend/college_salary_structure.html', {'tenant_id': tenant_id})

from employees.models import Employee

@login_required
def college_attendance_view(request):
    # Fetch employees (optional: filter by tenant if user has one)
    if hasattr(request.user, 'employee') and request.user.employee.tenant:
        employees = Employee.objects.filter(tenant=request.user.employee.tenant)
    elif request.user.is_superuser:
         # Fallback for superuser
        from tenants.models import Tenant
        tenant = Tenant.objects.filter(type='EDUCATION').first() or Tenant.objects.first()
        employees = Employee.objects.filter(tenant=tenant) if tenant else Employee.objects.all()
    else:
        employees = Employee.objects.all()

    return render(request, 'frontend/college_attendance.html', {
        'employees': list(employees.values('id', 'employee_code', 'first_name', 'last_name', 'department__name'))
    })

def college_payroll_view(request):
    return render(request, 'frontend/college_payroll.html')

def college_payslips_view(request):
    return render(request, 'frontend/college_payslips.html')

def college_compliance_view(request):
    return render(request, 'frontend/college_compliance.html')

def college_bank_payments_view(request):
    return render(request, 'frontend/college_bank_payments.html')

def college_reports_view(request):
    return render(request, 'frontend/college_reports.html')

def college_notifications_view(request):
    return render(request, 'frontend/college_notifications.html')

@login_required
def college_profile_view(request):
    return render(request, 'frontend/college_profile.html')

def college_audit_view(request):
    return render(request, 'frontend/college_audit.html')

def college_tax_declarations_view(request):
    return render(request, 'frontend/college_tax_declarations.html')

def college_loans_view(request):
    return render(request, 'frontend/college_loans.html')

def college_reimbursements_view(request):
    return render(request, 'frontend/college_reimbursements.html')

def college_settings_view(request):
    return render(request, 'frontend/college_settings.html')

def college_compliance_settings_view(request):
    return render(request, 'frontend/college_compliance_settings.html')

def college_help_view(request):
    return render(request, 'frontend/college_help.html')

def college_roles_view(request):
    return render(request, 'frontend/college_roles.html')

# Helper for staff template selection
def get_staff_base_template(user):
    if hasattr(user, 'profile') and user.profile.organization_type == 'COMPANY':
        return 'frontend/dashboard_company_staff_base.html'
    return 'frontend/dashboard_staff_base.html'

@login_required
def staff_dashboard_view(request):
    if hasattr(request.user, 'profile') and request.user.profile.organization_type == 'COMPANY':
        return render(request, 'frontend/company_staff_dashboard.html', {'base_template': get_staff_base_template(request.user)})
    return render(request, 'frontend/staff_dashboard.html', {'base_template': get_staff_base_template(request.user)})

@login_required
def staff_profile_view(request):
    return render(request, 'frontend/staff_profile.html', {'base_template': get_staff_base_template(request.user)})

@login_required
def staff_leaves_view(request):
    return render(request, 'frontend/staff_leaves.html', {'base_template': get_staff_base_template(request.user)})

@login_required
def staff_payslips_view(request):
    return render(request, 'frontend/staff_payslips.html', {'base_template': get_staff_base_template(request.user)})

@login_required
def staff_attendance_view(request):
    return render(request, 'frontend/staff_attendance.html', {'base_template': get_staff_base_template(request.user)})

@login_required
def staff_tax_view(request):
    return render(request, 'frontend/staff_tax.html', {'base_template': get_staff_base_template(request.user), 'title': 'My Tax Declarations'})

@login_required
def staff_reimbursements_view(request):
    return render(request, 'frontend/staff_reimbursements.html', {'base_template': get_staff_base_template(request.user), 'title': 'Reimbursements'})

@login_required
def staff_help_view(request):
    return render(request, 'frontend/staff_help.html', {'base_template': get_staff_base_template(request.user), 'title': 'Help & Support'})

@login_required
def staff_announcements_view(request):
    return render(request, 'frontend/staff_announcements.html', {'base_template': get_staff_base_template(request.user), 'title': 'Notice Board'})

# Corporate Admin Modules
@login_required
def company_employees_view(request):
    return render(request, 'frontend/company_employees.html')

@login_required
def company_employee_detail_view(request, id):
    return render(request, 'frontend/company_employee_detail.html')

# Corporate Staff (Employee) Modules
@login_required
def company_staff_dashboard_view(request):
    return render(request, 'frontend/company_staff_dashboard.html')

@login_required
def company_departments_view(request):
    return render(request, 'frontend/company_departments.html')

@login_required
def company_salary_structure_view(request):
    return render(request, 'frontend/company_salary_structure.html')

@login_required
def company_attendance_view(request):
    return render(request, 'frontend/company_attendance.html')

@login_required
def company_payroll_view(request):
    return render(request, 'frontend/company_payroll.html')

@login_required
def company_reimbursements_view(request):
    return render(request, 'frontend/company_reimbursements.html')

@login_required
def company_reimbursement_detail_view(request, id):
    return render(request, 'frontend/company_reimbursement_detail.html', {'claim_id': id})

@login_required
def company_payments_view(request):
    return render(request, 'frontend/company_payments.html')

@login_required
def company_reports_view(request):
    return render(request, 'frontend/company_reports.html')

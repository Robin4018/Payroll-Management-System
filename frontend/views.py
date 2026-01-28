from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
                
                return JsonResponse({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'username': user.username,
                    'role': 'employee' if hasattr(user, 'employee') else 'admin'
                })
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def login_view(request):
    return render(request, 'frontend/login.html')

def signup_view(request):
    return render(request, 'frontend/signup.html')

def dashboard_view(request):
    return render(request, 'frontend/dashboard.html')

def select_entity_view(request):
    return render(request, 'frontend/select_entity.html')

def dashboard_school_view(request):
    return render(request, 'frontend/dashboard_school.html')

def dashboard_college_view(request):
    return render(request, 'frontend/dashboard_college.html')


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
    return render(request, 'frontend/college_salary_structure.html')

from employees.models import Employee
from django.contrib.auth.decorators import login_required

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

    return render(request, 'frontend/college_attendance.html', {'employees': employees})

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

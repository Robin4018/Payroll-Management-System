from rest_framework import generics, viewsets
from .models import Employee, Department, Designation, EmployeeBankDetails, EmployeeDocument
from .serializers import EmployeeSerializer, DepartmentSerializer, DesignationSerializer, EmployeeBankDetailsSerializer, EmployeeDocumentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status
from django.contrib.auth.models import User

class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'employee') and user.employee.tenant:
            return Employee.objects.filter(tenant=user.employee.tenant)
        
        # Superuser/Admin Fallback: Filter by organization type
        if hasattr(user, 'profile'):
            org_type = user.profile.organization_type
            if org_type == 'COMPANY':
                return Employee.objects.filter(tenant__type='CORPORATE')
            else:
                return Employee.objects.filter(tenant__type='EDUCATION')
        
        return Employee.objects.all()

    def perform_create(self, serializer):
        from tenants.models import Tenant
        user = self.request.user
        
        if hasattr(user, 'employee') and user.employee.tenant:
            tenant = user.employee.tenant
        else:
            # Determine tenant based on organization type
            org_type = getattr(user.profile, 'organization_type', 'COMPANY') if hasattr(user, 'profile') else 'COMPANY'
            tenant_type = 'CORPORATE' if org_type == 'COMPANY' else 'EDUCATION'
            tenant = Tenant.objects.filter(type=tenant_type).first() or Tenant.objects.first()
            
        employee = serializer.save(tenant=tenant)
        
        role_id = self.request.data.get('role_id')
        if role_id and employee.user:
            try:
                group = Group.objects.get(id=role_id)
                employee.user.groups.add(group)
            except Group.DoesNotExist:
                pass

    def perform_update(self, serializer):
        employee = serializer.save()
        role_id = self.request.data.get('role_id')
        if role_id and employee.user:
            employee.user.groups.clear()
            try:
                group = Group.objects.get(id=role_id)
                employee.user.groups.add(group)
            except Group.DoesNotExist:
                pass

    @action(detail=False, methods=['GET'])
    def export_csv(self, request):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="employees.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Email', 'Phone', 'Department', 'Designation', 'Type', 'Status', 'Employee Code', 'Joining Date'])
        
        employees = self.filter_queryset(self.get_queryset())
        for emp in employees:
            writer.writerow([
                emp.first_name,
                emp.last_name,
                emp.email,
                emp.phone,
                emp.department.name if emp.department else '',
                emp.designation_fk.name if emp.designation_fk else emp.designation or '',
                emp.employment_type,
                'Active' if emp.is_active else 'Inactive',
                emp.employee_code,
                emp.date_of_joining
            ])
        
        return response

    @action(detail=False, methods=['POST'])
    def import_csv(self, request):
        import csv
        import io
        from rest_framework.response import Response
        
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not file.name.endswith('.csv'):
            return Response({'error': 'File must be CSV'}, status=status.HTTP_400_BAD_REQUEST)
            
        data_set = file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string) # Skip header
        
        created_count = 0
        errors = []
        
        # Determine Tenant
        from tenants.models import Tenant
        if hasattr(request.user, 'employee') and request.user.employee.tenant:
            tenant = request.user.employee.tenant
        else:
            org_type = getattr(request.user.profile, 'organization_type', 'COMPANY') if hasattr(request.user, 'profile') else 'COMPANY'
            tenant_type = 'CORPORATE' if org_type == 'COMPANY' else 'EDUCATION'
            tenant = Tenant.objects.filter(type=tenant_type).first() or Tenant.objects.first()

        for row in csv.reader(io_string, delimiter=',', quotechar='"'):
            try:
                # Expected: First Name, Last Name, Email, Phone, Dept, Desig, Type, CTC, Joining Date
                if len(row) < 4: continue
                
                first_name = row[0].strip()
                last_name = row[1].strip()
                email = row[2].strip()
                phone = row[3].strip()
                
                if Employee.objects.filter(email=email).exists():
                    errors.append(f"Skipped {email}: Already exists")
                    continue
                    
                # Handle FKs
                dept_name = row[4].strip() if len(row) > 4 else None
                desig_name = row[5].strip() if len(row) > 5 else None
                type_val = row[6].strip().upper() if len(row) > 6 else 'PERMANENT'
                
                department = None
                if dept_name:
                    department, _ = Department.objects.get_or_create(tenant=tenant, name=dept_name)
                    
                designation = None
                if desig_name:
                    designation, _ = Designation.objects.get_or_create(tenant=tenant, name=desig_name, defaults={'department': department})

                joining_date = '2023-01-01' # Default
                
                Employee.objects.create(
                    tenant=tenant,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    department=department,
                    designation_fk=designation,
                    employment_type=type_val,
                    date_of_joining=joining_date
                )
                created_count += 1
                
            except Exception as e:
                errors.append(f"Row Error: {str(e)}")
        
        return Response({
            'message': f'Imported {created_count} employees', 
            'errors': errors
        }, status=status.HTTP_200_OK)

class EmployeeBankDetailsViewSet(viewsets.ModelViewSet):
    queryset = EmployeeBankDetails.objects.all()
    serializer_class = EmployeeBankDetailsSerializer
    
class EmployeeDocumentViewSet(viewsets.ModelViewSet):
    queryset = EmployeeDocument.objects.all()
    serializer_class = EmployeeDocumentSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'employee') and user.employee.tenant:
            return Department.objects.filter(tenant=user.employee.tenant)
        
        if hasattr(user, 'profile'):
            tenant_type = 'CORPORATE' if user.profile.organization_type == 'COMPANY' else 'EDUCATION'
            return Department.objects.filter(tenant__type=tenant_type)
            
        return Department.objects.all()

    def perform_create(self, serializer):
        from tenants.models import Tenant
        user = self.request.user
        if hasattr(user, 'employee') and user.employee.tenant:
            tenant = user.employee.tenant
        else:
            org_type = getattr(user.profile, 'organization_type', 'COMPANY') if hasattr(user, 'profile') else 'COMPANY'
            tenant_type = 'CORPORATE' if org_type == 'COMPANY' else 'EDUCATION'
            tenant = Tenant.objects.filter(type=tenant_type).first() or Tenant.objects.first()
        serializer.save(tenant=tenant)

class DesignationViewSet(viewsets.ModelViewSet):
    serializer_class = DesignationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'employee') and user.employee.tenant:
            return Designation.objects.filter(tenant=user.employee.tenant)
        
        if hasattr(user, 'profile'):
            tenant_type = 'CORPORATE' if user.profile.organization_type == 'COMPANY' else 'EDUCATION'
            return Designation.objects.filter(tenant__type=tenant_type)
            
        return Designation.objects.all()

    def perform_create(self, serializer):
        from tenants.models import Tenant
        user = self.request.user
        if hasattr(user, 'employee') and user.employee.tenant:
            tenant = user.employee.tenant
        else:
            org_type = getattr(user.profile, 'organization_type', 'COMPANY') if hasattr(user, 'profile') else 'COMPANY'
            tenant_type = 'CORPORATE' if org_type == 'COMPANY' else 'EDUCATION'
            tenant = Tenant.objects.filter(type=tenant_type).first() or Tenant.objects.first()
        serializer.save(tenant=tenant)

from django.contrib.auth.models import Group
from .serializers import RoleSerializer

class RoleViewSet(viewsets.ModelViewSet):
    """
    Manage User Roles (Django Groups)
    """
    queryset = Group.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

# ... Keep existing Auth Views ...

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        user = request.user
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_superuser": user.is_superuser,
        }
        
        if user.is_superuser or user.is_staff:
            data['role'] = 'admin'
            data['employee_id'] = None
            if hasattr(user, 'employee'):
                emp = user.employee
                data['employee_id'] = emp.id
                data['employee_name'] = f"{emp.first_name} {emp.last_name}"
                data['designation'] = emp.designation_fk.name if emp.designation_fk else emp.designation
                if emp.profile_photo: data['photo'] = emp.profile_photo.url
        elif hasattr(user, 'employee'):
            emp = user.employee
            data['role'] = 'employee'
            data['employee_id'] = emp.id
            data['employee_name'] = f"{emp.first_name} {emp.last_name}"
            data['designation'] = emp.designation_fk.name if emp.designation_fk else emp.designation
            data['department'] = emp.department.name if emp.department else None
            if emp.profile_photo:
                data['photo'] = emp.profile_photo.url
            else:
                data['photo'] = None
        else:
            # Fallback for new registrants who might not have an employee record yet
            data['role'] = 'admin' if (user.is_superuser or user.is_staff) else 'employee'
            data['employee_id'] = None
        
        if hasattr(user, 'profile'):
            data['organization_type'] = user.profile.organization_type
            
        return Response(data)

    def patch(self, request):
        user = request.user
        emp = getattr(user, 'employee', None)
        
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        profile_photo = request.FILES.get('profile_photo')
        remove_photo = request.data.get('remove_photo')

        if first_name is not None: user.first_name = first_name
        if last_name is not None: user.last_name = last_name
        if email is not None: user.email = email
        user.save()

        # Ensure Identity Record exists (Stable synchronization for Admins)
        from .models import Employee
        from tenants.models import Tenant
        
        if not emp:
            org_type = getattr(user.profile, 'organization_type', 'COMPANY') if hasattr(user, 'profile') else 'COMPANY'
            tenant_type = 'CORPORATE' if org_type == 'COMPANY' else 'EDUCATION'
            tenant = Tenant.objects.filter(type=tenant_type).first() or Tenant.objects.first()
            if tenant:
                emp = Employee.objects.create(
                    user=user,
                    tenant=tenant,
                    first_name=user.first_name or user.username,
                    last_name=user.last_name or "",
                    email=user.email or f"{user.username}@system.local",
                    phone="0000000000",
                    date_of_joining="2024-01-01"
                )

        if emp:
            if first_name is not None: emp.first_name = first_name
            if last_name is not None: emp.last_name = last_name
            if email is not None: emp.email = email
            
            # Handle Photo Synchronization
            if profile_photo:
                emp.profile_photo = profile_photo
            elif remove_photo == 'true' or remove_photo is True:
                emp.profile_photo = None
            
            # Ensure tenant matches organization type for identity record if it was mismatched
            if hasattr(user, 'profile'):
                correct_type = 'CORPORATE' if user.profile.organization_type == 'COMPANY' else 'EDUCATION'
                if emp.tenant.type != correct_type:
                    new_tenant = Tenant.objects.filter(type=correct_type).first()
                    if new_tenant:
                        emp.tenant = new_tenant
                
            emp.save()

        return Response({"message": "Administrative identity synchronized"})

class SetProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from .models import UserProfile
        
        org_type = request.data.get('type')
        if org_type not in ['SCHOOL', 'COLLEGE', 'COMPANY']:
            return Response({"error": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST)

        profile, created = UserProfile.objects.update_or_create(
            user=request.user,
            defaults={'organization_type': org_type}
        )

        # Force tenant re-assignment for superusers/admins based on new choice
        from tenants.models import Tenant
        tenant_type = 'CORPORATE' if org_type == 'COMPANY' else 'EDUCATION'
        target_tenant = Tenant.objects.filter(type=tenant_type).first()
        
        if target_tenant:
            emp = getattr(request.user, 'employee', None)
            if emp:
                emp.tenant = target_tenant
                emp.save()
            else:
                # Create administrative identity if missing
                Employee.objects.create(
                    user=request.user,
                    tenant=target_tenant,
                    first_name=request.user.first_name or request.user.username,
                    last_name=request.user.last_name or "",
                    email=request.user.email or f"{request.user.username}@system.local",
                    date_of_joining="2024-01-01"
                )
        
        # Core Requirement: If Educational Institution selected, prioritize Staff Portal
        redirect_path = f"/dashboard/{org_type.lower()}/"
        role = 'admin' if (request.user.is_superuser or request.user.is_staff) else 'employee'
        
        if org_type == 'COLLEGE' and not request.user.is_superuser:
            redirect_path = "/dashboard/staff/"
            role = 'employee'
            
        return Response({
            "message": "Profile initialized and tenant strictly assigned", 
            "redirect": redirect_path,
            "role": role
        })

class RegisterView(APIView):
    authentication_classes = [] 
    permission_classes = [] 

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        full_name = request.data.get('full_name', '')

        if not username or not password:
            return Response({"error": "Username/Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "An account with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Split full name
        first_name = full_name
        last_name = ""
        if " " in full_name:
            parts = full_name.split(" ", 1)
            first_name = parts[0]
            last_name = parts[1]

        from django.db import transaction
        
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username, 
                    password=password, 
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
        
                # Create/Ensure Employee Profile (Identity Synchronization)
                from .models import Employee
                from tenants.models import Tenant
                
                # Assign to default tenant
                tenant = Tenant.objects.filter(type='EDUCATION').first() or Tenant.objects.first()
                if tenant:
                    # Robust check: if an employee with this email already exists but NO user, link it
                    # otherwise create a new one.
                    emp, created = Employee.objects.get_or_create(
                        email=email or f"{user.username}@system.local",
                        defaults={
                            'user': user,
                            'tenant': tenant,
                            'first_name': first_name,
                            'last_name': last_name,
                            'phone': "0000000000",
                            'date_of_joining': "2024-01-01"
                        }
                    )
                    if not created and not emp.user:
                         emp.user = user
                         emp.save()
                    elif not created and emp.user:
                        # Email conflict - rollback
                        raise Exception("This email is already associated with an account.")

            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Atomic transaction handles user deletion if employee creation fails
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

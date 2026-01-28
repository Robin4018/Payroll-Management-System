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
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def perform_create(self, serializer):
        # Assign tenant from logged-in user context
        if hasattr(self.request.user, 'employee'):
            tenant = self.request.user.employee.tenant
        else:
            # Fallback or Admin logic (fetch first tenant or from profile)
            from tenants.models import Tenant
            tenant = Tenant.objects.first() # TODO: Improve for multi-tenant SAAS
            
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
        if hasattr(request.user, 'employee'):
            tenant = request.user.employee.tenant
        else:
            from tenants.models import Tenant
            tenant = Tenant.objects.first()

        for row in csv.reader(io_string, delimiter=',', quotechar='"'):
            try:
                # Expected: First Name, Last Name, Email, Phone, Dept, Desig, Type, CTC, Joining Date
                # Flexible parsing check
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
                # row[7] CTC? row[8] Joining?
                
                department = None
                if dept_name:
                    department, _ = Department.objects.get_or_create(tenant=tenant, name=dept_name)
                    
                designation = None
                if desig_name:
                    designation, _ = Designation.objects.get_or_create(tenant=tenant, name=desig_name, defaults={'department': department})

                joining_date = '2023-01-01' # Default
                # TODO: Parse date properly if provided
                
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
        # Filter by user's tenant
        if hasattr(self.request.user, 'employee'):
            return Department.objects.filter(tenant=self.request.user.employee.tenant)
        # Fallback for admin or simple reproduction
        return Department.objects.all()

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'employee'):
            tenant = self.request.user.employee.tenant
        else:
             from tenants.models import Tenant
             tenant = Tenant.objects.first()
        serializer.save(tenant=tenant)

class DesignationViewSet(viewsets.ModelViewSet):
    serializer_class = DesignationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'employee'):
            return Designation.objects.filter(tenant=self.request.user.employee.tenant)
        return Designation.objects.all()

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'employee'):
            tenant = self.request.user.employee.tenant
        else:
             from tenants.models import Tenant
             tenant = Tenant.objects.first()
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

class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "username": user.username,
            "is_superuser": user.is_superuser,
        }
        
        if hasattr(user, 'employee'):
            data['role'] = 'employee'
            data['employee_id'] = user.employee.id
            data['employee_name'] = f"{user.employee.first_name} {user.employee.last_name}"
        else:
            data['role'] = 'admin'
        
        if hasattr(user, 'profile'):
            data['organization_type'] = user.profile.organization_type
            
        return Response(data)

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
        
        return Response({"message": "Profile updated", "redirect": f"/dashboard/{org_type.lower()}/"})

class RegisterView(APIView):
    authentication_classes = [] 
    permission_classes = [] 

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password:
            return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)

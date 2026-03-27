from rest_framework import serializers
from .models import Employee, Department, Designation, EmployeeBankDetails, EmployeeDocument

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"
        extra_kwargs = {'tenant': {'read_only': True}}
    
    employee_count = serializers.SerializerMethodField()

    def get_employee_count(self, obj):
        # Count primary + secondary assignments
        primary = obj.employees.count()
        secondary = obj.secondary_employees.count()
        return primary + secondary

class DesignationSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source='department.name')
    
    class Meta:
        model = Designation
        fields = "__all__"
        extra_kwargs = {'tenant': {'read_only': True}}

class EmployeeBankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeBankDetails
        fields = "__all__"
        # extra_kwargs = {'employee': {'read_only': True}} - Removed to allow assigning employee via API

class EmployeeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDocument
        fields = "__all__"

from django.contrib.auth.models import Group

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source='department.name')
    designation_name = serializers.ReadOnlyField(source='designation_fk.name')
    designation_display = serializers.SerializerMethodField()
    profile_photo = serializers.ImageField(required=False, allow_null=True)
    reporting_manager_name = serializers.SerializerMethodField()
    bank_details = EmployeeBankDetailsSerializer(read_only=True)
    documents = EmployeeDocumentSerializer(many=True, read_only=True)
    
    # RBAC / Roles
    role = serializers.SerializerMethodField()
    roles = serializers.PrimaryKeyRelatedField(source='user.groups', many=True, read_only=True)

    class Meta:
        model = Employee
        fields = "__all__"
        extra_kwargs = {
            'tenant': {'read_only': True},
            'employee_code': {'read_only': True, 'required': False}
        }
        
    def get_reporting_manager_name(self, obj):
        if obj.reporting_manager:
            return f"{obj.reporting_manager.first_name} {obj.reporting_manager.last_name}"
        return None

    def get_role(self, obj):
        if obj.user:
            return obj.user.groups.values_list('name', flat=True).first()
        return None

    designation_display = serializers.SerializerMethodField()
    
    def get_designation_display(self, obj):
        return obj.designation_fk.name if obj.designation_fk else (obj.designation or "Staff")

    def get_profile_photo(self, obj):
        if obj.profile_photo:
            return obj.profile_photo.url
        return None

    secondary_department_names = serializers.SerializerMethodField()

    def get_secondary_department_names(self, obj):
        return [d.name for d in obj.secondary_departments.all()]

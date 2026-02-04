from rest_framework import serializers
from .models import SalaryComponent, EmployeeSalaryStructure, PayrollLedger, PayrollAdjustment, SalaryTemplate, SalaryTemplateConfig, Loan, LoanRepayment, Reimbursement
from employees.models import Employee, EmployeeBankDetails

class PayrollAdjustmentSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.first_name')
    class Meta:
        model = PayrollAdjustment
        fields = "__all__"

class EmployeeBankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeBankDetails
        fields = "__all__"

class SalaryComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryComponent
        fields = "__all__"

class EmployeeSalaryStructureSerializer(serializers.ModelSerializer):
    component_name = serializers.ReadOnlyField(source='component.name')
    component_type = serializers.ReadOnlyField(source='component.type')
    
    class Meta:
        model = EmployeeSalaryStructure
        fields = "__all__"

class PayrollLedgerSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all()
    )

    class Meta:
        model = PayrollLedger
        fields = "__all__"

class SalaryTemplateConfigSerializer(serializers.ModelSerializer):
    component_name = serializers.ReadOnlyField(source='component.name')
    component_type = serializers.ReadOnlyField(source='component.type')
    
    class Meta:
        model = SalaryTemplateConfig
        fields = ['id', 'template', 'component', 'component_name', 'component_type', 'default_amount', 'formula']

class SalaryTemplateSerializer(serializers.ModelSerializer):
    configs = SalaryTemplateConfigSerializer(many=True, read_only=True)
    
    class Meta:
        model = SalaryTemplate
        fields = ['id', 'name', 'description', 'configs', 'tenant']

class LoanSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.first_name')
    
    class Meta:
        model = Loan
        fields = "__all__"
        read_only_fields = ['monthly_emi', 'outstanding_balance', 'total_repaid', 'approved_by', 'status']

class LoanRepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRepayment
        fields = "__all__"

class ReimbursementSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.first_name')
    class Meta:
        model = Reimbursement
        fields = "__all__"
        read_only_fields = ['status', 'approved_by', 'payroll_ledger']

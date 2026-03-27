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
        read_only_fields = ('tenant',)

class EmployeeSalaryStructureSerializer(serializers.ModelSerializer):
    component_name = serializers.ReadOnlyField(source='component.name')
    component_type = serializers.ReadOnlyField(source='component.type')
    
    class Meta:
        model = EmployeeSalaryStructure
        fields = "__all__"

class PayrollLedgerSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_code = serializers.ReadOnlyField(source='employee.employee_code')
    bank_details = serializers.SerializerMethodField()

    class Meta:
        model = PayrollLedger
        fields = [
            'id', 'employee', 'employee_name', 'employee_code', 'month',
            'total_earnings', 'total_deductions', 'net_pay',
            'pf_amount', 'esi_amount', 'pt_amount', 'tds_amount',
            'calculations_breakdown', 'status', 'utr_number', 'payment_date',
            'bank_details', 'bank_name', 'bank_account', 'created_at', 'updated_at'
        ]

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    
    bank_name = serializers.ReadOnlyField(source='employee.bank_details.bank_name')
    bank_account = serializers.ReadOnlyField(source='employee.bank_details.account_number')

    def get_bank_details(self, obj):
        if hasattr(obj.employee, 'bank_details'):
            return EmployeeBankDetailsSerializer(obj.employee.bank_details).data
        return None

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
        read_only_fields = ('tenant',)

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
    employee_name = serializers.SerializerMethodField()
    employee_code = serializers.ReadOnlyField(source='employee.employee_code')
    
    class Meta:
        model = Reimbursement
        fields = "__all__"
        read_only_fields = ['status', 'approved_by', 'payroll_ledger']

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"

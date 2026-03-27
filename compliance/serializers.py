from rest_framework import serializers
from .models import StatutoryRate, TaxSlab, TaxDeclaration

class StatutoryRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatutoryRate
        fields = '__all__'

class TaxSlabSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxSlab
        fields = '__all__'

class TaxDeclarationSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.first_name')
    
    class Meta:
        model = TaxDeclaration
        fields = '__all__'
        read_only_fields = ['employee', 'financial_year', 'status', 'approved_by', 'verified_amount', 'total_declared_amount']

from rest_framework import serializers
from .models import Tenant

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'type', 'financial_year_start', 'salary_cycle_start_day', 'tax_slabs', 'logo', 'email', 'phone', 'address']
        read_only_fields = ['id', 'name', 'type'] # Identifying info read-only normally

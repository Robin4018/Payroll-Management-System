from django.contrib import admin
from .models import SalaryComponent, EmployeeSalaryStructure, PayrollLedger

@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'type', 'calculation_type')
    list_filter = ('tenant', 'type', 'calculation_type')
    search_fields = ('name', 'tenant__name')

@admin.register(EmployeeSalaryStructure)
class EmployeeSalaryStructureAdmin(admin.ModelAdmin):
    list_display = ('employee', 'component', 'amount')
    list_filter = ('employee__tenant', 'component')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__employee_code')
    autocomplete_fields = ['employee', 'component']

@admin.register(PayrollLedger)
class PayrollLedgerAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'net_pay', 'status')
    list_filter = ('employee__tenant', 'month', 'status')
    search_fields = ('employee__first_name', 'employee__last_name')

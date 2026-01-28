from django.contrib import admin
from .models import StatutoryRate, TaxSlab, TaxDeclaration

@admin.register(StatutoryRate)
class StatutoryRateAdmin(admin.ModelAdmin):
    list_display = ('type', 'tenant', 'employee_contribution_percent', 'effective_from')
    list_filter = ('type', 'tenant')

@admin.register(TaxSlab)
class TaxSlabAdmin(admin.ModelAdmin):
    list_display = ('regime', 'financial_year', 'min_income', 'max_income', 'tax_rate')
    list_filter = ('regime', 'financial_year')

@admin.register(TaxDeclaration)
class TaxDeclarationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'financial_year', 'regime', 'status', 'verified_amount')
    list_filter = ('status', 'regime', 'financial_year', 'employee__tenant')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__employee_code')

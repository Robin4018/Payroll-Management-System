from django.contrib import admin
from .models import Tenant

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'type', 'is_active', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('type', 'is_active')

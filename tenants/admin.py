from django.contrib import admin
from .models import Tenant

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'latitude', 'longitude', 'geofence_radius', 'is_active')
    search_fields = ('name', 'email')
    list_filter = ('type', 'is_active')

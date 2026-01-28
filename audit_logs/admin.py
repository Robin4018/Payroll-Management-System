from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'actor', 'action', 'target_model', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('actor__username', 'details', 'target_model')
    readonly_fields = ('timestamp', 'actor', 'action', 'target_model', 'target_id', 'details', 'ip_address')

    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

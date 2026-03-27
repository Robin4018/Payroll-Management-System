from tenants.models import Tenant

def tenant_context(request):
    if request.user.is_authenticated:
        tenant = None
        if hasattr(request.user, 'employee') and request.user.employee.tenant:
            tenant = request.user.employee.tenant
        elif request.user.is_superuser:
            tenant = Tenant.objects.first()
        
        if tenant:
            tenant.display_name = tenant.short_name.upper() if tenant.short_name else tenant.name
            return {'current_tenant': tenant}
    return {'current_tenant': None}

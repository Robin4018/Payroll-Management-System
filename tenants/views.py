from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Tenant
from .serializers import TenantSerializer

class TenantSettingsViewSet(viewsets.ModelViewSet):
    """
    API to manage Tenant Settings.
    Ideally, a user belongs to one tenant.
    """
    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only the tenant relevant to the user
        # For now, hardcoding ID 1 or getting from employee profile
        if hasattr(self.request.user, 'employee'):
            return Tenant.objects.filter(id=self.request.user.employee.tenant.id)
        return Tenant.objects.all() # Fallback for superadmin

    @action(detail=False, methods=['get', 'patch'], url_path='current')
    def current(self, request):
        """
        Get or Update the current user's tenant settings.
        """
        # Logic to find tenant
        tenant = None
        if hasattr(request.user, 'employee') and request.user.employee.tenant:
            tenant = request.user.employee.tenant
        elif request.user.is_superuser:
            tenant = Tenant.objects.first()
        
        if not tenant:
            return Response({"error": "No tenant associated with this user"}, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'GET':
            serializer = self.get_serializer(tenant)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = self.get_serializer(tenant, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

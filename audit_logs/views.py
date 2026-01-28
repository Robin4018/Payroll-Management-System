from rest_framework import viewsets, permissions
from .models import AuditLog
from .serializers import AuditLogSerializer

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated] # Should be Admin only ideally

    def get_queryset(self):
        # Filter options
        q = self.queryset
        action = self.request.query_params.get('action')
        if action:
            q = q.filter(action=action)
        return q

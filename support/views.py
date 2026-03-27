from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import SupportTicket, TicketComment
from .serializers import SupportTicketSerializer, TicketCommentSerializer

class SupportTicketViewSet(viewsets.ModelViewSet):
    queryset = SupportTicket.objects.all()
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'employee'):
            return SupportTicket.objects.none()
            
        employee = user.employee
        # If user is superuser or has 'Admin'/'HR' in designation (simple check)
        # Or better: check for specific role if we had a role model.
        # For now, if superuser, show all in tenant.
        if user.is_superuser:
            return SupportTicket.objects.filter(employee__tenant=employee.tenant)
            
        return SupportTicket.objects.filter(employee=employee)

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'employee'):
            serializer.save(employee=self.request.user.employee)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        ticket = self.get_object()
        text = request.data.get('text')
        if not text:
            return Response({"error": "Text required"}, status=400)
            
        comment = TicketComment.objects.create(
            ticket=ticket,
            employee=request.request.user.employee, # Assuming exists
            text=text
        )
        return Response(TicketCommentSerializer(comment).data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = 'CLOSED'
        ticket.resolved_at = timezone.now()
        ticket.save()
        return Response({"status": "Closed"})

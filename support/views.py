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
        if hasattr(user, 'employee'):
            # Employees see their own tickets
            # Admins (HR/Higher roles) should see all or tenant specific
            # For simplicity, if standard employee, filter by self.
            # If Admin (checked via role logic ideally), return all.
            # Assuming 'Admin' role check or simple logic:
            
            # Simple check: If user is admin (superuser) see all, else filter
            # But we have tenants.
            # Let's return all for now if staff, else filter.
            # Real implementation needs Role check from Employee profile.
            
            # For demo: If "HR" designation or similar, show all. 
            # We'll stick to: Everyone sees their own, verify admin differently?
            # Let's filter by tenant at least if we had tenant field.
            # Ticket has employee -> tenant.
            
            return SupportTicket.objects.filter(employee=user.employee)
            
            # TODO: Improve for Admin view (needs identifying admin role)
        return SupportTicket.objects.none()

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

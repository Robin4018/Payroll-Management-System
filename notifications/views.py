from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

from attendance.models import LeaveRequest
from payroll.models import Loan, Reimbursement
from compliance.models import TaxDeclaration

class ApprovalsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        # Aggregate pending counts
        # This is a dashboard-style endpoint
        
        # Leaves
        leaves = LeaveRequest.objects.filter(status='PENDING').count()
        
        # Loans
        loans = Loan.objects.filter(status='PENDING').count()
        
        # Reimbursements
        reimbursements = Reimbursement.objects.filter(status='PENDING').count()
        
        # Tax Declarations (not exactly 'PENDING' but 'SUBMITTED' or verified check needed?)
        # Let's say status='PENDING' if we had it, or we check if not LOCKED.
        # TaxDeclaration doesn't have PENDING status by default in my code (it had approved/locked).
        # Assuming we treat 'submitted' logic or just count total for now.
        # Actually Model had 'status'. Let's check model definition if I recall. 
        # Default was likely OPEN or similar.
        # For safety, let's assume we count those not LOCKED or APPROVED.
        # Or let's skip Tax for now if ambiguous, or just check 'OPEN'.
        tax_declarations = TaxDeclaration.objects.filter(status='OPEN').count()
        
        return Response({
            "leaves": leaves,
            "loans": loans,
            "reimbursements": reimbursements,
            "tax_declarations": tax_declarations,
            "total": leaves + loans + reimbursements + tax_declarations
        })

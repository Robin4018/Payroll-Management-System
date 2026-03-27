from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import StatutoryRate, TaxSlab, TaxDeclaration
from .serializers import StatutoryRateSerializer, TaxSlabSerializer, TaxDeclarationSerializer

class StatutoryRateViewSet(viewsets.ModelViewSet):
    queryset = StatutoryRate.objects.all()
    serializer_class = StatutoryRateSerializer
    # Permission: Admin only for modification, read-only for others? 
    # For now, Authenticated. Logic: Admin manages rates.
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'employee'):
            return self.queryset.filter(tenant=user.employee.tenant)
        return self.queryset

class TaxSlabViewSet(viewsets.ModelViewSet):
    queryset = TaxSlab.objects.all()
    serializer_class = TaxSlabSerializer
    permission_classes = [permissions.IsAuthenticated] # Admin only in UI

class TaxDeclarationViewSet(viewsets.ModelViewSet):
    queryset = TaxDeclaration.objects.all()
    serializer_class = TaxDeclarationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'employee'):
              return self.queryset.filter(employee=user.employee)
        return self.queryset

    def perform_create(self, serializer):
        financial_year = self.request.data.get('financial_year', '2024-2025')
        if hasattr(self.request.user, 'employee'):
            serializer.save(employee=self.request.user.employee, financial_year=financial_year)
        else:
            serializer.save(financial_year=financial_year)

    @action(detail=True, methods=['post'], url_path='verify')
    def verify(self, request, pk=None):
        """
        Admin verifies the declaration amounts.
        """
        declaration = self.get_object()
        verified_amount = request.data.get('verified_amount')
        
        if verified_amount is None:
             return Response({"error": "Verify Amount required"}, status=400)
             
        declaration.verified_amount = verified_amount
        declaration.status = 'APPROVED'
        declaration.approved_by = request.user.employee if hasattr(request.user, 'employee') else None
        declaration.save()
        
        return Response({"status": "Verified"})

    @action(detail=True, methods=['post'], url_path='lock')
    def lock(self, request, pk=None):
        """
        Lock declaration (prevent further edits by employee).
        """
        declaration = self.get_object()
        declaration.status = 'LOCKED'
        declaration.save()
        return Response({"status": "Locked"})

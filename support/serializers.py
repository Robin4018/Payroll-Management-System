from rest_framework import serializers
from .models import SupportTicket, TicketComment

class TicketCommentSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.first_name', read_only=True)
    
    class Meta:
        model = TicketComment
        fields = ['id', 'ticket', 'employee', 'employee_name', 'text', 'created_at']
        read_only_fields = ['employee']

class SupportTicketSerializer(serializers.ModelSerializer):
    comments = TicketCommentSerializer(many=True, read_only=True)
    employee_name = serializers.CharField(source='employee.first_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.first_name', read_only=True)

    class Meta:
        model = SupportTicket
        fields = [
            'id', 'employee', 'employee_name', 'category', 'subject', 'description', 
            'priority', 'status', 'assigned_to', 'assigned_to_name', 
            'resolved_at', 'created_at', 'updated_at', 'comments'
        ]
        read_only_fields = ['employee', 'status', 'assigned_to', 'resolved_at']

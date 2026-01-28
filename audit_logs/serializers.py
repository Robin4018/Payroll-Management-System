from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.ReadOnlyField(source='actor.username')
    actor_email = serializers.ReadOnlyField(source='actor.email')
    
    class Meta:
        model = AuditLog
        fields = '__all__'

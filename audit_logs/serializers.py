from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()
    actor_email = serializers.SerializerMethodField()
    
    def get_actor_name(self, obj):
        return obj.actor.username if obj.actor else "System"
        
    def get_actor_email(self, obj):
        return obj.actor.email if obj.actor else "system@upms.local"
    
    class Meta:
        model = AuditLog
        fields = '__all__'

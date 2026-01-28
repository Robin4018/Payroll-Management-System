from django.db import models
from django.contrib.auth.models import User

class AuditLog(models.Model):
    class Action(models.TextChoices):
        LOGIN = 'LOGIN', 'Login'
        LOGOUT = 'LOGOUT', 'Logout'
        CREATE = 'CREATE', 'Create'
        UPDATE = 'UPDATE', 'Update'
        DELETE = 'DELETE', 'Delete'
        PAYROLL_RUN = 'PAYROLL_RUN', 'Payroll Run'
        OTHER = 'OTHER', 'Other'

    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=Action.choices)
    target_model = models.CharField(max_length=100, blank=True, null=True) # e.g. "EmployeeSalaryStructure"
    target_id = models.CharField(max_length=100, blank=True, null=True)
    details = models.TextField(blank=True, null=True) # JSON or Text description
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.actor} - {self.action} - {self.timestamp}"

from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    class Type(models.TextChoices):
        PAYROLL = 'PAYROLL', 'Payroll'
        LEAVE = 'LEAVE', 'Leave'
        PAYSLIP = 'PAYSLIP', 'Payslip'
        GENERAL = 'GENERAL', 'General'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=Type.choices, default=Type.GENERAL)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # For email/sms tracking
    email_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AuditLog
from payroll.models import EmployeeSalaryStructure, PayrollLedger

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    AuditLog.objects.create(
        actor=user,
        action=AuditLog.Action.LOGIN,
        details=f"User logged in from {ip}",
        ip_address=ip
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    AuditLog.objects.create(
        actor=user,
        action=AuditLog.Action.LOGOUT,
        details="User logged out"
    )

# Salary Change Tracking
@receiver(post_save, sender=EmployeeSalaryStructure)
def log_salary_change(sender, instance, created, **kwargs):
    action = AuditLog.Action.CREATE if created else AuditLog.Action.UPDATE
    # If we had access to 'request.user' here (via middleware thread local) that would be better.
    # For now, leaving actor null or system.
    # We will log the specifics.
    AuditLog.objects.create(
        action=action,
        target_model="EmployeeSalaryStructure",
        target_id=str(instance.id),
        details=f"Salary Structure for {instance.employee} was {action.lower()}d. Component: {instance.component.name}, Amount: {instance.amount}"
    )

from celery import shared_task
from .services import PayrollCalculator
from tenants.models import Tenant
from datetime import datetime

@shared_task
def calculate_payroll_task(tenant_id, month_str):
    """
    Celery task to run payroll calculation in background.
    """
    try:
        tenant = Tenant.objects.get(id=tenant_id)
        month_date = datetime.strptime(month_str, "%Y-%m-%d").date()
        
        calculator = PayrollCalculator(tenant)
        ledgers = calculator.run_payroll_for_tenant(month_date)
        
        # Email Notification
        from django.core.mail import send_mail
        from django.conf import settings
        
        email_count = 0
        for ledger in ledgers:
            try:
                subject = f"Payslip Generated for {month_str}"
                message = f"Dear {ledger.employee.first_name},\n\nYour payslip for {month_str} has been generated.\nNet Pay: {ledger.net_pay}\n\nPlease login to download it.\n\nRegards,\nUPMS"
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [ledger.employee.email],
                    fail_silently=True,
                )
                email_count += 1
            except Exception:
                pass

        return f"Successfully generated {len(ledgers)} payslips for {tenant.name} - {month_str}. Emails Sent: {email_count}"
    except Exception as e:
        return f"Error running payroll for tenant {tenant_id}: {str(e)}"

from django.core.mail import send_mail
from django.conf import settings
from .models import Notification

def send_notification(user, title, message, notif_type=Notification.Type.GENERAL, channels=['db', 'email']):
    """
    Sends notification to user via specified channels.
    channels: list of 'db', 'email', 'sms'
    """
    
    # 1. DB Notification
    if 'db' in channels:
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notif_type
        )
        
    # 2. Email Notification
    if 'email' in channels and user.email:
        try:
            send_mail(
                subject=f"Alert: {title}",
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=True # Fail silently to avoiding blocking main threads
            )
            # Update DB to show sent? (Complex if DB entry not created, but fine)
        except Exception as e:
            print(f"Error sending email: {e}")

    # 3. SMS Notification (Mock)
    if 'sms' in channels:
        # Mock SMS
        print(f"Sending SMS to {user.username}: {message}")

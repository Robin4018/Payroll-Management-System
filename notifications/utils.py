from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
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
                fail_silently=True 
            )
        except Exception as e:
            print(f"Error sending email: {e}")

    # 3. SMS Notification (Mock)
    if 'sms' in channels:
        print(f"Sending SMS to {user.username}: {message}")

def notify_admins(title, message, notif_type=Notification.Type.GENERAL):
    """
    Notifies all administrative users (Superusers and Staff).
    """
    from django.contrib.auth.models import User
    admins = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True))
    for admin in admins:
        send_notification(admin, title, message, notif_type)

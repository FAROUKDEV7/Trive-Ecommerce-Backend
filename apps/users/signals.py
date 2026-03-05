from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User


@receiver(post_save, sender=User)
def create_welcome_notification(sender, instance, created, **kwargs):
    if created:
        try:
            from apps.notifications.models import Notification
            Notification.objects.create(
                user=instance,
                type='welcome',
                title='Welcome to TRIVÉ!',
                message=f'Hi {instance.first_name}! Welcome to TRIVÉ. Discover our latest collections and enjoy exclusive offers.',
            )
        except Exception:
            pass  # Notifications app may not exist yet during migrations
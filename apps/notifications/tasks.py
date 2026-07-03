import logging
from celery import shared_task
from django.apps import apps

logger = logging.getLogger(__name__)

@shared_task
def send_email_task(notification_id, enabled):
    Notification = apps.get_model('notifications', 'Notification')
    try:
        notification = Notification.objects.select_related('user').get(id=notification_id)
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found for email task")
        return

    from .services import _send_email
    _send_email(notification, enabled)

@shared_task
def send_push_task(notification_id, enabled):
    Notification = apps.get_model('notifications', 'Notification')
    try:
        notification = Notification.objects.select_related('user').get(id=notification_id)
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found for push task")
        return

    from .services import _send_push
    _send_push(notification, enabled)

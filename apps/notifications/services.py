from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone

from .models import Notification, NotificationDelivery, NotificationPreference, PushDevice


User = get_user_model()
logger = logging.getLogger(__name__)


def get_staff_users():
    return User.objects.filter(is_active=True).filter(Q(is_staff=True) | Q(is_advisor=True)).distinct()


def get_or_create_preferences(user):
    prefs, _ = NotificationPreference.objects.get_or_create(user=user)
    return prefs


def _notification_group(user_id):
    return f'notifications_user_{user_id}'


def _serialize_notification(notification):
    return {
        'id': notification.id,
        'title': notification.title,
        'message': notification.message,
        'link': notification.link,
        'notification_type': notification.notification_type,
        'category': notification.category,
        'priority': notification.priority,
        'is_read': notification.is_read,
        'created_at': notification.created_at.isoformat(),
    }


def _delivery_record(notification, channel, status='queued', recipient='', error='', provider_message_id=''):
    return NotificationDelivery.objects.create(
        notification=notification,
        channel=channel,
        status=status,
        recipient=recipient,
        provider_message_id=provider_message_id,
        error=error,
        sent_at=timezone.now() if status == 'sent' else None,
    )


def _send_in_app(notification, enabled):
    if not enabled:
        _delivery_record(notification, 'in_app', status='skipped', error='disabled by preferences')
        return

    _delivery_record(notification, 'in_app', status='sent')
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        _notification_group(notification.user_id),
        {
            'type': 'notify_event',
            'notification': _serialize_notification(notification),
        },
    )


def _send_email(notification, enabled):
    recipient = notification.user.email or ''
    if not enabled:
        _delivery_record(notification, 'email', status='skipped', recipient=recipient, error='disabled by preferences')
        return
    if not recipient:
        _delivery_record(notification, 'email', status='skipped', error='missing recipient')
        return
    if not getattr(notification.user, 'email_consent', True):
        _delivery_record(notification, 'email', status='skipped', recipient=recipient, error='email consent disabled')
        return

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', '') or getattr(settings, 'EMAIL_HOST_USER', '') or 'no-reply@Visanextstep.local'
    try:
        send_mail(
            subject=notification.title,
            message=notification.message,
            from_email=from_email,
            recipient_list=[recipient],
            fail_silently=False,
        )
        _delivery_record(notification, 'email', status='sent', recipient=recipient)
    except Exception as exc:
        _delivery_record(notification, 'email', status='failed', recipient=recipient, error=str(exc))


@lru_cache(maxsize=1)
def _get_firebase_app():
    if not getattr(settings, 'FCM_ENABLED', False):
        return None, 'fcm disabled in settings'

    credentials_file = getattr(settings, 'FCM_CREDENTIALS_FILE', None)
    if not credentials_file:
        return None, 'missing FCM_CREDENTIALS_FILE'

    try:
        import firebase_admin
        from firebase_admin import credentials
    except ImportError:
        return None, 'firebase_admin package not installed'

    try:
        return firebase_admin.get_app(), ''
    except ValueError:
        pass

    credentials_path = Path(str(credentials_file))
    if not credentials_path.exists():
        return None, f'credentials file not found: {credentials_path}'

    options = {}
    project_id = getattr(settings, 'FCM_PROJECT_ID', '').strip()
    if project_id:
        options['projectId'] = project_id

    try:
        app = firebase_admin.initialize_app(
            credentials.Certificate(str(credentials_path)),
            options or None,
        )
        return app, ''
    except Exception as exc:
        logger.exception('Firebase init failed')
        return None, str(exc)


def _is_invalid_push_token(error_text):
    text = (error_text or '').upper()
    invalid_markers = (
        'UNREGISTERED',
        'NOT REGISTERED',
        'INVALID REGISTRATION TOKEN',
        'REGISTRATION TOKEN IS NOT A VALID',
    )
    return any(marker in text for marker in invalid_markers)


def _send_push(notification, enabled):
    devices = PushDevice.objects.filter(user=notification.user, is_active=True)
    if not enabled:
        _delivery_record(notification, 'push', status='skipped', error='disabled by preferences')
        return
    if not devices.exists():
        _delivery_record(notification, 'push', status='skipped', error='no active push device')
        return

    firebase_app, init_error = _get_firebase_app()
    if not firebase_app:
        status = 'skipped' if init_error == 'fcm disabled in settings' else 'failed'
        for device in devices:
            _delivery_record(
                notification,
                'push',
                status=status,
                recipient=device.token[:16],
                error=init_error,
            )
        return

    try:
        from firebase_admin import messaging
    except ImportError:
        for device in devices:
            _delivery_record(
                notification,
                'push',
                status='failed',
                recipient=device.token[:16],
                error='firebase_admin.messaging unavailable',
            )
        return

    payload = {
        'notification_id': str(notification.id),
        'notification_type': str(notification.notification_type),
        'category': str(notification.category),
        'priority': str(notification.priority),
        'link': str(notification.link or ''),
    }
    for key, value in (notification.payload or {}).items():
        if value is None:
            continue
        payload[str(key)] = str(value)

    for device in devices:
        message = messaging.Message(
            token=device.token,
            notification=messaging.Notification(
                title=notification.title,
                body=notification.message,
            ),
            data=payload,
        )
        dry_run = bool(getattr(settings, 'FCM_DRY_RUN', False))
        try:
            provider_message_id = messaging.send(message, app=firebase_app, dry_run=dry_run)
            _delivery_record(
                notification,
                'push',
                status='sent',
                recipient=device.token[:16],
                provider_message_id=provider_message_id,
            )
        except Exception as exc:
            err = str(exc)
            _delivery_record(
                notification,
                'push',
                status='failed',
                recipient=device.token[:16],
                error=err,
            )
            if _is_invalid_push_token(err):
                device.is_active = False
                device.save(update_fields=['is_active', 'last_seen_at'])


def _resolve_channel_policy(preferences, category, priority):
    enabled = {
        'in_app': preferences.is_channel_enabled(category, 'in_app'),
        'email': preferences.is_channel_enabled(category, 'email'),
        'push': preferences.is_channel_enabled(category, 'push'),
    }

    # Escalation by priority.
    if priority == 'critical':
        enabled['in_app'] = True
        enabled['email'] = True
        enabled['push'] = True
    elif priority == 'high':
        enabled['in_app'] = True
        enabled['push'] = True
    return enabled


def dispatch_notification(
    *,
    user,
    title,
    message,
    notification_type='general',
    category='system',
    priority='normal',
    link='',
    payload=None,
    created_by=None,
    audience=None,
):
    if audience is None:
        audience = 'staff' if (user.is_staff or user.is_advisor) else 'student'

    notification = Notification.objects.create(
        user=user,
        created_by=created_by,
        audience=audience,
        category=category,
        priority=priority,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link or '',
        payload=payload or {},
    )

    preferences = get_or_create_preferences(user)
    channel_policy = _resolve_channel_policy(preferences, category, priority)
    _send_in_app(notification, channel_policy['in_app'])
    
    from .tasks import send_email_task, send_push_task
    send_email_task.delay(notification.id, channel_policy['email'])
    send_push_task.delay(notification.id, channel_policy['push'])
    return notification


def dispatch_bulk(users: Iterable, **kwargs):
    notifications = []
    for user in users:
        notifications.append(dispatch_notification(user=user, **kwargs))
    return notifications


def notify_staff(**kwargs):
    users = get_staff_users()
    seen = set()
    out = []
    for user in users:
        if user.id in seen:
            continue
        seen.add(user.id)
        out.append(dispatch_notification(user=user, audience='staff', **kwargs))
    return out


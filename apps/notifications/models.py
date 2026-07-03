from django.db import models
from django.conf import settings


class Notification(models.Model):
    AUDIENCE_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Staff'),
    ]
    CATEGORY_CHOICES = [
        ('document', 'Document'),
        ('chat', 'Chat'),
        ('meeting', 'Meeting'),
        ('billing', 'Billing'),
        ('system', 'System'),
    ]
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('normal', 'Normal'),
        ('low', 'Low'),
    ]
    TYPE_CHOICES = [
        ('document_approved','Document Approved'),
        ('document_rejected','Document Rejected'),
        ('new_message','New Message'),
        ('meeting_confirmed','Meeting Confirmed'),
        ('payment_success','Payment Successful'),
        ('reminder','Reminder'),
        ('staff_new_document', 'Staff New Document'),
        ('staff_new_message', 'Staff New Message'),
        ('staff_meeting_booked', 'Staff Meeting Booked'),
        ('staff_payment_pending', 'Staff Payment Pending'),
        ('general','General'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_notifications',
    )
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='student')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='system')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='general')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    link = models.CharField(max_length=200, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"


def default_category_channels():
    return {
        'document': {'in_app': True, 'email': True, 'push': False},
        'chat': {'in_app': True, 'email': False, 'push': True},
        'meeting': {'in_app': True, 'email': True, 'push': True},
        'billing': {'in_app': True, 'email': True, 'push': False},
        'system': {'in_app': True, 'email': False, 'push': False},
    }


class NotificationPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    in_app_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=False)
    digest_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    category_channels = models.JSONField(default=default_category_channels, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification prefs — {self.user.email}"

    def is_channel_enabled(self, category, channel):
        channel = (channel or '').strip()
        if channel not in {'in_app', 'email', 'push'}:
            return False

        global_toggle = {
            'in_app': self.in_app_enabled,
            'email': self.email_enabled,
            'push': self.push_enabled,
        }[channel]
        if not global_toggle:
            return False

        categories = self.category_channels or {}
        category_cfg = categories.get(category) or categories.get('system') or {}
        return bool(category_cfg.get(channel, False))


class PushDevice(models.Model):
    PLATFORM_CHOICES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='push_devices')
    token = models.CharField(max_length=255, unique=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='web')
    is_active = models.BooleanField(default=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.email} — {self.platform}"


class NotificationDelivery(models.Model):
    CHANNEL_CHOICES = [
        ('in_app', 'In App'),
        ('email', 'Email'),
        ('push', 'Push'),
    ]
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]

    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='deliveries')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    recipient = models.CharField(max_length=255, blank=True)
    provider_message_id = models.CharField(max_length=255, blank=True)
    error = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['channel', 'status']),
        ]

    def __str__(self):
        return f"{self.notification_id} — {self.channel} — {self.status}"

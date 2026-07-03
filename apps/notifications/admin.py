from django.contrib import admin

from .models import Notification, NotificationDelivery, NotificationPreference, PushDevice


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'audience', 'category', 'priority', 'notification_type', 'is_read', 'created_at')
    list_filter = ('audience', 'category', 'priority', 'notification_type', 'is_read')
    search_fields = ('user__email', 'title', 'message')
    ordering = ('-created_at',)


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'in_app_enabled', 'email_enabled', 'push_enabled', 'digest_enabled', 'updated_at')
    search_fields = ('user__email',)


@admin.register(PushDevice)
class PushDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'is_active', 'last_seen_at', 'created_at')
    list_filter = ('platform', 'is_active')
    search_fields = ('user__email', 'token')


@admin.register(NotificationDelivery)
class NotificationDeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'notification', 'channel', 'status', 'recipient', 'sent_at', 'created_at')
    list_filter = ('channel', 'status')
    search_fields = ('notification__title', 'notification__user__email', 'recipient', 'error')
    ordering = ('-created_at',)

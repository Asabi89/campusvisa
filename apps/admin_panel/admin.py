from django.contrib import admin

from .models import PlatformSetting


@admin.register(PlatformSetting)
class PlatformSettingAdmin(admin.ModelAdmin):
    list_display = (
        'platform_name',
        'default_student_language',
        'maintenance_mode',
        'broadcast_enabled',
        'updated_at',
    )
    list_filter = ('default_student_language', 'maintenance_mode', 'broadcast_enabled')
    search_fields = ('platform_name', 'support_email', 'support_phone')
    readonly_fields = ('updated_at',)
    fieldsets = (
        ('General', {
            'fields': ('platform_name', 'default_student_language'),
        }),
        ('Support', {
            'fields': ('support_email', 'support_phone'),
        }),
        ('Feature Flags', {
            'fields': ('maintenance_mode', 'broadcast_enabled'),
        }),
        ('Meta', {
            'fields': ('updated_at',),
        }),
    )

    def has_add_permission(self, request):
        # Keep a single settings row.
        if PlatformSetting.objects.exists():
            return False
        return super().has_add_permission(request)

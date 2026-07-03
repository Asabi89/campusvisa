from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, StaffAccount


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'email', 'username', 'first_name', 'last_name',
        'is_student', 'is_advisor', 'is_staff', 'is_superuser', 'has_active_plan',
    )
    list_filter = ('is_student', 'is_advisor', 'is_staff', 'is_superuser', 'has_active_plan')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
    actions = ('make_staff', 'remove_staff', 'make_advisor', 'remove_advisor')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'password1', 'password2',
                'first_name', 'last_name',
                'is_active', 'is_staff', 'is_superuser',
                'is_student', 'is_advisor',
            ),
        }),
    )

    fieldsets = UserAdmin.fieldsets + (
        ('Visanextstep', {
            'fields': (
                'phone', 'country_of_residence', 'preferred_language',
                'email_consent', 'whatsapp_opt_in',
                'terms_accepted', 'privacy_accepted',
                'is_student', 'is_advisor',
                'has_completed_onboarding', 'has_active_plan',
                'created_at', 'updated_at',
            ),
        }),
    )

    @admin.action(description='Mark selected users as staff')
    def make_staff(self, request, queryset):
        queryset.update(is_staff=True)

    @admin.action(description='Remove staff access from selected users')
    def remove_staff(self, request, queryset):
        queryset.update(is_staff=False)

    @admin.action(description='Mark selected users as advisor')
    def make_advisor(self, request, queryset):
        queryset.update(is_advisor=True, is_student=False)

    @admin.action(description='Remove advisor role from selected users')
    def remove_advisor(self, request, queryset):
        queryset.update(is_advisor=False)


@admin.register(StaffAccount)
class StaffAccountAdmin(UserAdmin):
    model = StaffAccount
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_advisor', 'is_active')
    list_filter = ('is_superuser', 'is_advisor', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'password1', 'password2',
                'first_name', 'last_name',
                'is_active', 'is_superuser', 'is_advisor',
            ),
        }),
    )

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'country_of_residence', 'preferred_language')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Visanextstep', {'fields': ('is_advisor', 'is_student', 'has_completed_onboarding', 'has_active_plan')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=True)

    def save_model(self, request, obj, form, change):
        obj.is_staff = True
        if obj.is_advisor:
            obj.is_student = False
        super().save_model(request, obj, form, change)


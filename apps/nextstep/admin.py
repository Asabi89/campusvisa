from django.contrib import admin
from .models import NextStepSettings, NextStepFAQ, NextStepService, NextStepTestimonial

@admin.register(NextStepSettings)
class NextStepSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'updated_at')

    def has_add_permission(self, request):
        if NextStepSettings.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(NextStepFAQ)
class NextStepFAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('question', 'answer')

@admin.register(NextStepService)
class NextStepServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'description')

@admin.register(NextStepTestimonial)
class NextStepTestimonialAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'program', 'rating', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('student_name', 'content')

from .models import (
    NextstepHomePageSettings,
    CampusFrancePageSettings,
    ContactPageSettings,
    FAQPageSettings,
    MentionsLegalesSettings
)

class SingletonModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

@admin.register(NextstepHomePageSettings)
class NextstepHomePageSettingsAdmin(SingletonModelAdmin): pass

@admin.register(CampusFrancePageSettings)
class CampusFrancePageSettingsAdmin(SingletonModelAdmin): pass

@admin.register(ContactPageSettings)
class ContactPageSettingsAdmin(SingletonModelAdmin): pass

@admin.register(FAQPageSettings)
class FAQPageSettingsAdmin(SingletonModelAdmin): pass

@admin.register(MentionsLegalesSettings)
class MentionsLegalesSettingsAdmin(SingletonModelAdmin): pass


from django.contrib import admin
from .models import SiteSettings

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    # Only allow 1 instance of this model
    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

from .models import (
    HomePageSettings,
    PresentationItem,
    FeatureItem,
    ProcessStep,
    AdvantageItem,
    Testimonial
)

@admin.register(HomePageSettings)
class HomePageSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

@admin.register(PresentationItem)
class PresentationItemAdmin(admin.ModelAdmin):
    list_display = ('text', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('text',)

@admin.register(FeatureItem)
class FeatureItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'description')

@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'description')

@admin.register(AdvantageItem)
class AdvantageItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_highlighted', 'order', 'is_active')
    list_editable = ('is_highlighted', 'order', 'is_active')
    search_fields = ('title', 'description')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'subtitle', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'quote')


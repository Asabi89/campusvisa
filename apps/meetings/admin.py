from django.contrib import admin

from .models import AvailableSlot, Meeting


admin.site.register(AvailableSlot)
admin.site.register(Meeting)

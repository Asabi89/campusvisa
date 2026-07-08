"""
URL configuration for the admin subdomain (admin.campusvisa.com).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

# Customize Django Administration header and titles
admin.site.site_header = "Nextstep Consulting"
admin.site.site_title = "Nextstep Consulting Admin"
admin.site.index_title = "Administration Nextstep Consulting"

urlpatterns = [
    path('', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

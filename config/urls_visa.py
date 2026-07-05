from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path('', include('apps.pages.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('auth/', include(('allauth.urls', 'allauth'), namespace='allauth')),
    path('onboarding/', include('apps.onboarding.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('documents/', include('apps.documents.urls')),
    path('chat/', include('apps.chat.urls')),
    path('meetings/', include('apps.meetings.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('plans/', include('apps.plans.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

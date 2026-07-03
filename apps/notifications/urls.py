from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.list_notifications, name='list'),
    path('mark-read/<int:pk>/', views.mark_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('preferences/', views.update_preferences, name='preferences'),
    path('push/register/', views.push_register, name='push_register'),
    path('push/unregister/', views.push_unregister, name='push_unregister'),
]

from django.urls import path

from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Auth
    path('login/', views.staff_login, name='login'),
    path('logout/', views.staff_logout, name='logout'),

    # Overview
    path('', views.overview, name='overview'),

    # Students
    path('students/', views.students_list, name='students'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),

    # Documents
    path('documents/', views.documents_list, name='documents'),
    path('documents/student/<int:pk>/', views.student_documents, name='student_documents'),
    path('documents/<int:pk>/review/', views.document_review, name='document_review'),
    path('documents/bulk-review/', views.documents_bulk_review, name='documents_bulk_review'),

    # Document Types
    path('document-types/', views.document_types_list, name='document_types'),
    path('document-types/reorder/', views.document_types_reorder, name='document_types_reorder'),

    # Meetings & Slots
    path('meetings/', views.meetings_list, name='meetings'),
    path('meetings/slot/create/', views.slot_create, name='slot_create'),
    path('meetings/slots/bulk/', views.slots_bulk_create, name='slots_bulk_create'),
    path('meetings/slot/<int:pk>/delete/', views.slot_delete, name='slot_delete'),
    path('meetings/<int:pk>/update/', views.meeting_update, name='meeting_update'),

    # Chat / Messages
    path('messages/', views.messages_list, name='messages'),
    path('messages/<int:pk>/', views.chat_detail, name='chat_detail'),
    path('messages/<int:pk>/toggle-urgent/', views.room_toggle_urgent, name='room_toggle_urgent'),
    path('messages/bulk-urgent/', views.rooms_bulk_urgent, name='rooms_bulk_urgent'),
    path('messages/message/<int:pk>/toggle-priority/', views.message_toggle_priority, name='message_toggle_priority'),

    # Subscriptions
    path('subscriptions/', views.subscriptions_list, name='subscriptions'),
    path('subscriptions/<int:pk>/update/', views.subscription_update, name='subscription_update'),

    # Plans
    path('plans/', views.plans_list, name='plans'),

    # Notifications
    path('notifications/', views.notifications_list, name='notifications'),
    path('notifications/read/<int:pk>/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/read-all/', views.notification_mark_all_read, name='notification_mark_all_read'),

    # Settings
    path('settings/', views.settings_view, name='settings'),
]

from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.overview, name='overview'),
    path('documents/', views.documents, name='documents'),
    path('documents/<slug:slug>/telecharger/', views.document_upload, name='document_upload'),
    path('messages/', views.chat_view, name='messages'),
    path('rendez-vous/', views.meetings, name='meetings'),
    path('profil/', views.profile, name='profile'),
    path('profil/avatar/', views.avatar_upload, name='avatar_upload'),
    path('mon-plan/', views.plan_detail, name='plan'),
]

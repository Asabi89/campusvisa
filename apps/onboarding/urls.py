from django.urls import path

from . import views

app_name = 'onboarding'

urlpatterns = [
    path('', views.questionnaire, name='questionnaire'),
    path('result/', views.result, name='result'),
    path('reset/', views.reset, name='reset'),
]

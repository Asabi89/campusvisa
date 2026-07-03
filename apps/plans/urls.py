from django.urls import path

from . import views

app_name = 'plans'

urlpatterns = [
    path('checkout/<slug:slug>/', views.checkout, name='checkout'),
    path('confirmation/<slug:slug>/', views.confirmation, name='confirmation'),
]

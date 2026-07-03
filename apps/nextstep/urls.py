from django.urls import path
from . import views

app_name = 'nextstep'

urlpatterns = [
    path('', views.home, name='home'),
    path('campus-france/', views.campus_france, name='campus_france'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('mentions-legales/', views.mentions_legales, name='mentions_legales'),
]

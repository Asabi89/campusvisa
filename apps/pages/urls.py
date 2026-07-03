from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('pricing/', views.pricing, name='pricing'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
]

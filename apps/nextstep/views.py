from django.shortcuts import render
from .models import NextStepFAQ, NextStepService, NextStepTestimonial

def home(request):
    if 'visa.nextstepc.com' in request.get_host():
        from apps.pages.views import home as visa_home
        return visa_home(request)

    context = {
        'services': NextStepService.objects.filter(is_active=True).order_by('order'),
        'testimonials': NextStepTestimonial.objects.filter(is_active=True),
        'faqs': NextStepFAQ.objects.filter(is_active=True).order_by('order')[:5], # Only show top 5 FAQs on home
    }
    return render(request, 'nextstep/home_nextstep.html', context)

def campus_france(request):
    return render(request, 'nextstep/campus_france_nextstep.html')

def contact(request):
    return render(request, 'nextstep/contact_nextstep.html')

def faq(request):
    context = {
        'faqs': NextStepFAQ.objects.filter(is_active=True).order_by('order'),
    }
    return render(request, 'nextstep/faq_nextstep.html', context)

def mentions_legales(request):
    return render(request, 'nextstep/mentions_legales_nextstep.html')

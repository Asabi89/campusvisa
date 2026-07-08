from django.shortcuts import render
from .models import (
    NextStepFAQ, NextStepService, NextStepTestimonial, NextStepAdvantage,
    NextstepHomePageSettings, CampusFrancePageSettings,
    ContactPageSettings, FAQPageSettings, MentionsLegalesSettings
)

def home(request):
    home_settings = NextstepHomePageSettings.get_solo()
    context = {
        'home_settings': home_settings,
        'services': NextStepService.objects.filter(is_active=True).order_by('order'),
        'advantages': NextStepAdvantage.objects.filter(is_active=True).order_by('order'),
        'testimonials': NextStepTestimonial.objects.filter(is_active=True),
        'faqs': NextStepFAQ.objects.filter(is_active=True).order_by('order')[:5], # Only show top 5 FAQs on home
    }
    return render(request, 'nextstep/home_nextstep.html', context)

def campus_france(request):
    context = {'page_settings': CampusFrancePageSettings.get_solo()}
    return render(request, 'nextstep/campus_france_nextstep.html', context)

def contact(request):
    context = {'page_settings': ContactPageSettings.get_solo()}
    return render(request, 'nextstep/contact_nextstep.html', context)

def faq(request):
    context = {
        'page_settings': FAQPageSettings.get_solo(),
        'faqs': NextStepFAQ.objects.filter(is_active=True).order_by('order'),
    }
    return render(request, 'nextstep/faq_nextstep.html', context)

def mentions_legales(request):
    context = {'page_settings': MentionsLegalesSettings.get_solo()}
    return render(request, 'nextstep/mentions_legales_nextstep.html', context)

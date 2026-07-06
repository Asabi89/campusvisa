from django.shortcuts import render
from .models import (
    HomePageSettings, PresentationItem, FeatureItem,
    ProcessStep, AdvantageItem, Testimonial
)

def home(request):
    home_settings = HomePageSettings.get_solo()
    presentation_items = PresentationItem.objects.filter(is_active=True)
    features = FeatureItem.objects.filter(is_active=True)
    process_steps = ProcessStep.objects.filter(is_active=True)
    advantages = AdvantageItem.objects.filter(is_active=True)
    testimonials = Testimonial.objects.filter(is_active=True)
    
    context = {
        'home_settings': home_settings,
        'presentation_items': presentation_items,
        'features': features,
        'process_steps': process_steps,
        'advantages': advantages,
        'testimonials': testimonials,
    }
    return render(request, 'pages/home.html', context)

def about(request):
    return render(request, 'pages/about.html')

def services(request):
    return render(request, 'pages/services.html')

def pricing(request):
    return render(request, 'pages/pricing.html')

def how_it_works(request):
    return render(request, 'pages/how_it_works.html')

def testimonials(request):
    return render(request, 'pages/testimonials.html')

def faq(request):
    return render(request, 'pages/faq.html')

def contact(request):
    return render(request, 'pages/contact.html')

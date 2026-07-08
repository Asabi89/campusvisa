from django.shortcuts import render
from .models import (
    HomePageSettings, PresentationItem, FeatureItem,
    ProcessStep, AdvantageItem, Testimonial,
    AboutPageSettings, ServicesPageSettings, PricingPageSettings,
    HowItWorksPageSettings, TestimonialsPageSettings, FAQPageSettings,
    ContactPageSettings, PricingPlan, PricingFeature
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
    context = {'page_settings': AboutPageSettings.get_solo()}
    return render(request, 'pages/about.html', context)

def services(request):
    context = {'page_settings': ServicesPageSettings.get_solo()}
    return render(request, 'pages/services.html', context)

def pricing(request):
    context = {
        'page_settings': PricingPageSettings.get_solo(),
        'plans': PricingPlan.objects.filter(is_active=True).order_by('order'),
        'features': PricingFeature.objects.all().order_by('order'),
    }
    return render(request, 'pages/pricing.html', context)

def how_it_works(request):
    context = {'page_settings': HowItWorksPageSettings.get_solo()}
    return render(request, 'pages/how_it_works.html', context)

def testimonials(request):
    context = {'page_settings': TestimonialsPageSettings.get_solo()}
    return render(request, 'pages/testimonials.html', context)

def faq(request):
    context = {'page_settings': FAQPageSettings.get_solo()}
    return render(request, 'pages/faq.html', context)

def contact(request):
    context = {'page_settings': ContactPageSettings.get_solo()}
    return render(request, 'pages/contact.html', context)

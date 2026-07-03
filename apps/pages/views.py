from django.shortcuts import render

def home(request):
    return render(request, 'pages/home.html')

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

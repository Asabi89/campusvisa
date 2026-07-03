from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import CustomLoginForm, CustomSignupForm


def signup_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser or request.user.is_advisor:
            return redirect('admin_panel:overview')
        return redirect('dashboard:overview')

    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Compte cree avec succes. Bienvenue.')
            if not user.has_completed_onboarding:
                return redirect('onboarding:questionnaire')
            next_url = request.POST.get('next') or reverse('dashboard:overview')
            return redirect(next_url)
    else:
        form = CustomSignupForm()

    return render(
        request,
        'account/signup.html',
        {
            'form': form,
            'next': request.GET.get('next', ''),
        },
    )


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser or request.user.is_advisor:
            return redirect('admin_panel:overview')
        return redirect('dashboard:overview')

    if request.method == 'POST':
        form = CustomLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if form.cleaned_data.get('remember_me'):
                request.session.set_expiry(60 * 60 * 24 * 30)
            else:
                request.session.set_expiry(0)

            if user.is_staff or user.is_superuser or user.is_advisor:
                return redirect('admin_panel:overview')
            messages.success(request, 'Connexion reussie.')
            if not user.has_completed_onboarding:
                return redirect('onboarding:questionnaire')
            if not user.has_active_plan:
                return redirect('onboarding:result')
            next_url = request.POST.get('next') or reverse('dashboard:overview')
            return redirect(next_url)
    else:
        form = CustomLoginForm(request=request)

    return render(
        request,
        'account/login.html',
        {
            'form': form,
            'next': request.GET.get('next', ''),
        },
    )


def logout_view(request):
    logout(request)
    messages.info(request, 'Vous etes deconnecte.')
    return redirect('pages:home')

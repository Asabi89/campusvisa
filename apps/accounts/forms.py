import re

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django_countries.fields import CountryField
from phonenumber_field.formfields import PhoneNumberField


class CustomSignupForm(forms.Form):
    first_name = forms.CharField(max_length=150, label='Prenom')
    last_name = forms.CharField(max_length=150, label='Nom')
    email = forms.EmailField(label='Email')
    phone = PhoneNumberField(
        label='Telephone',
        required=False,
        region='FR',
    )
    country_of_residence = CountryField(blank_label='Selectionnez votre pays').formfield(label='Pays de residence')
    preferred_language = forms.ChoiceField(
        label='Langue preferee',
        choices=(('fr', 'Francais'), ('en', 'English')),
        initial='fr',
    )
    password1 = forms.CharField(widget=forms.PasswordInput, label='Mot de passe')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirmer le mot de passe')
    terms_accepted = forms.BooleanField(
        label="J'accepte les conditions d'utilisation",
        required=True,
    )
    privacy_accepted = forms.BooleanField(
        label="J'accepte la politique de confidentialite",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'h-4 w-4 rounded border-gray-300 text-secondary focus:ring-secondary',
                })
                continue
            attrs = {
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-900 text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-secondary/30 focus:border-secondary transition-colors',
                'placeholder': field.label,
            }
            if name == 'last_name':
                attrs['placeholder'] = 'Exemple: Kendou'
            if name == 'first_name':
                attrs['placeholder'] = 'Exemple: Ola'
            if name == 'email':
                attrs['placeholder'] = 'Exemple: ola.kendou@email.com'
            if name == 'phone':
                attrs['placeholder'] = 'Exemple: +33 6 12 34 56 78'
                attrs['type'] = 'tel'
            field.widget.attrs.update(attrs)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        UserModel = get_user_model()
        if UserModel.objects.filter(email=email).exists():
            raise forms.ValidationError('Un compte avec cet email existe deja.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Les deux mots de passe ne correspondent pas.')
        return cleaned_data

    def _generate_username(self):
        first_name = self.cleaned_data.get('first_name', '')
        last_name = self.cleaned_data.get('last_name', '')
        email = self.cleaned_data.get('email', '')
        base = f'{first_name}{last_name}'.strip().lower()
        if not base:
            base = email.split('@')[0]
        base = re.sub(r'[^a-z0-9_]+', '', base)[:20] or 'student'

        UserModel = get_user_model()
        candidate = base
        index = 1
        while UserModel.objects.filter(username=candidate).exists():
            candidate = f'{base}{index}'
            index += 1
        return candidate

    def save(self):
        UserModel = get_user_model()
        user = UserModel.objects.create_user(
            username=self._generate_username(),
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            phone=self.cleaned_data.get('phone', ''),
            country_of_residence=self.cleaned_data['country_of_residence'],
            preferred_language=self.cleaned_data['preferred_language'],
            terms_accepted=self.cleaned_data['terms_accepted'],
            privacy_accepted=self.cleaned_data['privacy_accepted'],
            is_student=True,
        )
        return user


class CustomLoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Mot de passe')
    remember_me = forms.BooleanField(label='Se souvenir de moi', required=False)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'h-4 w-4 rounded border-gray-300 text-secondary focus:ring-secondary',
                })
                continue
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 bg-white text-gray-900 text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-secondary/30 focus:border-secondary transition-colors',
                'placeholder': field.label,
            })

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            self.user_cache = authenticate(self.request, username=email.lower(), password=password)
            if self.user_cache is None:
                raise forms.ValidationError('Email ou mot de passe invalide.')
            if not self.user_cache.is_active:
                raise forms.ValidationError('Ce compte est desactive.')
        return cleaned_data

    def get_user(self):
        return self.user_cache

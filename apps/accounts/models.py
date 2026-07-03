from django.contrib.auth.models import AbstractUser
from django.db import models
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    LANGUAGE_CHOICES = (
        ('fr', 'Francais'),
        ('en', 'English'),
    )

    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    phone = PhoneNumberField(blank=True)
    country_of_residence = CountryField(blank=True)
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='fr')
    email_consent = models.BooleanField(default=True)
    whatsapp_opt_in = models.BooleanField(default=False)
    terms_accepted = models.BooleanField(default=False)
    privacy_accepted = models.BooleanField(default=False)
    is_student = models.BooleanField(default=True)
    is_advisor = models.BooleanField(default=False)
    has_completed_onboarding = models.BooleanField(default=False)
    has_active_plan = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class StaffAccount(CustomUser):
    class Meta:
        proxy = True
        verbose_name = 'Staff Account'
        verbose_name_plural = 'Staff Accounts'

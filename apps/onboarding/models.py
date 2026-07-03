from django.db import models
from django.conf import settings


class OnboardingResponse(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='onboarding')
    passport_status = models.CharField(max_length=20, choices=[('yes','Yes'),('no','No'),('in_process','In Process')], blank=True)
    education_level = models.CharField(max_length=20, choices=[('high_school','High School'),('bachelor','Bachelor'),('master','Master')], blank=True)
    admission_status = models.CharField(max_length=20, choices=[('admitted','Already Admitted'),('applied','Applied'),('not_applied','Not Applied')], blank=True)
    campus_france_account = models.CharField(max_length=5, choices=[('yes','Yes'),('no','No')], blank=True)
    visa_support = models.CharField(max_length=20, choices=[('full','Full Assistance'),('review','Review Only'),('none','No Help Needed')], blank=True)
    financial_situation = models.CharField(max_length=20, choices=[('own_funds','Own Funds'),('sponsor','Sponsor'),('not_ready','Not Ready')], blank=True)
    timeline = models.CharField(max_length=20, choices=[('less_3','Less than 3 months'),('3_to_6','3-6 months'),('more_6','6+ months')], blank=True)
    basic_score = models.IntegerField(default=0)
    standard_score = models.IntegerField(default=0)
    premium_score = models.IntegerField(default=0)
    recommended_plan = models.CharField(max_length=20, blank=True)
    needs_assistance = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Onboarding - {self.user.email}"

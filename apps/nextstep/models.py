from django.db import models

class NextStepSettings(models.Model):
    """Singleton model for NextStep global settings."""
    logo = models.ImageField(upload_to='nextstep/logos/', blank=True, null=True, help_text="Logo principal de NextStep")
    
    # Liens
    appointment_url = models.URLField(blank=True, help_text="Lien pour 'Prendre Rendez-vous' (ex: Calendly)")
    
    # Réseaux Sociaux
    facebook_link = models.URLField(blank=True)
    instagram_link = models.URLField(blank=True)
    linkedin_link = models.URLField(blank=True)
    twitter_link = models.URLField(blank=True)
    
    # Contacts
    contact_email = models.EmailField(blank=True, help_text="Adresse email de contact")
    contact_phone = models.CharField(max_length=20, blank=True, help_text="Numéro de téléphone de contact")
    address = models.TextField(blank=True, help_text="Adresse physique")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'NextStep Setting'
        verbose_name_plural = 'NextStep Settings'

    def __str__(self):
        return 'Paramètres de NextStep'

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj


class NextStepFAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.IntegerField(default=0, help_text="Ordre d'affichage (0, 1, 2...)")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'FAQ NextStep'
        verbose_name_plural = 'FAQs NextStep'
        ordering = ['order']

    def __str__(self):
        return self.question


class NextStepService(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    icon_name = models.CharField(max_length=100, blank=True, help_text="Nom de l'icône (ex: icon_target.png) ou chemin")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Service NextStep'
        verbose_name_plural = 'Services NextStep'
        ordering = ['order']

    def __str__(self):
        return self.title


class NextStepTestimonial(models.Model):
    student_name = models.CharField(max_length=100)
    program = models.CharField(max_length=100, help_text="ex: Master Informatique à la Sorbonne")
    content = models.TextField()
    image = models.ImageField(upload_to='nextstep/testimonials/', blank=True, null=True)
    rating = models.IntegerField(default=5, help_text="Note sur 5")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Témoignage NextStep'
        verbose_name_plural = 'Témoignages NextStep'

    def __str__(self):
        return f"Témoignage de {self.student_name}"

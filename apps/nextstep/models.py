from django.db import models

class NextStepSettings(models.Model):
    """Singleton model for NextStep global settings."""
    # Branding
    logo = models.ImageField(upload_to="nextstep/logos/", blank=True, null=True, help_text="Logo principal de NextStep")
    favicon = models.ImageField(upload_to="nextstep/logos/", blank=True, null=True, help_text="Favicon (icône d'onglet)")
    
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
        verbose_name = 'Nextstep Consulting - Paramètres Globaux'
        verbose_name_plural = 'Nextstep Consulting - Paramètres Globaux'

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
        verbose_name = 'Nextstep - Paramètres FAQ'
        verbose_name_plural = 'Nextstep - Paramètres FAQs'
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
        verbose_name = 'Nextstep - Accueil Service'
        verbose_name_plural = 'Nextstep - Accueil Services'
        ordering = ['order']

    def __str__(self):
        return self.title


class NextStepTestimonial(models.Model):
    student_name = models.CharField(max_length=100)
    program = models.CharField(max_length=100, help_text="ex: Master Informatique à la Sorbonne")
    content = models.TextField()
    image = models.ImageField(upload_to="nextstep/testimonials/", blank=True, null=True)
    rating = models.IntegerField(default=5, help_text="Note sur 5")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Nextstep - Accueil Témoignage"
        verbose_name_plural = 'Nextstep - Accueil Témoignages'

    def __str__(self):
        return f"Témoignage de {self.student_name}"

class NextstepHomePageSettings(models.Model):
    # Hero Section
    hero_title = models.CharField(max_length=255, default="Bienvenue chez NextStep Consulting")
    hero_subtitle = models.TextField(blank=True, default="Votre partenaire de confiance pour réussir vos études en France.")
    hero_button_text = models.CharField(max_length=50, default="Découvrir nos services")
    hero_button_link = models.CharField(max_length=200, default="#services")
    hero_image = models.ImageField(upload_to="nextstep/home/", blank=True, null=True)

    # About Section
    about_title = models.CharField(max_length=255, default="À Propos de Nous")
    about_text = models.TextField(blank=True, default="Nous sommes une équipe d'experts dédiés à la réussite de votre mobilité internationale.")
    
    # Why Choose Us Section
    why_us_title = models.CharField(max_length=255, default="Pourquoi nous choisir ?")
    why_us_text = models.TextField(blank=True, default="Un accompagnement personnalisé et une expertise reconnue.")

    class Meta:
        verbose_name = 'Nextstep - Paramètres Accueil'
        verbose_name_plural = 'Nextstep - Paramètres Accueil'

    def __str__(self): return "Paramètres de la page d'accueil"

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

class CampusFrancePageSettings(models.Model):
    title = models.CharField(max_length=255, default="Procédure Campus France")
    description = models.TextField(blank=True, default="Tout ce qu'il faut savoir sur la procédure Campus France.")
    
    class Meta:
        verbose_name = 'Nextstep - Page Campus France'
        verbose_name_plural = 'Nextstep - Page Campus France'

    def __str__(self): return 'Paramètres de la page Campus France'

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

class ContactPageSettings(models.Model):
    title = models.CharField(max_length=255, default="Contactez-nous")
    subtitle = models.TextField(blank=True, default="Nous sommes à votre écoute.")
    
    class Meta:
        verbose_name ="Nextstep - Page Contact"
        verbose_name_plural ="Nextstep - Page Contact"

    def __str__(self): return 'Paramètres de la page Contact'

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

class FAQPageSettings(models.Model):
    title = models.CharField(max_length=255, default="Foire Aux Questions")
    subtitle = models.TextField(blank=True, default="Les réponses à vos questions les plus fréquentes.")
    
    class Meta:
        verbose_name ="Nextstep - Page FAQ"
        verbose_name_plural ="Nextstep - Page FAQ"

    def __str__(self): return 'Paramètres de la page FAQ'

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

class MentionsLegalesSettings(models.Model):
    title = models.CharField(max_length=255, default="Mentions Légales")
    content = models.TextField(blank=True, default="Contenu des mentions légales de NextStep Consulting.")
    
    class Meta:
        verbose_name ="Nextstep - Page Mentions Légales"
        verbose_name_plural ="Nextstep - Page Mentions Légales"

    def __str__(self): return 'Paramètres de la page Mentions Légales'

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj


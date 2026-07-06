from django.db import models

class SiteSettings(models.Model):
    """Singleton model for global site settings (Contact, Social Media)."""
    
    # Contact Info
    contact_email = models.EmailField(blank=True, default="support@visanexstep.com", help_text="Email de contact principal")
    contact_phone = models.CharField(max_length=20, blank=True, default="+33 1 23 45 67 89", help_text="Numéro de téléphone de contact")
    address = models.TextField(blank=True, default="10 Rue de la Paix, 75002 Paris, France", help_text="Adresse physique")
    
    # Social Media Links
    facebook_link = models.URLField(blank=True, help_text="Lien vers la page Facebook")
    instagram_link = models.URLField(blank=True, help_text="Lien vers le compte Instagram")
    linkedin_link = models.URLField(blank=True, help_text="Lien vers la page LinkedIn")
    twitter_link = models.URLField(blank=True, help_text="Lien vers le compte Twitter/X")
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Paramètre du site'
        verbose_name_plural = 'Paramètres du site'

    def __str__(self):
        return 'Paramètres Globaux'

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

class HomePageSettings(models.Model):
    # Hero Section
    hero_title = models.CharField(max_length=255, default='Votre parcours pour étudier en France commence ici')
    hero_subtitle = models.TextField(default="De l'inscription Campus France à l'obtention du visa — nous vous guidons à chaque étape avec un accompagnement personnalisé.")
    hero_primary_button_text = models.CharField(max_length=50, default='Démarrer mon dossier')
    hero_primary_button_link = models.CharField(max_length=200, default='account_signup', help_text='Nom de la vue (ex: account_signup) ou URL absolue')
    hero_secondary_button_text = models.CharField(max_length=50, default='Comment ça marche')
    hero_secondary_button_link = models.CharField(max_length=200, default='#processus')

    # Presentation Section
    presentation_title = models.CharField(max_length=255, default="Finis les dossiers papiers et l'incertitude.")
    presentation_description = models.TextField(default="Visanexstep à été conçu pour révolutionner la manière dont les étudiants préparent leur départ pour la France.")

    # Features Section
    features_subtitle = models.CharField(max_length=100, default='Fonctionnalités clés')
    features_title = models.CharField(max_length=255, default='Tout ce dont vous avez besoin, au même endroit.')
    features_description = models.TextField(default="Une suite d'outils pensée spécifiquement pour la réussite de votre mobilité étudiante.")

    # Process Section
    process_title = models.CharField(max_length=255, default='4 étapes pour décrocher votre visa')
    process_description = models.TextField(default='Un processus clair, digitalisé et structuré pour garantir votre succès.')

    # Advantages Section
    advantages_subtitle = models.CharField(max_length=100, default="L'avantage Visanexstep")
    advantages_title = models.CharField(max_length=255, default='Mettez toutes les chances de votre côté.')
    advantages_description_1 = models.TextField(default='Une demande de visa étudiant est un parcours complexe où la moindre erreur peut être fatale. Nous éliminons ce risque.')
    advantages_description_2 = models.TextField(default="Notre approche hybride (SaaS + Humain) vous permet de rester autonome tout en bénéficiant de l'œil expert de professionnels à chaque étape clé. Vous n'êtes plus jamais seul face à vos démarches.")

    # Testimonials Section
    testimonials_title = models.CharField(max_length=255, default='Ils ont réussi avec Visanexstep')

    # CTA Section
    cta_title = models.CharField(max_length=255, default="Prêt à transformer votre projet d'études en réalité ?")
    cta_subtitle = models.TextField(default="Rejoignez des centaines d'étudiants qui ont choisi la sérénité avec Visanexstep.")
    cta_button_text = models.CharField(max_length=50, default='Créer mon compte gratuitement')
    cta_button_link = models.CharField(max_length=200, default='account_signup')
    cta_subtext = models.CharField(max_length=255, default="Aucune carte de crédit requise pour s'inscrire.")

    class Meta:
        verbose_name = 'Page Accueil - Paramètres'
        verbose_name_plural = 'Page Accueil - Paramètres'

    def __str__(self):
        return 'Paramètres de la page d\'accueil'

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

class PresentationItem(models.Model):
    text = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Présentation - Élément'
        verbose_name_plural = 'Présentation - Éléments'

    def __str__(self):
        return self.text

class FeatureItem(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='features/', blank=True, null=True, help_text='Icone ou image')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Fonctionnalité'
        verbose_name_plural = 'Fonctionnalités'

    def __str__(self):
        return self.title

class ProcessStep(models.Model):
    number = models.IntegerField(help_text='Numéro de l\'étape')
    title = models.CharField(max_length=100)
    description = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Étape de processus'
        verbose_name_plural = 'Étapes de processus'

    def __str__(self):
        return f"{self.number}. {self.title}"

class AdvantageItem(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon_svg = models.TextField(blank=True, help_text='Code SVG de l\'icône')
    is_highlighted = models.BooleanField(default=False, help_text='Mettre en évidence (carte différente)')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Avantage'
        verbose_name_plural = 'Avantages'

    def __str__(self):
        return self.title

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, help_text='Ex: Master Finance, Paris')
    quote = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Témoignage'
        verbose_name_plural = 'Témoignages'

    def __str__(self):
        return self.name


from django.db import models

class SiteSettings(models.Model):
    """Singleton model for global site settings (Contact, Social Media)."""
    
    # Branding
    logo = models.ImageField(upload_to="visanexstep/branding/", blank=True, null=True, help_text="Logo principal")
    favicon = models.ImageField(upload_to="visanexstep/branding/", blank=True, null=True, help_text="Favicon (icône d'onglet)")
    
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
        verbose_name = 'Visanexstep - Paramètres Globaux'
        verbose_name_plural = 'Visanexstep - Paramètres Globaux'

    def __str__(self):
        return 'Paramètres Globaux'

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

class HomePageSettings(models.Model):
    # Hero Section
    hero_title = models.CharField(max_length=255, default="Votre parcours pour étudier en France commence ici")
    hero_subtitle = models.TextField(default="De l'inscription Campus France à l'obtention du visa — nous vous guidons à chaque étape avec un accompagnement personnalisé.")
    hero_primary_button_text = models.CharField(max_length=50, default="Démarrer mon dossier")
    hero_primary_button_link = models.CharField(max_length=200, default="account_signup", help_text="Nom de la vue (ex: account_signup) ou URL absolue")
    hero_secondary_button_text = models.CharField(max_length=50, default="Comment ça marche")
    hero_secondary_button_link = models.CharField(max_length=200, default="#processus")

    # Presentation Section
    presentation_title = models.CharField(max_length=255, default="Finis les dossiers papiers et l'incertitude.")
    presentation_description = models.TextField(default="Visanexstep à été conçu pour révolutionner la manière dont les étudiants préparent leur départ pour la France.")

    # Features Section
    features_subtitle = models.CharField(max_length=100, default="Fonctionnalités clés")
    features_title = models.CharField(max_length=255, default="Tout ce dont vous avez besoin, au même endroit.")
    features_description = models.TextField(default="Une suite d'outils pensée spécifiquement pour la réussite de votre mobilité étudiante.")

    # Process Section
    process_title = models.CharField(max_length=255, default="4 étapes pour décrocher votre visa")
    process_description = models.TextField(default="Un processus clair, digitalisé et structuré pour garantir votre succès.")

    # Advantages Section
    advantages_subtitle = models.CharField(max_length=100, default="L'avantage Visanexstep")
    advantages_title = models.CharField(max_length=255, default="Mettez toutes les chances de votre côté.")
    advantages_description_1 = models.TextField(default="Une demande de visa étudiant est un parcours complexe où la moindre erreur peut être fatale. Nous éliminons ce risque.")
    advantages_description_2 = models.TextField(default="Notre approche hybride (SaaS + Humain) vous permet de rester autonome tout en bénéficiant de l'œil expert de professionnels à chaque étape clé. Vous n'êtes plus jamais seul face à vos démarches.")

    # Testimonials Section
    testimonials_title = models.CharField(max_length=255, default="Ils ont réussi avec Visanexstep")

    # CTA Section
    cta_title = models.CharField(max_length=255, default="Prêt à transformer votre projet d'études en réalité ?")
    cta_subtitle = models.TextField(default="Rejoignez des centaines d'étudiants qui ont choisi la sérénité avec Visanexstep.")
    cta_button_text = models.CharField(max_length=50, default="Créer mon compte gratuitement")
    cta_button_link = models.CharField(max_length=200, default="account_signup")
    cta_subtext = models.CharField(max_length=255, default="Aucune carte de crédit requise pour s'inscrire.")

    class Meta:
        verbose_name = 'Visanexstep - Accueil Paramètres'
        verbose_name_plural = 'Visanexstep - Accueil Paramètres'

    def __str__(self):
        return "Paramètres de la page d'accueil"

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
        verbose_name = 'Visanexstep - Accueil Présentation'
        verbose_name_plural = 'Visanexstep - Accueil Présentation'

    def __str__(self):
        return self.text

class FeatureItem(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="features/", blank=True, null=True, help_text="Icone ou image")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Visanexstep - Accueil Fonctionnalité'
        verbose_name_plural = 'Visanexstep - Accueil Fonctionnalités'

    def __str__(self):
        return self.title

class ProcessStep(models.Model):
    number = models.IntegerField(help_text="Numéro de l'étape")
    title = models.CharField(max_length=100)
    description = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Visanexstep - Accueil Processus'
        verbose_name_plural = 'Visanexstep - Accueil Processus'

    def __str__(self):
        return f"{self.number}. {self.title}"

class AdvantageItem(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon_svg = models.TextField(blank=True, help_text="Code SVG de l'icône")
    is_highlighted = models.BooleanField(default=False, help_text="Mettre en évidence (carte différente)")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Visanexstep - Accueil Avantage'
        verbose_name_plural = 'Visanexstep - Accueil Avantages'

    def __str__(self):
        return self.title

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, help_text="Ex: Master Finance, Paris")
    quote = models.TextField()
    image = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Visanexstep - Accueil Témoignage'
        verbose_name_plural = 'Visanexstep - Accueil Témoignages'

    def __str__(self):
        return self.name


class AboutPageSettings(models.Model):
    title = models.CharField(max_length=255, default="À propos de Visanexstep")
    subtitle = models.TextField(blank=True, default="Découvrez notre histoire et notre mission.")
    content = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Visanexstep - Page À Propos'
        verbose_name_plural = 'Visanexstep - Page À Propos'

    def __str__(self): return 'Paramètres de la page À propos'

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

class ServicesPageSettings(models.Model):
    title = models.CharField(max_length=255, default="Nos Services")
    subtitle = models.TextField(blank=True, default="Des solutions sur mesure pour votre projet d'études.")
    
    class Meta:
        verbose_name = "Visanexstep - Page Services"
        verbose_name_plural ="Visanexstep - Page Services"

    def __str__(self): return 'Paramètres de la page Services'

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

class PricingPageSettings(models.Model):
    title = models.CharField(max_length=255, default="Un tarif transparent. Zéro surprise.")
    subtitle = models.TextField(blank=True, default="Découvrez nos conditions d'accompagnement pour vos études en France.")
    description = models.TextField(blank=True, default="Nous proposons un accompagnement personnalisé et adapté à chaque profil d'étudiant. Nos tarifs sont établis sur mesure en fonction de la complexité de votre dossier, de vos besoins en coaching, et des services spécifiques demandés. Contactez-nous pour obtenir un devis gratuit et personnalisé.")
    button_text = models.CharField(max_length=100, default="Contactez-nous")
    button_link = models.CharField(max_length=255, default="pages:contact")
    
    class Meta:
        verbose_name ="Visanexstep - Page Tarifs - Paramètres"
        verbose_name_plural ="Visanexstep - Page Tarifs - Paramètres"

    def __str__(self): return 'Paramètres de la page Tarifs'

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj


class PricingPlan(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom de l'offre")
    description = models.TextField(verbose_name="Description")
    price = models.CharField(max_length=50, verbose_name="Prix (ex: 49€ ou Sur devis)")
    button_text = models.CharField(max_length=100, verbose_name="Texte du bouton")
    button_link = models.CharField(max_length=255, default="#", verbose_name="Lien du bouton")
    is_popular = models.BooleanField(default=False, verbose_name="Plus populaire")
    features_list = models.TextField(help_text="Une fonctionnalité par ligne. Précéder d'un '-' (ex: - Accès à la plateforme). Pour barrer/désactiver, précéder d'un 'x' (ex: x Chat en temps réel).", verbose_name="Liste des fonctionnalités")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Visanexstep - Tarifs Offre"
        verbose_name_plural = "Visanexstep - Tarifs Offres"
        ordering = ['order']

    def __str__(self):
        return self.name

    def get_features(self):
        features = []
        for line in self.features_list.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            is_active = True
            if line.startswith('-'):
                text = line[1:].strip()
            elif line.startswith('x') or line.startswith('X'):
                text = line[1:].strip()
                is_active = False
            else:
                text = line
            features.append({'text': text, 'is_active': is_active})
        return features


class PricingFeature(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nom de la fonctionnalité")
    basic_value = models.CharField(max_length=100, blank=True, verbose_name="Valeur pour Essentiel (ex: 'Oui', 'Non', '1 seule fois')")
    premium_value = models.CharField(max_length=100, blank=True, verbose_name="Valeur pour Premium")
    excellence_value = models.CharField(max_length=100, blank=True, verbose_name="Valeur pour Excellence")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Visanexstep - Tarifs Comparatif"
        verbose_name_plural = "Visanexstep - Tarifs Comparatifs"
        ordering = ['order']

    def __str__(self):
        return self.name

class HowItWorksPageSettings(models.Model):
    title = models.CharField(max_length=255, default="Comment ça marche")
    subtitle = models.TextField(blank=True, default="Notre processus détaillé de A à Z.")
    
    class Meta:
        verbose_name = 'Visanexstep - Page Processus'
        verbose_name_plural = 'Visanexstep - Page Processus'

    def __str__(self): return 'Paramètres de la page Processus'

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

class TestimonialsPageSettings(models.Model):
    title = models.CharField(max_length=255, default="Témoignages")
    subtitle = models.TextField(blank=True, default="Ce que nos étudiants disent de nous.")
    
    class Meta:
        verbose_name = 'Visanexstep - Page Témoignages'
        verbose_name_plural = 'Visanexstep - Page Témoignages'

    def __str__(self): return 'Paramètres de la page Témoignages'

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

class FAQPageSettings(models.Model):
    title = models.CharField(max_length=255, default="Foire Aux Questions")
    subtitle = models.TextField(blank=True, default="Trouvez les réponses à vos questions.")
    
    class Meta:
        verbose_name ="Visanexstep - Page FAQ"
        verbose_name_plural ="Visanexstep - Page FAQ"

    def __str__(self): return 'Paramètres de la page FAQ'

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

class ContactPageSettings(models.Model):
    title = models.CharField(max_length=255, default="Contactez-nous")
    subtitle = models.TextField(blank=True, default="Nous sommes là pour vous aider.")
    
    class Meta:
        verbose_name ="Visanexstep - Page Contact"
        verbose_name_plural ="Visanexstep - Page Contact"

    def __str__(self): return 'Paramètres de la page Contact'

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj


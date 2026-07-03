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

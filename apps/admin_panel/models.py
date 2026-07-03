from django.db import models


class PlatformSetting(models.Model):
    LANGUAGE_CHOICES = (
        ('fr', 'Francais'),
        ('en', 'English'),
    )

    platform_name = models.CharField(max_length=100, default='Visanextstep')
    support_email = models.EmailField(blank=True)
    support_phone = models.CharField(max_length=50, blank=True)
    default_student_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='fr')
    maintenance_mode = models.BooleanField(default=False)
    broadcast_enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Platform Setting'
        verbose_name_plural = 'Platform Settings'

    def __str__(self):
        return f'Platform settings ({self.platform_name})'

    @classmethod
    def get_solo(cls):
        instance = cls.objects.first()
        if instance:
            return instance
        return cls.objects.create()


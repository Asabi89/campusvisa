from django.db import models
from django.conf import settings


class DocumentType(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    tip = models.CharField(max_length=255, blank=True, help_text='Conseil affiche aux etudiants, ex: "Assurez-vous que le scan est lisible"')
    is_required = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class Document(models.Model):
    STATUS_CHOICES = [('pending','Pending Review'),('approved','Approved'),('rejected','Rejected'),('reupload','Re-upload Required')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True, blank=True)
    custom_name = models.CharField(max_length=200, blank=True)
    file = models.FileField(upload_to='documents/%Y/%m/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_comment = models.TextField(blank=True)
    is_custom = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        name = self.custom_name if self.is_custom else self.document_type.name if self.document_type else 'Unknown'
        return f"{self.user.email} - {name}"

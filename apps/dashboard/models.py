from django.db import models
from django.conf import settings


class ProgressStep(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class StudentProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    step = models.ForeignKey(ProgressStep, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'step']

    def __str__(self):
        status = '✅' if self.is_completed else '⬜'
        return f"{status} {self.user.email} - {self.step.name}"

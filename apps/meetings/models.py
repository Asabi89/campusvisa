from django.db import models
from django.conf import settings


class AvailableSlot(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.date} {self.start_time}-{self.end_time}"


class Meeting(models.Model):
    STATUS_CHOICES = [('scheduled','Scheduled'),('completed','Completed'),('cancelled','Cancelled')]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meetings')
    slot = models.OneToOneField(AvailableSlot, on_delete=models.CASCADE)
    topic = models.CharField(max_length=200)
    meeting_link = models.URLField(blank=True)
    calendar_link = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.email} - {self.slot.date}"

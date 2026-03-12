from django.db import models
from accounts.models import User


class Availability(models.Model):
    doctor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='availability_slots'
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        ordering = ['date', 'start_time']
        verbose_name_plural = 'Availabilities'

    def __str__(self):
        return f"Dr.{self.doctor.username} | {self.date} | {self.start_time}-{self.end_time}"

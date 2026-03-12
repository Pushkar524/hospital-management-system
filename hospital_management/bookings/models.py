from django.db import models
from accounts.models import User
from doctors.models import Availability


class Booking(models.Model):
    doctor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='doctor_bookings'
    )
    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='patient_bookings'
    )
    slot = models.ForeignKey(Availability, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} → Dr.{self.doctor.username} on {self.slot.date}"

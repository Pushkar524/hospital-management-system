from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from functools import wraps

from doctors.models import Availability
from bookings.models import Booking
from accounts.utils import send_notification
from .google_calendar import add_appointment_to_calendar


def patient_required(view_func):
    """Decorator to restrict access to patient users only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'patient':
            messages.error(request, 'Access denied. Patients only.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@patient_required
def patient_dashboard(request):
    available_slots = Availability.objects.filter(
        is_booked=False,
        date__gte=date.today()
    ).select_related('doctor')

    my_bookings = Booking.objects.filter(
        patient=request.user
    ).select_related('doctor', 'slot')

    return render(request, 'bookings/patient_dashboard.html', {
        'available_slots': available_slots,
        'my_bookings': my_bookings,
    })


@patient_required
def book_slot(request, slot_id):
    if request.method == 'POST':
        try:
            # Only get the slot if it is NOT already booked
            slot = Availability.objects.get(id=slot_id, is_booked=False)

            booking = Booking.objects.create(
                doctor=slot.doctor,
                patient=request.user,
                slot=slot
            )

            # Mark slot as booked so no one else can book it
            slot.is_booked = True
            slot.save()

            # Send email to patient
            send_notification(
                "BOOKING_CONFIRMATION_PATIENT",
                request.user.email,
                doctor_name=slot.doctor.get_full_name() or slot.doctor.username,
                date=slot.date.strftime('%B %d, %Y'),
                time=f"{slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}"
            )
            
            # Send email to doctor
            send_notification(
                "BOOKING_CONFIRMATION_DOCTOR",
                slot.doctor.email,
                patient_name=request.user.get_full_name() or request.user.username,
                date=slot.date.strftime('%B %d, %Y'),
                time=f"{slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}"
            )
            
            # Add to Google Calendar (won't crash if credentials not set up)
            add_appointment_to_calendar(booking)

            messages.success(request, 'Appointment booked successfully!')

        except Availability.DoesNotExist:
            messages.error(request, 'This slot is no longer available.')

    return redirect('patient_dashboard')

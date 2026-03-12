from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Availability
from bookings.models import Booking
from functools import wraps


def doctor_required(view_func):
    """Decorator to restrict access to doctor users only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'doctor':
            messages.error(request, 'Access denied. Doctors only.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@doctor_required
def doctor_dashboard(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        if date and start_time and end_time:
            Availability.objects.create(
                doctor=request.user,
                date=date,
                start_time=start_time,
                end_time=end_time,
            )
            messages.success(request, 'Availability slot added successfully.')
        return redirect('doctor_dashboard')

    slots = Availability.objects.filter(doctor=request.user)
    bookings = Booking.objects.filter(doctor=request.user).select_related('patient', 'slot')

    return render(request, 'doctors/dashboard.html', {
        'slots': slots,
        'bookings': bookings,
    })

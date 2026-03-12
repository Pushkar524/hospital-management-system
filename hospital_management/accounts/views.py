from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import DoctorSignupForm, PatientSignupForm
from .utils import send_notification


def doctor_signup(request):
    if request.method == 'POST':
        form = DoctorSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_notification("SIGNUP_WELCOME", user.email)
            login(request, user)
            return redirect('doctor_dashboard')
    else:
        form = DoctorSignupForm()
    return render(request, 'accounts/doctor_signup.html', {'form': form})


def patient_signup(request):
    if request.method == 'POST':
        form = PatientSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_notification("SIGNUP_WELCOME", user.email)
            login(request, user)
            return redirect('patient_dashboard')
    else:
        form = PatientSignupForm()
    return render(request, 'accounts/patient_signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'doctor':
                return redirect('doctor_dashboard')
            else:
                return redirect('patient_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

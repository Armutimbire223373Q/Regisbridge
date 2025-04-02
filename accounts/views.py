from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta
from .forms import CustomUserCreationForm, ProfileForm, UserRegistrationForm, AuthenticationForm
from students.models import Grade, Attendance
from core.models import Event, NewsItem
from teachers.models import Class, Schedule, Assignment, TeacherProfile, Announcement
from django.contrib.auth import get_user_model

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """Handle user login."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('accounts:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """Handle user logout."""
    logout(request)
    return redirect('accounts:login')

@login_required
def dashboard(request):
    context = {
        'recent_news': NewsItem.objects.filter(is_published=True).order_by('-date_posted')[:5],
        'upcoming_events': Event.objects.filter(end_date__gte=timezone.now()).order_by('start_date')[:5],
    }
    
    if hasattr(request.user, 'teacherprofile'):
        context['announcements'] = Announcement.objects.filter(
            teacher=request.user.teacherprofile
        ).order_by('-created_at')[:5]
    
    if hasattr(request.user, 'studentprofile'):
        context['announcements'] = Announcement.objects.filter(
            class_group=request.user.studentprofile.class_group
        ).order_by('-created_at')[:5]
    
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

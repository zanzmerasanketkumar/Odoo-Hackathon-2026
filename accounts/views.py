from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import User, UserProfile


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.username}!')
                    next_url = request.GET.get('next', 'dashboard')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Your account is inactive.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


class UserRegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful! You can now log in.')
        return response


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/edit_profile.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Profile updated successfully!')
        return response


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Password changed successfully!')
        return response


@login_required
def dashboard_view(request):
    # Import models for real data
    from vehicles.models import Vehicle
    from trips.models import Trip
    from maintenance.models import MaintenanceSchedule
    from drivers.models import Driver
    from django.db.models import Count, Q, Avg, Sum
    from datetime import datetime, timedelta
    
    # Get real data
    total_vehicles = Vehicle.objects.count()
    available_vehicles = Vehicle.objects.filter(status='available').count()
    on_trip_vehicles = Vehicle.objects.filter(status='on_trip').count()
    in_shop_vehicles = Vehicle.objects.filter(status='in_shop').count()
    
    total_trips = Trip.objects.count()
    active_trips = Trip.objects.filter(status__in=['dispatched', 'in_progress']).count()
    completed_trips = Trip.objects.filter(status='completed').count()
    
    total_drivers = Driver.objects.count()
    available_drivers = Driver.objects.filter(status='available').count()
    
    # Maintenance data
    maintenance_due = MaintenanceSchedule.objects.filter(
        scheduled_date__lte=datetime.now() + timedelta(days=7),
        status__in=['scheduled', 'pending']
    ).count()
    
    overdue_maintenance = MaintenanceSchedule.objects.filter(
        scheduled_date__lt=datetime.now(),
        status__in=['scheduled', 'pending']
    ).count()
    
    # Recent trips
    recent_trips = Trip.objects.select_related('vehicle', 'driver').order_by('-created_at')[:5]
    
    # Maintenance alerts
    maintenance_alerts = MaintenanceSchedule.objects.select_related('vehicle', 'maintenance_type').filter(
        scheduled_date__lte=datetime.now() + timedelta(days=14),
        status__in=['scheduled', 'pending']
    ).order_by('scheduled_date')[:5]
    
    # Calculate fuel efficiency (average from completed trips)
    from fuel.models import FuelLog
    
    # Get fuel logs for completed trips
    fuel_logs = FuelLog.objects.filter(
        trip__status='completed',
        trip__actual_distance__isnull=False,
        fuel_liters__isnull=False
    ).select_related('trip')
    
    if fuel_logs.exists():
        total_distance = sum(log.trip.actual_distance for log in fuel_logs if log.trip.actual_distance)
        total_fuel = sum(log.fuel_liters for log in fuel_logs if log.fuel_liters)
        fuel_efficiency = total_distance / total_fuel if total_fuel > 0 else 0
    else:
        fuel_efficiency = 0
    
    # Get historical fuel consumption data for the last 6 months
    from django.db.models import Sum
    from datetime import datetime, timedelta
    import calendar
    
    fuel_consumption_data = []
    fuel_consumption_labels = []
    
    for i in range(6):
        month_start = datetime.now().replace(day=1) - timedelta(days=i*30)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_fuel = FuelLog.objects.filter(
            created_at__date__gte=month_start.date(),
            created_at__date__lte=month_end.date()
        ).aggregate(total_fuel=Sum('fuel_liters'))['total_fuel'] or 0
        
        fuel_consumption_data.append(float(month_fuel))
        fuel_consumption_labels.append(calendar.month_name[month_start.month][:3])
    
    # Reverse to show oldest to newest
    fuel_consumption_data.reverse()
    fuel_consumption_labels.reverse()
    
    context = {
        'user': request.user,
        'role': request.user.get_role_display(),
        # Vehicle stats
        'total_vehicles': total_vehicles,
        'available_vehicles': available_vehicles,
        'on_trip_vehicles': on_trip_vehicles,
        'in_shop_vehicles': in_shop_vehicles,
        # Trip stats
        'total_trips': total_trips,
        'active_trips': active_trips,
        'completed_trips': completed_trips,
        # Driver stats
        'total_drivers': total_drivers,
        'available_drivers': available_drivers,
        # Maintenance stats
        'maintenance_due': maintenance_due,
        'overdue_maintenance': overdue_maintenance,
        # Data for display
        'recent_trips': recent_trips,
        'maintenance_alerts': maintenance_alerts,
        'fuel_efficiency': fuel_efficiency,
        'fuel_consumption_data': fuel_consumption_data,
        'fuel_consumption_labels': fuel_consumption_labels,
    }
    return render(request, 'accounts/dashboard.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import Driver, DriverPerformance, DriverDocument, DriverAttendance
from .forms import DriverForm, DriverDocumentForm, DriverAttendanceForm


class DriverListView(LoginRequiredMixin, ListView):
    model = Driver
    template_name = 'drivers/driver_list.html'
    context_object_name = 'drivers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Driver.objects.filter(is_active=True)
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(license_number__icontains=search_query)
            )
        
        # Filter by status
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by license expiry
        license_filter = self.request.GET.get('license_filter', '')
        if license_filter == 'expired':
            queryset = queryset.filter(license_expiry__lte=timezone.now().date())
        elif license_filter == 'expiring_soon':
            queryset = queryset.filter(
                license_expiry__lte=timezone.now().date() + timedelta(days=30),
                license_expiry__gt=timezone.now().date()
            )
        
        return queryset.order_by('last_name', 'first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Driver.STATUS_CHOICES
        return context


class DriverCreateView(LoginRequiredMixin, CreateView):
    model = Driver
    form_class = DriverForm
    template_name = 'drivers/driver_form.html'
    success_url = reverse_lazy('drivers:driver_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Create performance record for new driver
        DriverPerformance.objects.create(driver=form.instance)
        messages.success(self.request, f'Driver "{form.instance.full_name}" has been created successfully!')
        return response


class DriverUpdateView(LoginRequiredMixin, UpdateView):
    model = Driver
    form_class = DriverForm
    template_name = 'drivers/driver_form.html'
    success_url = reverse_lazy('drivers:driver_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Driver "{form.instance.full_name}" has been updated successfully!')
        return response


class DriverDeleteView(LoginRequiredMixin, DeleteView):
    model = Driver
    template_name = 'drivers/driver_confirm_delete.html'
    success_url = reverse_lazy('drivers:driver_list')
    
    def delete(self, request, *args, **kwargs):
        driver = self.get_object()
        driver.is_active = False
        driver.save()
        messages.success(request, f'Driver "{driver.full_name}" has been deactivated.')
        return redirect(self.success_url)


@login_required
def driver_detail_view(request, pk):
    driver = get_object_or_404(Driver, pk=pk, is_active=True)
    performance, created = DriverPerformance.objects.get_or_create(driver=driver)
    documents = driver.documents.all()
    recent_attendance = driver.attendance.order_by('-date')[:10]
    
    context = {
        'driver': driver,
        'performance': performance,
        'documents': documents,
        'recent_attendance': recent_attendance,
    }
    return render(request, 'drivers/driver_detail.html', context)


@login_required
def driver_performance_view(request, pk):
    driver = get_object_or_404(Driver, pk=pk, is_active=True)
    performance, created = DriverPerformance.objects.get_or_create(driver=driver)
    
    context = {
        'driver': driver,
        'performance': performance,
    }
    return render(request, 'drivers/driver_performance.html', context)


@login_required
def driver_documents_view(request, pk):
    driver = get_object_or_404(Driver, pk=pk, is_active=True)
    documents = driver.documents.all()
    
    if request.method == 'POST':
        form = DriverDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.driver = driver
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('driver_documents', pk=driver.pk)
    else:
        form = DriverDocumentForm()
    
    context = {
        'driver': driver,
        'documents': documents,
        'form': form,
    }
    return render(request, 'drivers/driver_documents.html', context)


@login_required
def driver_attendance_view(request, pk):
    driver = get_object_or_404(Driver, pk=pk, is_active=True)
    attendance_records = driver.attendance.order_by('-date')
    
    if request.method == 'POST':
        form = DriverAttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.driver = driver
            attendance.save()
            messages.success(request, 'Attendance record added successfully!')
            return redirect('driver_attendance', pk=driver.pk)
    else:
        form = DriverAttendanceForm()
    
    context = {
        'driver': driver,
        'attendance_records': attendance_records,
        'form': form,
    }
    return render(request, 'drivers/driver_attendance.html', context)


@login_required
def get_available_drivers(request):
    """API endpoint to get available drivers for trip assignment"""
    drivers = Driver.objects.filter(
        status='on_duty',
        is_active=True
    ).exclude(
        license_expiry__lte=timezone.now().date()
    ).values('id', 'first_name', 'last_name', 'license_number')
    
    return JsonResponse({'drivers': list(drivers)})


@login_required
def driver_dashboard(request):
    """Dashboard view with driver statistics"""
    total_drivers = Driver.objects.filter(is_active=True).count()
    available_drivers = Driver.objects.filter(status='on_duty', is_active=True).count()
    expired_licenses = Driver.objects.filter(
        license_expiry__lte=timezone.now().date(),
        is_active=True
    ).count()
    expiring_soon = Driver.objects.filter(
        license_expiry__lte=timezone.now().date() + timedelta(days=30),
        license_expiry__gt=timezone.now().date(),
        is_active=True
    ).count()
    
    # Performance statistics
    avg_safety_score = DriverPerformance.objects.aggregate(
        avg_score=Avg('safety_score')
    )['avg_score'] or 0
    
    context = {
        'total_drivers': total_drivers,
        'available_drivers': available_drivers,
        'expired_licenses': expired_licenses,
        'expiring_soon': expiring_soon,
        'avg_safety_score': round(avg_safety_score, 2),
    }
    return render(request, 'drivers/dashboard.html', context)


@login_required
def driver_document_upload(request, pk):
    """Handle document upload for a driver"""
    if request.method == 'POST':
        # Handle file upload
        if request.FILES.get('file'):
            # Create document record
            document = DriverDocument.objects.create(
                driver_id=pk,
                document_type=request.POST.get('document_type'),
                title=request.POST.get('title'),
                file=request.FILES['file'],
                expiry_date=request.POST.get('expiry_date'),
                notes=request.POST.get('notes')
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Document uploaded successfully',
                'document_id': document.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No file uploaded'
            })
    
    return JsonResponse({'success': False, 'message': 'GET method not allowed'})

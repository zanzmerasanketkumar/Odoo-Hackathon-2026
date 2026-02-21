from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from .models import MaintenanceType, MaintenanceSchedule, MaintenancePart, MaintenanceDocument, MaintenanceReminder
from .forms import MaintenanceScheduleForm, MaintenancePartForm, MaintenanceDocumentForm, MaintenanceReminderForm


class MaintenanceListView(LoginRequiredMixin, ListView):
    model = MaintenanceSchedule
    template_name = 'maintenance/maintenance_list.html'
    context_object_name = 'maintenance_schedules'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = MaintenanceSchedule.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(vehicle__name__icontains=search_query) |
                Q(vehicle__license_plate__icontains=search_query) |
                Q(maintenance_type__name__icontains=search_query)
            )
        
        # Filter by status
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by priority
        priority_filter = self.request.GET.get('priority', '')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        return queryset.order_by('scheduled_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = MaintenanceSchedule.STATUS_CHOICES
        context['priority_choices'] = MaintenanceSchedule.PRIORITY_CHOICES
        return context


class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceSchedule
    form_class = MaintenanceScheduleForm
    template_name = 'maintenance/maintenance_form.html'
    success_url = reverse_lazy('maintenance:maintenance_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        
        # Set vehicle status to in_shop when maintenance is scheduled
        vehicle = form.instance.vehicle
        vehicle.status = 'in_shop'
        vehicle.save()
        
        response = super().form_valid(form)
        messages.success(self.request, f'Maintenance "{form.instance.title}" has been scheduled successfully!')
        return response


class MaintenanceUpdateView(LoginRequiredMixin, UpdateView):
    model = MaintenanceSchedule
    form_class = MaintenanceScheduleForm
    template_name = 'maintenance/maintenance_form.html'
    success_url = reverse_lazy('maintenance:maintenance_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Maintenance "{form.instance.title}" has been updated successfully!')
        return response


@login_required
def maintenance_detail_view(request, pk):
    maintenance = get_object_or_404(MaintenanceSchedule, pk=pk)
    parts = maintenance.parts.all()
    documents = maintenance.documents.all()
    
    # Calculate totals
    total_parts_cost = sum(part.total_cost for part in parts)
    
    context = {
        'maintenance': maintenance,
        'parts': parts,
        'documents': documents,
        'total_parts_cost': total_parts_cost,
    }
    return render(request, 'maintenance/maintenance_detail.html', context)


@login_required
def maintenance_complete_view(request, pk):
    maintenance = get_object_or_404(MaintenanceSchedule, pk=pk)
    
    if request.method == 'POST':
        actual_duration = request.POST.get('actual_duration')
        actual_cost = request.POST.get('actual_cost')
        completion_notes = request.POST.get('completion_notes', '')
        
        maintenance.complete_maintenance(
            actual_duration=int(actual_duration) if actual_duration else None,
            actual_cost=float(actual_cost) if actual_cost else None,
            completion_notes=completion_notes,
            completed_by=request.user
        )
        
        messages.success(request, f'Maintenance "{maintenance.title}" has been completed!')
        return redirect('maintenance:maintenance_list')  # Redirect to maintenance list after completion
    
    return render(request, 'maintenance/maintenance_complete.html', {'maintenance': maintenance})


@login_required
def maintenance_parts_view(request, pk):
    maintenance = get_object_or_404(MaintenanceSchedule, pk=pk)
    parts = maintenance.parts.all()
    
    if request.method == 'POST':
        form = MaintenancePartForm(request.POST)
        if form.is_valid():
            part = form.save(commit=False)
            part.maintenance_schedule = maintenance
            part.save()
            messages.success(request, 'Part added successfully!')
            return redirect('maintenance:maintenance_parts', pk=maintenance.pk)
    else:
        form = MaintenancePartForm()
    
    # Calculate total costs
    total_parts_cost = sum(part.total_cost for part in parts)
    total_estimated_cost = total_parts_cost + (maintenance.estimated_cost or 0)
    
    context = {
        'maintenance': maintenance,
        'parts': parts,
        'form': form,
        'total_parts_cost': total_parts_cost,
        'total_estimated_cost': total_estimated_cost,
    }
    return render(request, 'maintenance/maintenance_parts.html', context)


@login_required
def maintenance_documents_view(request, pk):
    maintenance = get_object_or_404(MaintenanceSchedule, pk=pk)
    documents = maintenance.documents.all()
    
    if request.method == 'POST':
        form = MaintenanceDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.maintenance_schedule = maintenance
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('maintenance:maintenance_documents', pk=maintenance.pk)
    else:
        form = MaintenanceDocumentForm()
    
    # Calculate formatted file sizes for each document
    documents_with_sizes = []
    for document in documents:
        if document.file and document.file.size:
            size = document.file.size
            if size < 1024:
                formatted_size = f"{size} B"
            elif size < 1048576:
                formatted_size = f"{size / 1024:.1f} KB"
            else:
                formatted_size = f"{size / 1048576:.1f} MB"
        else:
            formatted_size = "N/A"
        
        documents_with_sizes.append({
            'document': document,
            'formatted_size': formatted_size
        })
    
    # Calculate document type counts
    document_type_counts = {
        'invoice': documents.filter(document_type='invoice').count(),
        'photo': documents.filter(document_type='photo').count(),
        'report': documents.filter(document_type='report').count(),
        'other': documents.filter(document_type='other').count(),
    }
    
    context = {
        'maintenance': maintenance,
        'documents': documents,
        'documents_with_sizes': documents_with_sizes,
        'document_type_counts': document_type_counts,
        'form': form,
    }
    return render(request, 'maintenance/maintenance_documents.html', context)


@login_required
def maintenance_dashboard(request):
    """Dashboard view with maintenance statistics"""
    total_maintenance = MaintenanceSchedule.objects.count()
    scheduled_maintenance = MaintenanceSchedule.objects.filter(status='scheduled').count()
    in_progress_maintenance = MaintenanceSchedule.objects.filter(status='in_progress').count()
    completed_maintenance = MaintenanceSchedule.objects.filter(status='completed').count()
    
    # Overdue maintenance
    overdue_maintenance = MaintenanceSchedule.objects.filter(
        status='scheduled',
        scheduled_date__lt=timezone.now()
    )
    
    # Upcoming maintenance (next 7 days)
    upcoming_maintenance = MaintenanceSchedule.objects.filter(
        status='scheduled',
        scheduled_date__lte=timezone.now() + timezone.timedelta(days=7),
        scheduled_date__gt=timezone.now()
    )
    
    context = {
        'total_maintenance': total_maintenance,
        'scheduled_maintenance': scheduled_maintenance,
        'in_progress_maintenance': in_progress_maintenance,
        'completed_maintenance': completed_maintenance,
        'overdue_maintenance': overdue_maintenance,
        'upcoming_maintenance': upcoming_maintenance,
    }
    return render(request, 'maintenance/dashboard.html', context)

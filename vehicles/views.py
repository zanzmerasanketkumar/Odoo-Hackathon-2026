from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from .models import Vehicle, VehicleType, VehicleDocument
from .forms import VehicleForm, VehicleDocumentForm


class VehicleListView(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = 'vehicles/vehicle_list.html'
    context_object_name = 'vehicles'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Vehicle.objects.filter(is_active=True)
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(license_plate__icontains=search_query) |
                Q(model__icontains=search_query)
            )
        
        # Filter by status
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by vehicle type
        type_filter = self.request.GET.get('vehicle_type', '')
        if type_filter:
            queryset = queryset.filter(vehicle_type_id=type_filter)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicle_types'] = VehicleType.objects.all()
        context['status_choices'] = Vehicle.STATUS_CHOICES
        return context


class VehicleCreateView(LoginRequiredMixin, CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'vehicles/vehicle_form.html'
    success_url = reverse_lazy('vehicle_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Vehicle "{form.instance.name}" has been created successfully!')
        return response


class VehicleUpdateView(LoginRequiredMixin, UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'vehicles/vehicle_form.html'
    success_url = reverse_lazy('vehicle_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Vehicle "{form.instance.name}" has been updated successfully!')
        return response


class VehicleDeleteView(LoginRequiredMixin, DeleteView):
    model = Vehicle
    template_name = 'vehicles/vehicle_confirm_delete.html'
    success_url = reverse_lazy('vehicle_list')
    
    def delete(self, request, *args, **kwargs):
        vehicle = self.get_object()
        vehicle.is_active = False
        vehicle.save()
        messages.success(request, f'Vehicle "{vehicle.name}" has been deactivated.')
        return redirect(self.success_url)


@login_required
def vehicle_detail_view(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, is_active=True)
    documents = vehicle.documents.all()
    
    # Get recent trips for this vehicle
    from trips.models import Trip
    recent_trips = Trip.objects.filter(vehicle=vehicle).order_by('-created_at')[:5]
    
    # Get maintenance records
    from maintenance.models import MaintenanceSchedule
    maintenance_records = MaintenanceSchedule.objects.filter(vehicle=vehicle).order_by('-scheduled_date')[:5]
    
    context = {
        'vehicle': vehicle,
        'documents': documents,
        'recent_trips': recent_trips,
        'maintenance_records': maintenance_records,
    }
    return render(request, 'vehicles/vehicle_detail.html', context)


@login_required
def vehicle_documents_view(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, is_active=True)
    documents = vehicle.documents.all()
    
    if request.method == 'POST':
        form = VehicleDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.vehicle = vehicle
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('vehicles:vehicle_documents', pk=vehicle.pk)
    else:
        form = VehicleDocumentForm()
    
    context = {
        'vehicle': vehicle,
        'documents': documents,
        'form': form,
    }
    return render(request, 'vehicles/vehicle_documents.html', context)

@login_required
def vehicle_document_delete_view(request, document_id):
    document = get_object_or_404(VehicleDocument, pk=document_id)
    vehicle_pk = document.vehicle.pk
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document deleted successfully!')
        return redirect('vehicles:vehicle_documents', pk=vehicle_pk)
    
    return redirect('vehicles:vehicle_documents', pk=vehicle_pk)


@login_required
def get_available_vehicles(request):
    """API endpoint to get available vehicles for trip assignment"""
    vehicles = Vehicle.objects.filter(
        status='available',
        is_active=True
    ).values('id', 'name', 'license_plate', 'capacity', 'model')
    
    return JsonResponse({'vehicles': list(vehicles)})


@login_required
def check_vehicle_capacity(request):
    """API endpoint to check if vehicle can handle cargo weight"""
    vehicle_id = request.GET.get('vehicle_id')
    cargo_weight = request.GET.get('cargo_weight', 0)
    
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id, is_active=True)
        can_carry = float(vehicle.capacity) >= float(cargo_weight)
        
        return JsonResponse({
            'can_carry': can_carry,
            'vehicle_capacity': float(vehicle.capacity),
            'cargo_weight': float(cargo_weight)
        })
    except Vehicle.DoesNotExist:
        return JsonResponse({'error': 'Vehicle not found'}, status=404)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count, Sum, Avg
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Trip, TripExpense, TripCheckpoint, TripDocument
from .forms import TripForm, TripExpenseForm, TripCheckpointForm, TripDocumentForm


class TripListView(LoginRequiredMixin, ListView):
    model = Trip
    template_name = 'trips/trip_list.html'
    context_object_name = 'trips'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Trip.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(trip_number__icontains=search_query) |
                Q(origin__icontains=search_query) |
                Q(destination__icontains=search_query) |
                Q(driver__first_name__icontains=search_query) |
                Q(driver__last_name__icontains=search_query) |
                Q(vehicle__name__icontains=search_query) |
                Q(vehicle__license_plate__icontains=search_query)
            )
        
        # Filter by status
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by priority
        priority_filter = self.request.GET.get('priority', '')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        # Filter by date range
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(start_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_date__date__lte=end_date)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Trip.STATUS_CHOICES
        context['priority_choices'] = Trip.PRIORITY_CHOICES
        return context


class TripCreateView(LoginRequiredMixin, CreateView):
    model = Trip
    form_class = TripForm
    template_name = 'trips/trip_form.html'
    success_url = reverse_lazy('trips:trip_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f'Trip "{form.instance.trip_number}" has been created successfully!')
        return response
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class TripUpdateView(LoginRequiredMixin, UpdateView):
    model = Trip
    form_class = TripForm
    template_name = 'trips/trip_form.html'
    success_url = reverse_lazy('trips:trip_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Trip "{form.instance.trip_number}" has been updated successfully!')
        return response
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class TripDeleteView(LoginRequiredMixin, DeleteView):
    model = Trip
    template_name = 'trips/trip_confirm_delete.html'
    success_url = reverse_lazy('trips:trip_list')
    
    def delete(self, request, *args, **kwargs):
        trip = self.get_object()
        messages.success(request, f'Trip "{trip.trip_number}" has been deleted.')
        return super().delete(request, *args, **kwargs)


@login_required
def trip_detail_view(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    expenses = trip.expenses.all()
    checkpoints = trip.checkpoints.all()
    documents = trip.documents.all()
    
    context = {
        'trip': trip,
        'expenses': expenses,
        'checkpoints': checkpoints,
        'documents': documents,
    }
    return render(request, 'trips/trip_detail.html', context)


@login_required
def trip_dispatch_view(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    
    if trip.can_dispatch():
        if trip.dispatch(dispatched_by=request.user):
            messages.success(request, f'Trip "{trip.trip_number}" has been dispatched successfully!')
        else:
            messages.error(request, 'Failed to dispatch trip. Please check vehicle and driver availability.')
    else:
        messages.error(request, 'This trip cannot be dispatched. Please check all requirements.')
    
    return redirect('trips:trip_detail', pk=trip.pk)


@login_required
def trip_start_view(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    
    if trip.start_trip():
        messages.success(request, f'Trip "{trip.trip_number}" has been started!')
    else:
        messages.error(request, 'Failed to start trip.')
    
    return redirect('trips:trip_detail', pk=trip.pk)


@login_required
def trip_complete_view(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    
    if request.method == 'POST':
        actual_distance = request.POST.get('actual_distance')
        actual_duration = request.POST.get('actual_duration')
        
        if trip.complete_trip(
            actual_distance=float(actual_distance) if actual_distance else None,
            actual_duration=int(actual_duration) if actual_duration else None
        ):
            messages.success(request, f'Trip "{trip.trip_number}" has been completed!')
            return redirect('trips:trip_list')  # Redirect to trips list after completion
        else:
            messages.error(request, 'Failed to complete trip.')
    
    return redirect('trips:trip_detail', pk=trip.pk)


@login_required
def trip_cancel_view(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    
    if request.method == 'POST':
        reason = request.POST.get('cancellation_reason', '')
        
        if trip.cancel_trip(reason=reason):
            messages.success(request, f'Trip "{trip.trip_number}" has been cancelled.')
        else:
            messages.error(request, 'Failed to cancel trip.')
    
    return redirect('trips:trip_detail', pk=trip.pk)


@login_required
def trip_expenses_view(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    expenses = trip.expenses.all()
    
    # Calculate totals
    total_expenses = sum(expense.amount for expense in expenses)
    average_expense = total_expenses / expenses.count() if expenses.count() > 0 else 0
    
    if request.method == 'POST':
        form = TripExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.trip = trip
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('trips:trip_expenses', pk=trip.pk)
    else:
        form = TripExpenseForm()
    
    context = {
        'trip': trip,
        'expenses': expenses,
        'form': form,
        'total_expenses': total_expenses,
        'average_expense': average_expense,
    }
    return render(request, 'trips/trip_expenses.html', context)


@login_required
def trip_checkpoints_view(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    checkpoints = trip.checkpoints.all()
    
    if request.method == 'POST':
        form = TripCheckpointForm(request.POST)
        if form.is_valid():
            checkpoint = form.save(commit=False)
            checkpoint.trip = trip
            checkpoint.save()
            messages.success(request, 'Checkpoint added successfully!')
            return redirect('trips:trip_checkpoints', pk=trip.pk)
    else:
        form = TripCheckpointForm()
    
    context = {
        'trip': trip,
        'checkpoints': checkpoints,
        'form': form,
    }
    return render(request, 'trips/trip_checkpoints.html', context)


@login_required
def trip_documents_view(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    documents = trip.documents.all()
    
    if request.method == 'POST':
        form = TripDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.trip = trip
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('trips:trip_documents', pk=trip.pk)
    else:
        form = TripDocumentForm()
    
    context = {
        'trip': trip,
        'documents': documents,
        'form': form,
    }
    return render(request, 'trips/trip_documents.html', context)


@login_required
def trip_dashboard(request):
    """Dashboard view with trip statistics"""
    total_trips = Trip.objects.count()
    active_trips = Trip.objects.filter(status__in=['dispatched', 'in_progress']).count()
    completed_trips = Trip.objects.filter(status='completed').count()
    cancelled_trips = Trip.objects.filter(status='cancelled').count()
    
    # Recent trips
    recent_trips = Trip.objects.order_by('-created_at')[:10]
    
    # Overdue trips
    overdue_trips = Trip.objects.filter(
        status='dispatched',
        start_date__lt=timezone.now() - timezone.timedelta(hours=1)
    )
    
    context = {
        'total_trips': total_trips,
        'active_trips': active_trips,
        'completed_trips': completed_trips,
        'cancelled_trips': cancelled_trips,
        'recent_trips': recent_trips,
        'overdue_trips': overdue_trips,
    }
    return render(request, 'trips/dashboard.html', context)


@login_required
def get_trip_stats(request):
    """API endpoint to get trip statistics for dashboard"""
    stats = {
        'total': Trip.objects.count(),
        'draft': Trip.objects.filter(status='draft').count(),
        'dispatched': Trip.objects.filter(status='dispatched').count(),
        'in_progress': Trip.objects.filter(status='in_progress').count(),
        'completed': Trip.objects.filter(status='completed').count(),
        'cancelled': Trip.objects.filter(status='cancelled').count(),
    }
    return JsonResponse(stats)


@login_required
def trip_expense_create_view(request, pk):
    """Create a new expense for a specific trip"""
    trip = get_object_or_404(Trip, pk=pk)
    
    if request.method == 'POST':
        form = TripExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.trip = trip
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('trips:trip_expenses', pk=trip.pk)
    else:
        form = TripExpenseForm()
    
    context = {
        'trip': trip,
        'form': form,
        'page_title': f'Add Expense - {trip.trip_number}',
    }
    return render(request, 'trips/trip_expense_create.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Avg
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import FuelStation, FuelLog, Expense, FuelBudget
from .forms import FuelLogForm, ExpenseForm, FuelBudgetForm, FuelStationForm


class FuelLogListView(LoginRequiredMixin, ListView):
    model = FuelLog
    template_name = 'fuel/fuel_log_list.html'
    context_object_name = 'fuel_logs'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = FuelLog.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(vehicle__name__icontains=search_query) |
                Q(vehicle__license_plate__icontains=search_query) |
                Q(driver__first_name__icontains=search_query) |
                Q(driver__last_name__icontains=search_query) |
                Q(fuel_station__name__icontains=search_query)
            )
        
        # Filter by vehicle
        vehicle_filter = self.request.GET.get('vehicle', '')
        if vehicle_filter:
            queryset = queryset.filter(vehicle_id=vehicle_filter)
        
        # Filter by date range
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(fuel_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(fuel_date__date__lte=end_date)
        
        return queryset.order_by('-fuel_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from vehicles.models import Vehicle
        context['vehicles'] = Vehicle.objects.filter(is_active=True)
        return context


class FuelLogCreateView(LoginRequiredMixin, CreateView):
    model = FuelLog
    form_class = FuelLogForm
    template_name = 'fuel/fuel_log_form.html'
    success_url = reverse_lazy('fuel:fuel_log_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Fuel log has been added successfully!')
        return response


class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'fuel/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Expense.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(description__icontains=search_query) |
                Q(vendor__icontains=search_query) |
                Q(vehicle__name__icontains=search_query) |
                Q(driver__first_name__icontains=search_query) |
                Q(driver__last_name__icontains=search_query)
            )
        
        # Filter by expense type
        type_filter = self.request.GET.get('expense_type', '')
        if type_filter:
            queryset = queryset.filter(expense_type=type_filter)
        
        # Filter by date range
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(expense_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(expense_date__lte=end_date)
        
        return queryset.order_by('-expense_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expense_types'] = Expense.EXPENSE_TYPES
        return context


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'fuel/expense_form.html'
    success_url = reverse_lazy('fuel:expense_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Expense has been added successfully!')
        return response


class FuelBudgetListView(LoginRequiredMixin, ListView):
    model = FuelBudget
    template_name = 'fuel/fuel_budget_list.html'
    context_object_name = 'fuel_budgets'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = FuelBudget.objects.all()
        
        # Filter by period
        period_filter = self.request.GET.get('period', '')
        if period_filter:
            queryset = queryset.filter(period=period_filter)
        
        # Filter by active status
        active_filter = self.request.GET.get('is_active', '')
        if active_filter:
            queryset = queryset.filter(is_active=active_filter == 'true')
        
        return queryset.order_by('-start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['period_choices'] = FuelBudget.PERIOD_CHOICES
        return context


class FuelBudgetCreateView(LoginRequiredMixin, CreateView):
    model = FuelBudget
    form_class = FuelBudgetForm
    template_name = 'fuel/fuel_budget_form.html'
    success_url = reverse_lazy('fuel:fuel_budget_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Fuel budget has been created successfully!')
        return response


@login_required
def fuel_dashboard(request):
    """Dashboard view with fuel and expense statistics"""
    
    # Fuel statistics
    total_fuel_logs = FuelLog.objects.count()
    total_fuel_consumed = FuelLog.objects.aggregate(
        total=Sum('fuel_liters')
    )['total'] or 0
    total_fuel_cost = FuelLog.objects.aggregate(
        total=Sum('total_cost')
    )['total'] or 0
    
    # Average fuel efficiency
    avg_fuel_efficiency = FuelLog.objects.filter(
        fuel_efficiency__isnull=False
    ).aggregate(
        avg=Avg('fuel_efficiency')
    )['avg'] or 0
    
    # Expense statistics
    total_expenses = Expense.objects.count()
    total_expense_amount = Expense.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Recent fuel logs
    recent_fuel_logs = FuelLog.objects.order_by('-fuel_date')[:10]
    
    # Recent expenses
    recent_expenses = Expense.objects.order_by('-expense_date')[:10]
    
    # Budget utilization
    active_budgets = FuelBudget.objects.filter(is_active=True)
    
    context = {
        'total_fuel_logs': total_fuel_logs,
        'total_fuel_consumed': total_fuel_consumed,
        'total_fuel_cost': total_fuel_cost,
        'avg_fuel_efficiency': round(avg_fuel_efficiency, 2),
        'total_expenses': total_expenses,
        'total_expense_amount': total_expense_amount,
        'recent_fuel_logs': recent_fuel_logs,
        'recent_expenses': recent_expenses,
        'active_budgets': active_budgets,
    }
    return render(request, 'fuel/dashboard.html', context)


@login_required
def fuel_efficiency_report(request):
    """Generate fuel efficiency report"""
    from vehicles.models import Vehicle
    
    vehicles = Vehicle.objects.filter(is_active=True)
    vehicle_efficiency = []
    
    for vehicle in vehicles:
        fuel_logs = FuelLog.objects.filter(
            vehicle=vehicle,
            fuel_efficiency__isnull=False
        )
        
        if fuel_logs.exists():
            avg_efficiency = fuel_logs.aggregate(
                avg=Avg('fuel_efficiency')
            )['avg'] or 0
            
            total_distance = fuel_logs.aggregate(
                total=Sum('distance_traveled')
            )['total'] or 0
            
            total_fuel = fuel_logs.aggregate(
                total=Sum('fuel_liters')
            )['total'] or 0
            
            vehicle_efficiency.append({
                'vehicle': vehicle,
                'avg_efficiency': round(avg_efficiency, 2),
                'total_distance': total_distance,
                'total_fuel': total_fuel,
                'logs_count': fuel_logs.count()
            })
    
    context = {
        'vehicle_efficiency': vehicle_efficiency,
    }
    return render(request, 'fuel/fuel_efficiency_report.html', context)


@login_required
def get_fuel_stats(request):
    """API endpoint to get fuel statistics for dashboard"""
    from datetime import datetime
    
    # Get date range from request
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    fuel_logs = FuelLog.objects.filter(fuel_date__gte=start_date)
    
    stats = {
        'total_logs': fuel_logs.count(),
        'total_liters': float(fuel_logs.aggregate(total=Sum('fuel_liters'))['total'] or 0),
        'total_cost': float(fuel_logs.aggregate(total=Sum('total_cost'))['total'] or 0),
        'avg_efficiency': float(fuel_logs.filter(fuel_efficiency__isnull=False).aggregate(avg=Avg('fuel_efficiency'))['avg'] or 0),
    }
    
    return JsonResponse(stats)

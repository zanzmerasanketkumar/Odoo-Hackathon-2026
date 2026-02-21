from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Count, Sum, Avg, Q
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta, datetime
from .models import DashboardKPI, Report, Alert, SystemMetric, Notification
from .forms import ReportForm
from vehicles.models import Vehicle
from drivers.models import Driver
from trips.models import Trip
from fuel.models import FuelLog, Expense
from maintenance.models import MaintenanceSchedule
import json
import csv


@login_required
def dashboard_view(request):
    """Main analytics dashboard"""
    
    # Calculate KPIs
    total_vehicles = Vehicle.objects.filter(is_active=True).count()
    available_vehicles = Vehicle.objects.filter(status='available', is_active=True).count()
    vehicles_on_trip = Vehicle.objects.filter(status='on_trip', is_active=True).count()
    vehicles_in_maintenance = Vehicle.objects.filter(status='in_shop', is_active=True).count()
    
    total_drivers = Driver.objects.filter(is_active=True).count()
    available_drivers = Driver.objects.filter(status='on_duty', is_active=True).count()
    
    active_trips = Trip.objects.filter(status__in=['dispatched', 'in_progress']).count()
    completed_trips = Trip.objects.filter(status='completed').count()
    
    # Fleet utilization
    if total_vehicles > 0:
        fleet_utilization = round((vehicles_on_trip / total_vehicles) * 100, 2)
    else:
        fleet_utilization = 0
    
    # Financial metrics
    total_fuel_cost = FuelLog.objects.aggregate(
        total=Sum('total_cost')
    )['total'] or 0
    
    total_expenses = Expense.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    total_operational_cost = total_fuel_cost + total_expenses
    
    # Update KPIs in database
    DashboardKPI.objects.update_or_create(
        kpi_type='total_vehicles',
        defaults={'value': total_vehicles, 'unit': 'vehicles'}
    )
    DashboardKPI.objects.update_or_create(
        kpi_type='available_vehicles',
        defaults={'value': available_vehicles, 'unit': 'vehicles'}
    )
    DashboardKPI.objects.update_or_create(
        kpi_type='vehicles_on_trip',
        defaults={'value': vehicles_on_trip, 'unit': 'vehicles'}
    )
    DashboardKPI.objects.update_or_create(
        kpi_type='vehicles_in_maintenance',
        defaults={'value': vehicles_in_maintenance, 'unit': 'vehicles'}
    )
    DashboardKPI.objects.update_or_create(
        kpi_type='total_drivers',
        defaults={'value': total_drivers, 'unit': 'drivers'}
    )
    DashboardKPI.objects.update_or_create(
        kpi_type='available_drivers',
        defaults={'value': available_drivers, 'unit': 'drivers'}
    )
    DashboardKPI.objects.update_or_create(
        kpi_type='active_trips',
        defaults={'value': active_trips, 'unit': 'trips'}
    )
    DashboardKPI.objects.update_or_create(
        kpi_type='completed_trips',
        defaults={'value': completed_trips, 'unit': 'trips'}
    )
    DashboardKPI.objects.update_or_create(
        kpi_type='total_revenue',
        defaults={'value': 0, 'unit': '$'}  # Would be calculated from actual revenue
    )
    DashboardKPI.objects.update_or_create(
        kpi_type='total_expenses',
        defaults={'value': total_operational_cost, 'unit': '$'}
    )
    DashboardKPI.objects.update_or_create(
        kpi_type='fleet_utilization',
        defaults={'value': fleet_utilization, 'unit': '%'}
    )
    
    # Get recent alerts
    recent_alerts = Alert.objects.filter(status='active').order_by('-created_at')[:10]
    
    # Get recent notifications for user
    recent_notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    context = {
        'total_vehicles': total_vehicles,
        'available_vehicles': available_vehicles,
        'vehicles_on_trip': vehicles_on_trip,
        'vehicles_in_maintenance': vehicles_in_maintenance,
        'total_drivers': total_drivers,
        'available_drivers': available_drivers,
        'active_trips': active_trips,
        'completed_trips': completed_trips,
        'fleet_utilization': fleet_utilization,
        'total_fuel_cost': total_fuel_cost,
        'total_expenses': total_expenses,
        'total_operational_cost': total_operational_cost,
        'recent_alerts': recent_alerts,
        'recent_notifications': recent_notifications,
    }
    
    return render(request, 'analytics/dashboard.html', context)


class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'analytics/report_list.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        return Report.objects.order_by('-created_at')


class ReportCreateView(LoginRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'analytics/report_form.html'
    success_url = reverse_lazy('analytics:reports')
    
    def form_valid(self, form):
        form.instance.generated_by = self.request.user
        messages.success(self.request, 'Report created successfully!')
        return super().form_valid(form)


class ReportUpdateView(LoginRequiredMixin, UpdateView):
    model = Report
    form_class = ReportForm
    template_name = 'analytics/report_form.html'
    success_url = reverse_lazy('analytics:reports')
    
    def form_valid(self, form):
        messages.success(self.request, 'Report updated successfully!')
        return super().form_valid(form)


class ReportDeleteView(LoginRequiredMixin, DeleteView):
    model = Report
    template_name = 'analytics/report_confirm_delete.html'
    success_url = reverse_lazy('analytics:reports')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Report deleted successfully!')
        return super().delete(request, *args, **kwargs)


@login_required
def generate_report(request, pk):
    """Generate and download report"""
    report = get_object_or_404(Report, pk=pk)
    
    if report.report_type == 'trip_summary':
        data = generate_trip_summary_report(report.start_date, report.end_date)
    elif report.report_type == 'vehicle_performance':
        data = generate_vehicle_performance_report(report.start_date, report.end_date)
    elif report.report_type == 'driver_performance':
        data = generate_driver_performance_report(report.start_date, report.end_date)
    elif report.report_type == 'fuel_consumption':
        data = generate_fuel_consumption_report(report.start_date, report.end_date)
    elif report.report_type == 'expense_report':
        data = generate_expense_report(report.start_date, report.end_date)
    else:
        data = {}
    
    # Save data to report
    report.data = data
    report.is_generated = True
    report.generated_at = timezone.now()
    report.save()
    
    if report.file_format == 'csv':
        return generate_csv_report(report, data)
    elif report.file_format == 'excel':
        return generate_excel_report(report, data)
    else:  # PDF
        return generate_pdf_report(report, data)


def generate_trip_summary_report(start_date, end_date):
    """Generate trip summary report data"""
    trips = Trip.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )
    
    data = {
        'total_trips': trips.count(),
        'completed_trips': trips.filter(status='completed').count(),
        'cancelled_trips': trips.filter(status='cancelled').count(),
        'active_trips': trips.filter(status__in=['dispatched', 'in_progress']).count(),
        'trips_by_status': dict(trips.values('status').annotate(count=Count('id')).values_list('status', 'count')),
        'trips_by_priority': dict(trips.values('priority').annotate(count=Count('id')).values_list('priority', 'count')),
    }
    
    return data


def generate_vehicle_performance_report(start_date, end_date):
    """Generate vehicle performance report data"""
    vehicles = Vehicle.objects.filter(is_active=True)
    vehicle_data = []
    
    for vehicle in vehicles:
        trips = Trip.objects.filter(
            vehicle=vehicle,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        fuel_logs = FuelLog.objects.filter(
            vehicle=vehicle,
            fuel_date__date__gte=start_date,
            fuel_date__date__lte=end_date
        )
        
        total_distance = trips.filter(status='completed').aggregate(
            total=Sum('actual_distance')
        )['total'] or 0
        
        total_fuel = fuel_logs.aggregate(
            total=Sum('fuel_liters')
        )['total'] or 0
        
        fuel_efficiency = (total_distance / total_fuel) if total_fuel > 0 else 0
        
        vehicle_data.append({
            'vehicle_name': vehicle.name,
            'license_plate': vehicle.license_plate,
            'total_trips': trips.count(),
            'completed_trips': trips.filter(status='completed').count(),
            'total_distance': float(total_distance),
            'total_fuel': float(total_fuel),
            'fuel_efficiency': round(fuel_efficiency, 2),
        })
    
    return {'vehicles': vehicle_data}


def generate_driver_performance_report(start_date, end_date):
    """Generate driver performance report data"""
    drivers = Driver.objects.filter(is_active=True)
    driver_data = []
    
    for driver in drivers:
        trips = Trip.objects.filter(
            driver=driver,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        total_distance = trips.filter(status='completed').aggregate(
            total=Sum('actual_distance')
        )['total'] or 0
        
        driver_data.append({
            'driver_name': driver.full_name,
            'total_trips': trips.count(),
            'completed_trips': trips.filter(status='completed').count(),
            'cancelled_trips': trips.filter(status='cancelled').count(),
            'total_distance': float(total_distance),
            'completion_rate': round((trips.filter(status='completed').count() / trips.count() * 100) if trips.count() > 0 else 0, 2),
        })
    
    return {'drivers': driver_data}


def generate_fuel_consumption_report(start_date, end_date):
    """Generate fuel consumption report data"""
    fuel_logs = FuelLog.objects.filter(
        fuel_date__date__gte=start_date,
        fuel_date__date__lte=end_date
    )
    
    data = {
        'total_fuel_consumed': float(fuel_logs.aggregate(total=Sum('fuel_liters'))['total'] or 0),
        'total_fuel_cost': float(fuel_logs.aggregate(total=Sum('total_cost'))['total'] or 0),
        'average_cost_per_liter': float(fuel_logs.aggregate(avg=Avg('cost_per_liter'))['avg'] or 0),
        'fuel_by_type': dict(fuel_logs.values('fuel_type').annotate(
            total_liters=Sum('fuel_liters'),
            total_cost=Sum('total_cost')
        ).values_list('fuel_type', 'total_liters', 'total_cost')),
    }
    
    return data


def generate_expense_report(start_date, end_date):
    """Generate expense report data"""
    expenses = Expense.objects.filter(
        expense_date__gte=start_date,
        expense_date__lte=end_date
    )
    
    data = {
        'total_expenses': float(expenses.aggregate(total=Sum('amount'))['total'] or 0),
        'expenses_by_type': dict(expenses.values('expense_type').annotate(
            total_amount=Sum('amount'),
            count=Count('id')
        ).values_list('expense_type', 'total_amount', 'count')),
    }
    
    return data


def generate_csv_report(report, data):
    """Generate CSV report"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report.file_name}"'
    
    writer = csv.writer(response)
    
    if report.report_type == 'trip_summary':
        writer.writerow(['Trip Summary Report'])
        writer.writerow(['Period', f'{report.start_date} to {report.end_date}'])
        writer.writerow([])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Trips', data.get('total_trips', 0)])
        writer.writerow(['Completed Trips', data.get('completed_trips', 0)])
        writer.writerow(['Cancelled Trips', data.get('cancelled_trips', 0)])
        writer.writerow(['Active Trips', data.get('active_trips', 0)])
    
    return response


def generate_excel_report(report, data):
    """Generate Excel report (placeholder)"""
    # This would use a library like openpyxl to generate Excel files
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{report.file_name}"'
    
    # Placeholder - in production, use openpyxl or similar
    response.write(b'Excel report generation not implemented')
    
    return response


def generate_pdf_report(report, data):
    """Generate PDF report (placeholder)"""
    # This would use a library like ReportLab to generate PDF files
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report.file_name}"'
    
    # Placeholder - in production, use ReportLab
    response.write(b'PDF report generation not implemented')
    
    return response


@login_required
def alerts_view(request):
    """View and manage alerts"""
    alerts = Alert.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        alerts = alerts.filter(status=status_filter)
    
    # Filter by severity
    severity_filter = request.GET.get('severity', '')
    if severity_filter:
        alerts = alerts.filter(severity=severity_filter)
    
    context = {
        'alerts': alerts,
        'status_choices': Alert.STATUS_CHOICES,
        'severity_choices': Alert.SEVERITY_CHOICES,
    }
    
    return render(request, 'analytics/alerts.html', context)


@login_required
def acknowledge_alert(request, pk):
    """Acknowledge an alert"""
    alert = get_object_or_404(Alert, pk=pk)
    alert.acknowledge(request.user)
    messages.success(request, f'Alert "{alert.title}" has been acknowledged.')
    return redirect('analytics:alerts')


@login_required
def resolve_alert(request, pk):
    """Resolve an alert"""
    alert = get_object_or_404(Alert, pk=pk)
    
    if request.method == 'POST':
        action_taken = request.POST.get('action_taken', '')
        alert.resolve(request.user, action_taken)
        messages.success(request, f'Alert "{alert.title}" has been resolved.')
    
    return redirect('analytics:alerts')

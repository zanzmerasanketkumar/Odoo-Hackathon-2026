from django.db import models
from django.utils import timezone
from decimal import Decimal
import json


class DashboardKPI(models.Model):
    KPI_TYPES = [
        ('total_vehicles', 'Total Vehicles'),
        ('active_vehicles', 'Active Vehicles'),
        ('vehicles_on_trip', 'Vehicles on Trip'),
        ('vehicles_in_maintenance', 'Vehicles in Maintenance'),
        ('total_drivers', 'Total Drivers'),
        ('available_drivers', 'Available Drivers'),
        ('active_trips', 'Active Trips'),
        ('completed_trips', 'Completed Trips'),
        ('total_revenue', 'Total Revenue'),
        ('total_expenses', 'Total Expenses'),
        ('fuel_efficiency', 'Fuel Efficiency'),
        ('fleet_utilization', 'Fleet Utilization'),
    ]
    
    kpi_type = models.CharField(max_length=50, choices=KPI_TYPES, unique=True)
    value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    unit = models.CharField(max_length=20, blank=True)  # e.g., '%', 'km/l', '$'
    trend = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # percentage change
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dashboard KPI"
        verbose_name_plural = "Dashboard KPIs"
    
    def __str__(self):
        return f"{self.get_kpi_type_display()}: {self.value} {self.unit}"


class Report(models.Model):
    REPORT_TYPES = [
        ('trip_summary', 'Trip Summary'),
        ('vehicle_performance', 'Vehicle Performance'),
        ('driver_performance', 'Driver Performance'),
        ('fuel_consumption', 'Fuel Consumption'),
        ('maintenance_summary', 'Maintenance Summary'),
        ('expense_report', 'Expense Report'),
        ('revenue_report', 'Revenue Report'),
        ('fleet_utilization', 'Fleet Utilization'),
        ('safety_report', 'Safety Report'),
    ]
    
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom'),
    ]
    
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    parameters = models.JSONField(default=dict, blank=True)  # Store filter parameters
    data = models.JSONField(default=dict)  # Store report data
    file_path = models.CharField(max_length=500, blank=True)  # Path to generated file
    file_format = models.CharField(max_length=10, choices=[('pdf', 'PDF'), ('excel', 'Excel'), ('csv', 'CSV')], default='pdf')
    is_generated = models.BooleanField(default=False)
    generated_at = models.DateTimeField(null=True, blank=True)
    generated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.period} ({self.start_date} to {self.end_date})"
    
    @property
    def file_name(self):
        return f"{self.report_type}_{self.period}_{self.start_date}_{self.end_date}.{self.file_format}"
    
    def get_status_display(self):
        """Return human-readable status"""
        if self.is_generated:
            return "Generated"
        else:
            return "Pending"


class Alert(models.Model):
    ALERT_TYPES = [
        ('maintenance_due', 'Maintenance Due'),
        ('license_expiry', 'License Expiry'),
        ('insurance_expiry', 'Insurance Expiry'),
        ('registration_expiry', 'Registration Expiry'),
        ('fuel_budget_exceeded', 'Fuel Budget Exceeded'),
        ('vehicle_overdue', 'Vehicle Overdue'),
        ('safety_incident', 'Safety Incident'),
        ('low_fuel_efficiency', 'Low Fuel Efficiency'),
        ('expense_threshold', 'Expense Threshold'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.CASCADE, null=True, blank=True, related_name='alerts')
    driver = models.ForeignKey('drivers.Driver', on_delete=models.CASCADE, null=True, blank=True, related_name='alerts')
    trip = models.ForeignKey('trips.Trip', on_delete=models.CASCADE, null=True, blank=True, related_name='alerts')
    action_required = models.BooleanField(default=True)
    action_taken = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')
    acknowledged_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Alert"
        verbose_name_plural = "Alerts"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.severity.upper()}"
    
    @property
    def is_overdue(self):
        if self.due_date and self.status == 'active':
            return timezone.now() > self.due_date
        return False
    
    def acknowledge(self, user):
        """Acknowledge the alert"""
        self.status = 'acknowledged'
        self.acknowledged_by = user
        self.acknowledged_at = timezone.now()
        self.save()
    
    def resolve(self, user, action_taken=''):
        """Resolve the alert"""
        self.status = 'resolved'
        self.resolved_by = user
        self.resolved_at = timezone.now()
        if action_taken:
            self.action_taken = action_taken
        self.save()


class SystemMetric(models.Model):
    METRIC_TYPES = [
        ('total_distance', 'Total Distance'),
        ('total_fuel_consumed', 'Total Fuel Consumed'),
        ('average_fuel_efficiency', 'Average Fuel Efficiency'),
        ('total_maintenance_cost', 'Total Maintenance Cost'),
        ('total_fuel_cost', 'Total Fuel Cost'),
        ('total_expenses', 'Total Expenses'),
        ('vehicle_utilization_rate', 'Vehicle Utilization Rate'),
        ('driver_utilization_rate', 'Driver Utilization Rate'),
        ('trip_completion_rate', 'Trip Completion Rate'),
        ('average_trip_duration', 'Average Trip Duration'),
        ('safety_score', 'Safety Score'),
        ('customer_satisfaction', 'Customer Satisfaction'),
    ]
    
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    value = models.DecimalField(max_digits=15, decimal_places=4)
    unit = models.CharField(max_length=20)  # e.g., 'km', 'liters', 'km/l', '$', '%'
    date = models.DateField()
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.CASCADE, null=True, blank=True, related_name='metrics')
    driver = models.ForeignKey('drivers.Driver', on_delete=models.CASCADE, null=True, blank=True, related_name='metrics')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "System Metric"
        verbose_name_plural = "System Metrics"
        ordering = ['-date']
        unique_together = ['metric_type', 'date', 'vehicle', 'driver']
    
    def __str__(self):
        target = f"{self.vehicle.name}" if self.vehicle else f"{self.driver.full_name}" if self.driver else "Fleet"
        return f"{target} - {self.get_metric_type_display()}: {self.value} {self.unit}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    
    recipient = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient.username} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

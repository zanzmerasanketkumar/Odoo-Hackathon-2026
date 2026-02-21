from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal


class MaintenanceType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    estimated_duration_hours = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Maintenance Type"
        verbose_name_plural = "Maintenance Types"
    
    def __str__(self):
        return self.name


class MaintenanceSchedule(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('postponed', 'Postponed'),
    ]
    
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.CASCADE, related_name='maintenance_schedules')
    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    scheduled_date = models.DateTimeField()
    estimated_duration_hours = models.PositiveIntegerField()
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_duration_hours = models.PositiveIntegerField(null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    odometer_reading = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    performed_by = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    completion_notes = models.TextField(blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='created_maintenance')
    completed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_maintenance')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Maintenance Schedule"
        verbose_name_plural = "Maintenance Schedules"
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"{self.vehicle.name} - {self.title}"
    
    @property
    def is_overdue(self):
        return self.status == 'scheduled' and self.scheduled_date < timezone.now()
    
    @property
    def cost_variance(self):
        if self.actual_cost and self.estimated_cost:
            return float(self.actual_cost) - float(self.estimated_cost)
        return None
    
    def complete_maintenance(self, actual_duration=None, actual_cost=None, completion_notes='', completed_by=None):
        """Mark maintenance as completed"""
        self.status = 'completed'
        if actual_duration:
            self.actual_duration_hours = actual_duration
        if actual_cost:
            self.actual_cost = actual_cost
        if completion_notes:
            self.completion_notes = completion_notes
        if completed_by:
            self.completed_by = completed_by
        
        # Update vehicle status
        self.vehicle.status = 'available'
        self.vehicle.last_service_date = timezone.now().date()
        self.vehicle.save()
        
        self.save()


class MaintenancePart(models.Model):
    maintenance_schedule = models.ForeignKey(MaintenanceSchedule, on_delete=models.CASCADE, related_name='parts')
    part_name = models.CharField(max_length=200)
    part_number = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    supplier = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Maintenance Part"
        verbose_name_plural = "Maintenance Parts"
    
    def __str__(self):
        return f"{self.part_name} - {self.quantity} x ${self.unit_cost}"
    
    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)


class MaintenanceDocument(models.Model):
    DOCUMENT_TYPES = [
        ('invoice', 'Invoice'),
        ('receipt', 'Receipt'),
        ('work_order', 'Work Order'),
        ('inspection_report', 'Inspection Report'),
        ('warranty', 'Warranty'),
        ('other', 'Other'),
    ]
    
    maintenance_schedule = models.ForeignKey(MaintenanceSchedule, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='maintenance_documents/')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Maintenance Document"
        verbose_name_plural = "Maintenance Documents"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.maintenance_schedule.title} - {self.title}"


class MaintenanceReminder(models.Model):
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.CASCADE, related_name='maintenance_reminders')
    reminder_type = models.CharField(max_length=50)  # e.g., 'oil_change', 'tire_rotation'
    description = models.TextField()
    trigger_odometer = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    trigger_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_sent = models.BooleanField(default=False)
    sent_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Maintenance Reminder"
        verbose_name_plural = "Maintenance Reminders"
        ordering = ['trigger_date', 'trigger_odometer']
    
    def __str__(self):
        return f"{self.vehicle.name} - {self.reminder_type}"
    
    @property
    def is_due(self):
        """Check if reminder is due"""
        if not self.is_active or self.is_sent:
            return False
        
        due = False
        if self.trigger_odometer and self.vehicle.odometer >= self.trigger_odometer:
            due = True
        if self.trigger_date and self.trigger_date <= timezone.now().date():
            due = True
        
        return due

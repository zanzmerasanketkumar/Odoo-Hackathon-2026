from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class Trip(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('dispatched', 'Dispatched'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('delayed', 'Delayed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    trip_number = models.CharField(max_length=20, unique=True, editable=False)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    driver = models.ForeignKey('drivers.Driver', on_delete=models.PROTECT, related_name='trips')
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.PROTECT, related_name='trips')
    cargo_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Cargo weight in kg"
    )
    cargo_description = models.TextField(blank=True)
    estimated_distance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Estimated distance in km"
    )
    estimated_duration = models.PositiveIntegerField(
        help_text="Estimated duration in hours"
    )
    actual_distance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Actual distance traveled in km"
    )
    actual_duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Actual duration in hours"
    )
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_trips')
    dispatched_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='dispatched_trips')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Trip"
        verbose_name_plural = "Trips"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Trip {self.trip_number} - {self.origin} to {self.destination}"
    
    def save(self, *args, **kwargs):
        if not self.trip_number:
            # Generate unique trip number
            from datetime import datetime
            today = datetime.now().strftime('%Y%m%d')
            last_trip = Trip.objects.filter(trip_number__startswith=f'TR{today}').order_by('-trip_number').first()
            if last_trip:
                last_number = int(last_trip.trip_number[10:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.trip_number = f"TR{today}{new_number:04d}"
        
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        return self.status in ['dispatched', 'in_progress']
    
    @property
    def duration_variance(self):
        """Calculate the difference between estimated and actual duration"""
        if self.actual_duration and self.estimated_duration:
            return self.actual_duration - self.estimated_duration
        return None
    
    @property
    def distance_variance(self):
        """Calculate the difference between estimated and actual distance"""
        if self.actual_distance and self.estimated_distance:
            return float(self.actual_distance) - float(self.estimated_distance)
        return None
    
    @property
    def is_overdue(self):
        """Check if trip is overdue"""
        if self.status == 'dispatched' and self.start_date:
            return timezone.now() > self.start_date + timezone.timedelta(hours=self.estimated_duration)
        return False
    
    def can_dispatch(self):
        """Check if trip can be dispatched"""
        return (
            self.status == 'draft' and
            self.driver.is_available and
            self.vehicle.is_available and
            float(self.cargo_weight) <= float(self.vehicle.capacity)
        )
    
    def dispatch(self, dispatched_by=None):
        """Dispatch the trip"""
        if self.can_dispatch():
            self.status = 'dispatched'
            self.dispatched_by = dispatched_by
            self.start_date = timezone.now()
            
            # Update vehicle and driver status
            self.vehicle.status = 'on_trip'
            self.vehicle.save()
            
            self.save()
            return True
        return False
    
    def start_trip(self):
        """Mark trip as in progress"""
        if self.status == 'dispatched':
            self.status = 'in_progress'
            self.actual_start_time = timezone.now()
            self.save()
            return True
        return False
    
    def complete_trip(self, actual_distance=None, actual_duration=None):
        """Complete the trip"""
        if self.status == 'in_progress':
            self.status = 'completed'
            self.actual_end_time = timezone.now()
            self.end_date = timezone.now()
            
            if actual_distance is not None:
                self.actual_distance = actual_distance
            if actual_duration is not None:
                self.actual_duration = actual_duration
            
            # Update vehicle status
            self.vehicle.status = 'available'
            self.vehicle.odometer += Decimal(str(actual_distance or 0))
            self.vehicle.save()
            
            # Update driver performance
            from drivers.models import DriverPerformance
            performance, created = DriverPerformance.objects.get_or_create(driver=self.driver)
            performance.update_performance(
                trip_completed=True,
                distance=actual_distance or 0,
                fuel_consumed=0  # Will be updated from fuel logs
            )
            
            self.save()
            return True
        return False
    
    def cancel_trip(self, reason=''):
        """Cancel the trip"""
        if self.status in ['draft', 'dispatched']:
            self.status = 'cancelled'
            self.cancellation_reason = reason
            self.end_date = timezone.now()
            
            # Update vehicle status if it was on trip
            if self.vehicle.status == 'on_trip':
                self.vehicle.status = 'available'
                self.vehicle.save()
            
            # Update driver performance
            from drivers.models import DriverPerformance
            performance, created = DriverPerformance.objects.get_or_create(driver=self.driver)
            performance.update_performance(trip_completed=False)
            
            self.save()
            return True
        return False


class TripExpense(models.Model):
    EXPENSE_TYPES = [
        ('fuel', 'Fuel'),
        ('toll', 'Toll'),
        ('parking', 'Parking'),
        ('maintenance', 'Maintenance'),
        ('food', 'Food'),
        ('accommodation', 'Accommodation'),
        ('other', 'Other'),
    ]
    
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='trip_expenses')
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    receipt = models.FileField(upload_to='trip_receipts/', blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Trip Expense"
        verbose_name_plural = "Trip Expenses"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.trip.trip_number} - {self.expense_type} - ${self.amount}"


class TripCheckpoint(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='checkpoints')
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    departure_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Trip Checkpoint"
        verbose_name_plural = "Trip Checkpoints"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.trip.trip_number} - {self.location}"


class TripDocument(models.Model):
    DOCUMENT_TYPES = [
        ('bill_of_lading', 'Bill of Lading'),
        ('delivery_receipt', 'Delivery Receipt'),
        ('proof_of_delivery', 'Proof of Delivery'),
        ('insurance', 'Insurance'),
        ('permit', 'Permit'),
        ('other', 'Other'),
    ]
    
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='trip_documents/')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Trip Document"
        verbose_name_plural = "Trip Documents"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.trip.trip_number} - {self.title}"

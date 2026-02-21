from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from decimal import Decimal


class Driver(models.Model):
    STATUS_CHOICES = [
        ('on_duty', 'On Duty'),
        ('off_duty', 'Off Duty'),
        ('suspended', 'Suspended'),
        ('on_leave', 'On Leave'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    address = models.TextField()
    date_of_birth = models.DateField()
    hire_date = models.DateField()
    license_number = models.CharField(max_length=50, unique=True)
    license_type = models.CharField(max_length=50)  # e.g., "Commercial", "Heavy Vehicle"
    license_expiry = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='off_duty')
    emergency_contact = models.CharField(max_length=100)
    emergency_phone = models.CharField(max_length=20)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='driver_profiles/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Driver"
        verbose_name_plural = "Drivers"
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_available(self):
        """Check if driver is available for trip assignment"""
        return (
            self.status == 'on_duty' and 
            self.is_active and 
            not self.license_expired
        )
    
    @property
    def license_expired(self):
        """Check if driver's license has expired"""
        return self.license_expiry <= timezone.now().date()
    
    @property
    def license_expires_soon(self):
        """Check if license expires within 30 days"""
        from datetime import timedelta
        return self.license_expiry <= timezone.now().date() + timedelta(days=30)


class DriverPerformance(models.Model):
    driver = models.OneToOneField(Driver, on_delete=models.CASCADE, related_name='performance')
    total_trips = models.PositiveIntegerField(default=0)
    completed_trips = models.PositiveIntegerField(default=0)
    cancelled_trips = models.PositiveIntegerField(default=0)
    total_distance = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # km
    total_fuel_consumed = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # liters
    safety_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)  # out of 100
    on_time_performance = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)  # percentage
    customer_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)  # out of 5
    last_trip_date = models.DateField(null=True, blank=True)
    accidents_count = models.PositiveIntegerField(default=0)
    violations_count = models.PositiveIntegerField(default=0)
    bonus_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Driver Performance"
        verbose_name_plural = "Driver Performances"
    
    def __str__(self):
        return f"{self.driver.full_name} - Performance"
    
    @property
    def completion_rate(self):
        """Calculate trip completion rate"""
        if self.total_trips == 0:
            return Decimal('0.00')
        return Decimal(self.completed_trips) / Decimal(self.total_trips) * Decimal('100')
    
    @property
    def cancellation_rate(self):
        """Calculate trip cancellation rate"""
        if self.total_trips == 0:
            return Decimal('0.00')
        return Decimal(self.cancelled_trips) / Decimal(self.total_trips) * Decimal('100')
    
    @property
    def fuel_efficiency(self):
        """Calculate fuel efficiency (km per liter)"""
        if self.total_fuel_consumed == 0:
            return Decimal('0.00')
        return self.total_distance / self.total_fuel_consumed
    
    def update_performance(self, trip_completed=True, distance=0, fuel_consumed=0):
        """Update driver performance after a trip"""
        self.total_trips += 1
        if trip_completed:
            self.completed_trips += 1
            self.total_distance += Decimal(str(distance))
            self.total_fuel_consumed += Decimal(str(fuel_consumed))
            self.last_trip_date = timezone.now().date()
        else:
            self.cancelled_trips += 1
        
        # Recalculate completion rate
        self.save()


class DriverDocument(models.Model):
    DOCUMENT_TYPES = [
        ('license', 'Driving License'),
        ('medical', 'Medical Certificate'),
        ('background', 'Background Check'),
        ('training', 'Training Certificate'),
        ('other', 'Other'),
    ]
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='driver_documents/')
    issue_date = models.DateField()
    expiry_date = models.DateField()
    notes = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Driver Document"
        verbose_name_plural = "Driver Documents"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.driver.full_name} - {self.title}"
    
    @property
    def is_expired(self):
        return self.expiry_date <= timezone.now().date()
    
    @property
    def expires_soon(self):
        from datetime import timedelta
        return self.expiry_date <= timezone.now().date() + timedelta(days=30)


class DriverAttendance(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('present', 'Present'),
            ('absent', 'Absent'),
            ('late', 'Late'),
            ('half_day', 'Half Day'),
        ],
        default='present'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Driver Attendance"
        verbose_name_plural = "Driver Attendance"
        unique_together = ['driver', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.driver.full_name} - {self.date}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate hours worked if check_in and check_out are provided
        if self.check_in and self.check_out:
            from datetime import datetime, time
            check_in_datetime = datetime.combine(self.date, self.check_in)
            check_out_datetime = datetime.combine(self.date, self.check_out)
            
            # Handle overnight shifts
            if check_out_datetime < check_in_datetime:
                from datetime import timedelta
                check_out_datetime += timedelta(days=1)
            
            diff = check_out_datetime - check_in_datetime
            self.hours_worked = Decimal(str(diff.total_seconds() / 3600))
        
        super().save(*args, **kwargs)

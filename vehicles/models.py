from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class VehicleType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Vehicle Type"
        verbose_name_plural = "Vehicle Types"
    
    def __str__(self):
        return self.name


class Vehicle(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('on_trip', 'On Trip'),
        ('in_shop', 'In Shop'),
        ('retired', 'Retired'),
    ]
    
    FUEL_TYPE_CHOICES = [
        ('diesel', 'Diesel'),
        ('petrol', 'Petrol'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('cng', 'CNG'),
        ('lpg', 'LPG'),
    ]
    
    TRANSMISSION_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
        ('cvt', 'CVT'),
        ('semi_automatic', 'Semi-Automatic'),
    ]
    
    name = models.CharField(max_length=100)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True, blank=True)
    make = models.CharField(max_length=100, blank=True, null=True, help_text="Vehicle manufacturer (e.g., Toyota, Ford, Mercedes)")
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField(null=True, blank=True, help_text="Manufacturing year")
    color = models.CharField(max_length=50, blank=True, null=True, help_text="Vehicle color")
    license_plate = models.CharField(max_length=20, unique=True)
    vin = models.CharField(max_length=17, unique=True, blank=True, null=True)
    
    # Engine and Performance
    engine_type = models.CharField(max_length=100, blank=True, help_text="Engine specifications (e.g., 2.5L Turbo Diesel)")
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, default='diesel')
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='manual')
    fuel_efficiency = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Fuel efficiency in km/l")
    
    # Capacity and Dimensions
    capacity = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Load capacity in kg"
    )
    odometer = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Current odometer reading in km"
    )
    fuel_capacity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Fuel tank capacity in liters"
    )
    
    # Financial Information
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Current market value")
    
    # Regulatory and Compliance
    insurance_expiry = models.DateField(null=True, blank=True)
    registration_expiry = models.DateField(null=True, blank=True)
    last_service_date = models.DateField(null=True, blank=True)
    next_service_due = models.DateField(null=True, blank=True)
    
    # Additional Information
    chassis_number = models.CharField(max_length=30, blank=True, null=True, help_text="Vehicle chassis number")
    engine_number = models.CharField(max_length=30, blank=True, null=True, help_text="Engine serial number")
    
    # Additional Real-World Fields
    body_type = models.CharField(max_length=50, blank=True, help_text="Body type (e.g., Box Truck, Flatbed, Tanker)")
    interior_color = models.CharField(max_length=50, blank=True, help_text="Interior color")
    wheelbase = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Wheelbase in cm")
    gross_vehicle_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="GVW in kg")
    curb_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Curb weight in kg")
    number_of_doors = models.PositiveIntegerField(null=True, blank=True, help_text="Number of doors")
    number_of_seats = models.PositiveIntegerField(null=True, blank=True, help_text="Number of seats")
    drive_type = models.CharField(max_length=20, choices=[
        ('2wd', '2WD'),
        ('4wd', '4WD'),
        ('awd', 'AWD'),
    ], blank=True, help_text="Drive type")
    
    # Warranty and Service
    warranty_expiry = models.DateField(null=True, blank=True, help_text="Warranty expiry date")
    road_tax_expiry = models.DateField(null=True, blank=True, help_text="Road tax expiry date")
    fitness_expiry = models.DateField(null=True, blank=True, help_text="Fitness certificate expiry date")
    pollution_expiry = models.DateField(null=True, blank=True, help_text="Pollution certificate expiry date")
    
    # Location and Assignment
    current_location = models.CharField(max_length=200, blank=True, help_text="Current location of vehicle")
    assigned_driver = models.ForeignKey('drivers.Driver', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_vehicles')
    
    # Financial Details
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Loan amount if financed")
    loan_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Loan interest rate %")
    loan_tenure_months = models.PositiveIntegerField(null=True, blank=True, help_text="Loan tenure in months")
    monthly_emi = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Monthly EMI amount")
    
    notes = models.TextField(blank=True, help_text="Additional notes about the vehicle")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.license_plate})"
    
    def save(self, *args, **kwargs):
        # Auto-calculate next service due (every 10,000 km)
        if self.last_service_date and not self.next_service_due:
            # This is a simplified calculation - in production, you'd track actual usage
            from datetime import timedelta
            self.next_service_due = self.last_service_date + timedelta(days=90)
        super().save(*args, **kwargs)
    
    @property
    def is_available(self):
        return self.status == 'available' and self.is_active
    
    @property
    def needs_service(self):
        if self.next_service_due:
            return self.next_service_due <= timezone.now().date()
        return False
    
    @property
    def insurance_expired(self):
        if self.insurance_expiry:
            return self.insurance_expiry <= timezone.now().date()
        return False
    
    @property
    def registration_expired(self):
        if self.registration_expiry:
            return self.registration_expiry <= timezone.now().date()
        return False


class VehicleDocument(models.Model):
    DOCUMENT_TYPES = [
        ('registration', 'Registration'),
        ('insurance', 'Insurance'),
        ('inspection', 'Inspection'),
        ('permit', 'Permit'),
        ('other', 'Other'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='vehicle_documents/')
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Vehicle Document"
        verbose_name_plural = "Vehicle Documents"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.vehicle.name} - {self.title}"
    
    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date <= timezone.now().date()
        return False
    
    @property
    def is_expiring_soon(self):
        if self.expiry_date:
            from datetime import timedelta
            return self.expiry_date <= timezone.now().date() + timedelta(days=30)
        return False

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal


class FuelStation(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='USA')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Fuel Station"
        verbose_name_plural = "Fuel Stations"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.city}, {self.state}"


class FuelLog(models.Model):
    FUEL_TYPES = [
        ('diesel', 'Diesel'),
        ('gasoline', 'Gasoline'),
        ('propane', 'Propane'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    ]
    
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.CASCADE, related_name='fuel_logs')
    trip = models.ForeignKey('trips.Trip', on_delete=models.CASCADE, null=True, blank=True, related_name='fuel_expenses')
    fuel_station = models.ForeignKey(FuelStation, on_delete=models.SET_NULL, null=True, blank=True)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPES, default='diesel')
    fuel_liters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Fuel quantity in liters"
    )
    cost_per_liter = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        help_text="Cost per liter"
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    odometer_reading = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Odometer reading at fueling"
    )
    previous_odometer = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Previous odometer reading"
    )
    distance_traveled = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Distance traveled since last fueling"
    )
    fuel_efficiency = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Fuel efficiency in km/l"
    )
    fuel_date = models.DateTimeField(default=timezone.now)
    driver = models.ForeignKey('drivers.Driver', on_delete=models.SET_NULL, null=True, blank=True, related_name='fuel_logs')
    receipt = models.FileField(upload_to='fuel_receipts/', blank=True, null=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='created_fuel_logs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Fuel Log"
        verbose_name_plural = "Fuel Logs"
        ordering = ['-fuel_date']
    
    def __str__(self):
        return f"{self.vehicle.name} - {self.fuel_liters}L - ${self.total_cost}"
    
    def save(self, *args, **kwargs):
        # Calculate total cost if not provided
        if self.fuel_liters and self.cost_per_liter and not self.total_cost:
            self.total_cost = self.fuel_liters * self.cost_per_liter
        
        # Calculate distance and efficiency if odometer is provided
        if self.odometer_reading:
            # Get previous fuel log for this vehicle
            previous_log = FuelLog.objects.filter(
                vehicle=self.vehicle,
                fuel_date__lt=self.fuel_date
            ).order_by('-fuel_date').first()
            
            if previous_log:
                self.previous_odometer = previous_log.odometer_reading
                self.distance_traveled = self.odometer_reading - previous_log.odometer_reading
                
                # Calculate fuel efficiency
                if self.distance_traveled > 0 and self.fuel_liters > 0:
                    self.fuel_efficiency = self.distance_traveled / self.fuel_liters
        
        super().save(*args, **kwargs)


class Expense(models.Model):
    EXPENSE_TYPES = [
        ('fuel', 'Fuel'),
        ('maintenance', 'Maintenance'),
        ('insurance', 'Insurance'),
        ('registration', 'Registration'),
        ('toll', 'Toll'),
        ('parking', 'Parking'),
        ('fine', 'Fine/Violation'),
        ('repair', 'Repair'),
        ('tire', 'Tire'),
        ('oil_change', 'Oil Change'),
        ('car_wash', 'Car Wash'),
        ('salary', 'Driver Salary'),
        ('bonus', 'Bonus'),
        ('training', 'Training'),
        ('office', 'Office Supplies'),
        ('software', 'Software'),
        ('other', 'Other'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('mobile_payment', 'Mobile Payment'),
        ('fleet_card', 'Fleet Card'),
    ]
    
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.CASCADE, related_name='expenses', null=True, blank=True)
    driver = models.ForeignKey('drivers.Driver', on_delete=models.CASCADE, related_name='expenses', null=True, blank=True)
    trip = models.ForeignKey('trips.Trip', on_delete=models.CASCADE, related_name='expenses', null=True, blank=True)
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='credit_card')
    expense_date = models.DateField()
    receipt = models.FileField(upload_to='expense_receipts/', blank=True, null=True)
    vendor = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    is_reimbursable = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenses')
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='created_expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"
        ordering = ['-expense_date']
    
    def __str__(self):
        return f"{self.expense_type} - {self.description} - ${self.amount}"


class FuelBudget(models.Model):
    PERIOD_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.CASCADE, related_name='fuel_budgets', null=True, blank=True)
    driver = models.ForeignKey('drivers.Driver', on_delete=models.CASCADE, related_name='fuel_budgets', null=True, blank=True)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    budget_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    actual_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='created_budgets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Fuel Budget"
        verbose_name_plural = "Fuel Budgets"
        ordering = ['-start_date']
        unique_together = ['vehicle', 'period', 'start_date']
    
    def __str__(self):
        target = self.vehicle.name if self.vehicle else self.driver.full_name if self.driver else 'Fleet'
        return f"{target} - {self.period} Budget"
    
    @property
    def remaining_budget(self):
        return self.budget_amount - self.actual_spent
    
    @property
    def budget_utilization(self):
        if self.budget_amount > 0:
            return (self.actual_spent / self.budget_amount) * 100
        return 0
    
    def update_actual_spent(self):
        """Update actual spent based on fuel logs within the period"""
        from django.db.models import Sum
        
        filters = {
            'fuel_date__date__gte': self.start_date,
            'fuel_date__date__lte': self.end_date,
        }
        
        if self.vehicle:
            filters['vehicle'] = self.vehicle
        elif self.driver:
            filters['driver'] = self.driver
        
        total = FuelLog.objects.filter(**filters).aggregate(
            total=Sum('total_cost')
        )['total'] or 0
        
        self.actual_spent = total
        self.save()

from django.contrib import admin
from .models import FuelStation, FuelLog, Expense, FuelBudget


@admin.register(FuelStation)
class FuelStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'is_active', 'created_at')
    list_filter = ('is_active', 'state', 'created_at')
    search_fields = ('name', 'city', 'state', 'address')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(FuelLog)
class FuelLogAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'fuel_date', 'fuel_liters', 'total_cost', 'fuel_efficiency', 'fuel_station', 'driver', 'created_at')
    list_filter = ('fuel_type', 'fuel_date', 'fuel_station', 'created_at')
    search_fields = ('vehicle__name', 'vehicle__license_plate', 'driver__first_name', 'driver__last_name', 'fuel_station__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('vehicle', 'trip', 'fuel_station', 'fuel_type', 'fuel_date')
        }),
        ('Fuel Details', {
            'fields': ('fuel_liters', 'cost_per_liter', 'total_cost')
        }),
        ('Odometer & Efficiency', {
            'fields': ('odometer_reading', 'previous_odometer', 'distance_traveled', 'fuel_efficiency')
        }),
        ('Additional Information', {
            'fields': ('driver', 'receipt', 'notes')
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('expense_type', 'description', 'amount', 'expense_date', 'payment_method', 'vehicle', 'driver', 'is_approved', 'created_at')
    list_filter = ('expense_type', 'payment_method', 'expense_date', 'is_approved', 'created_at')
    search_fields = ('description', 'vendor', 'vehicle__name', 'driver__first_name', 'driver__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('expense_type', 'description', 'amount', 'expense_date')
        }),
        ('Assignment', {
            'fields': ('vehicle', 'driver', 'trip')
        }),
        ('Payment', {
            'fields': ('payment_method', 'vendor', 'receipt')
        }),
        ('Additional Information', {
            'fields': ('category', 'notes', 'is_reimbursable')
        }),
        ('Approval', {
            'fields': ('is_approved', 'approved_by')
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FuelBudget)
class FuelBudgetAdmin(admin.ModelAdmin):
    list_display = ('get_target', 'period', 'start_date', 'end_date', 'budget_amount', 'actual_spent', 'remaining_budget', 'budget_utilization', 'is_active', 'created_at')
    list_filter = ('period', 'start_date', 'end_date', 'is_active', 'created_at')
    search_fields = ('vehicle__name', 'driver__first_name', 'driver__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_target(self, obj):
        if obj.vehicle:
            return obj.vehicle.name
        elif obj.driver:
            return obj.driver.full_name
        return 'Fleet'
    get_target.short_description = 'Target'
    
    def budget_utilization(self, obj):
        return f"{obj.budget_utilization:.2f}%"
    budget_utilization.short_description = 'Utilization %'
    
    fieldsets = (
        ('Budget Information', {
            'fields': ('vehicle', 'driver', 'period', 'start_date', 'end_date')
        }),
        ('Amounts', {
            'fields': ('budget_amount', 'actual_spent')
        }),
        ('Additional Information', {
            'fields': ('notes', 'is_active')
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

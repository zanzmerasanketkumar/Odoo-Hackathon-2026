from django.contrib import admin
from .models import Vehicle, VehicleType, VehicleDocument


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'license_plate', 'model', 'vehicle_type', 'status', 'capacity', 'is_active', 'created_at')
    list_filter = ('status', 'is_active', 'vehicle_type', 'created_at')
    search_fields = ('name', 'license_plate', 'model', 'vin')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'vehicle_type', 'model', 'license_plate', 'vin')
        }),
        ('Capacity & Performance', {
            'fields': ('capacity', 'odometer', 'fuel_capacity')
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
        ('Purchase Information', {
            'fields': ('purchase_date', 'purchase_cost')
        }),
        ('Important Dates', {
            'fields': ('insurance_expiry', 'registration_expiry', 'last_service_date', 'next_service_due')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return self.readonly_fields + ('created_at', 'updated_at')


@admin.register(VehicleDocument)
class VehicleDocumentAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'title', 'document_type', 'expiry_date', 'is_expired', 'created_at')
    list_filter = ('document_type', 'expiry_date', 'created_at')
    search_fields = ('vehicle__name', 'vehicle__license_plate', 'title')
    readonly_fields = ('created_at', 'updated_at')
    
    def is_expired(self, obj):
        if obj.expiry_date:
            from django.utils import timezone
            return obj.expiry_date <= timezone.now().date()
        return False
    is_expired.boolean = True
    is_expired.short_description = 'Expired'

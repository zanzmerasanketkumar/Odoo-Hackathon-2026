from django.contrib import admin
from .models import Driver, DriverPerformance, DriverDocument, DriverAttendance


class DriverPerformanceInline(admin.TabularInline):
    model = DriverPerformance
    can_delete = False
    readonly_fields = ('created_at', 'updated_at')


class DriverDocumentInline(admin.TabularInline):
    model = DriverDocument
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'license_number', 'status', 'is_active', 'license_expiry', 'created_at')
    list_filter = ('status', 'is_active', 'license_expiry', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'license_number')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [DriverDocumentInline]
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'date_of_birth')
        }),
        ('Employment Information', {
            'fields': ('hire_date', 'status', 'salary', 'is_active')
        }),
        ('License Information', {
            'fields': ('license_number', 'license_type', 'license_expiry')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact', 'emergency_phone')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'


@admin.register(DriverPerformance)
class DriverPerformanceAdmin(admin.ModelAdmin):
    list_display = ('driver', 'total_trips', 'completed_trips', 'completion_rate', 'safety_score', 'fuel_efficiency', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('driver__first_name', 'driver__last_name', 'driver__email')
    readonly_fields = ('created_at', 'updated_at')
    
    def completion_rate(self, obj):
        return f"{obj.completion_rate:.2f}%"
    completion_rate.short_description = 'Completion Rate'
    
    def fuel_efficiency(self, obj):
        return f"{obj.fuel_efficiency:.2f} km/l"
    fuel_efficiency.short_description = 'Fuel Efficiency'


@admin.register(DriverDocument)
class DriverDocumentAdmin(admin.ModelAdmin):
    list_display = ('driver', 'title', 'document_type', 'issue_date', 'expiry_date', 'is_expired', 'is_verified', 'created_at')
    list_filter = ('document_type', 'expiry_date', 'is_verified', 'created_at')
    search_fields = ('driver__first_name', 'driver__last_name', 'title')
    readonly_fields = ('created_at', 'updated_at')
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(DriverAttendance)
class DriverAttendanceAdmin(admin.ModelAdmin):
    list_display = ('driver', 'date', 'check_in', 'check_out', 'hours_worked', 'status', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('driver__first_name', 'driver__last_name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'

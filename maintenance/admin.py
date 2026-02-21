from django.contrib import admin
from .models import MaintenanceType, MaintenanceSchedule, MaintenancePart, MaintenanceDocument, MaintenanceReminder


class MaintenancePartInline(admin.TabularInline):
    model = MaintenancePart
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


class MaintenanceDocumentInline(admin.TabularInline):
    model = MaintenanceDocument
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MaintenanceType)
class MaintenanceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'estimated_duration_hours', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'title', 'maintenance_type', 'status', 'priority', 'scheduled_date', 'created_at')
    list_filter = ('status', 'priority', 'scheduled_date', 'created_at')
    search_fields = ('vehicle__name', 'title', 'maintenance_type__name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MaintenancePartInline, MaintenanceDocumentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('vehicle', 'maintenance_type', 'title', 'description')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Schedule', {
            'fields': ('scheduled_date', 'estimated_duration_hours')
        }),
        ('Cost', {
            'fields': ('estimated_cost', 'actual_cost')
        }),
        ('Details', {
            'fields': ('odometer_reading', 'performed_by', 'notes', 'completion_notes')
        }),
        ('System Information', {
            'fields': ('created_by', 'completed_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MaintenancePart)
class MaintenancePartAdmin(admin.ModelAdmin):
    list_display = ('maintenance_schedule', 'part_name', 'quantity', 'unit_cost', 'total_cost', 'supplier', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('maintenance_schedule__title', 'part_name', 'part_number', 'supplier')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MaintenanceDocument)
class MaintenanceDocumentAdmin(admin.ModelAdmin):
    list_display = ('maintenance_schedule', 'title', 'document_type', 'created_at')
    list_filter = ('document_type', 'created_at')
    search_fields = ('maintenance_schedule__title', 'title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MaintenanceReminder)
class MaintenanceReminderAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'reminder_type', 'is_active', 'is_sent', 'trigger_date', 'trigger_odometer', 'created_at')
    list_filter = ('is_active', 'is_sent', 'trigger_date', 'created_at')
    search_fields = ('vehicle__name', 'reminder_type', 'description')
    readonly_fields = ('created_at', 'updated_at', 'sent_date')

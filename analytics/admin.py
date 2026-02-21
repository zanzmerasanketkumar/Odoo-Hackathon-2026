from django.contrib import admin
from .models import DashboardKPI, Report, Alert, SystemMetric, Notification


@admin.register(DashboardKPI)
class DashboardKPIAdmin(admin.ModelAdmin):
    list_display = ('kpi_type', 'value', 'unit', 'trend', 'last_updated')
    list_filter = ('kpi_type', 'last_updated')
    search_fields = ('kpi_type',)
    readonly_fields = ('last_updated',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'period', 'start_date', 'end_date', 'file_format', 'is_generated', 'generated_at', 'created_at')
    list_filter = ('report_type', 'period', 'file_format', 'is_generated', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'generated_at')
    
    fieldsets = (
        ('Report Information', {
            'fields': ('report_type', 'title', 'description', 'period')
        }),
        ('Date Range', {
            'fields': ('start_date', 'end_date')
        }),
        ('Generation', {
            'fields': ('file_format', 'is_generated', 'generated_by', 'generated_at', 'file_path')
        }),
        ('Configuration', {
            'fields': ('parameters', 'data')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'alert_type', 'severity', 'status', 'vehicle', 'driver', 'action_required', 'is_overdue', 'created_at')
    list_filter = ('alert_type', 'severity', 'status', 'action_required', 'created_at')
    search_fields = ('title', 'message', 'vehicle__name', 'driver__first_name', 'driver__last_name')
    readonly_fields = ('created_at', 'updated_at', 'acknowledged_at', 'resolved_at')
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('alert_type', 'title', 'message', 'severity', 'status')
        }),
        ('Assignment', {
            'fields': ('vehicle', 'driver', 'trip')
        }),
        ('Action Required', {
            'fields': ('action_required', 'action_taken', 'due_date')
        }),
        ('Resolution', {
            'fields': ('acknowledged_by', 'acknowledged_at', 'resolved_by', 'resolved_at')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SystemMetric)
class SystemMetricAdmin(admin.ModelAdmin):
    list_display = ('metric_type', 'value', 'unit', 'date', 'vehicle', 'driver', 'created_at')
    list_filter = ('metric_type', 'date', 'created_at')
    search_fields = ('metric_type', 'vehicle__name', 'driver__first_name', 'driver__last_name')
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'title', 'notification_type', 'is_read', 'created_at', 'read_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
    readonly_fields = ('created_at', 'read_at')
    
    fieldsets = (
        ('Notification', {
            'fields': ('recipient', 'title', 'message', 'notification_type')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'action_url')
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

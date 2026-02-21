from django.contrib import admin
from .models import Trip, TripExpense, TripCheckpoint, TripDocument


class TripExpenseInline(admin.TabularInline):
    model = TripExpense
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


class TripCheckpointInline(admin.TabularInline):
    model = TripCheckpoint
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


class TripDocumentInline(admin.TabularInline):
    model = TripDocument
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('trip_number', 'origin', 'destination', 'driver', 'vehicle', 'status', 'priority', 'start_date', 'created_at')
    list_filter = ('status', 'priority', 'start_date', 'created_at')
    search_fields = ('trip_number', 'origin', 'destination', 'driver__first_name', 'driver__last_name', 'vehicle__name', 'vehicle__license_plate')
    readonly_fields = ('trip_number', 'created_at', 'updated_at')
    inlines = [TripExpenseInline, TripCheckpointInline, TripDocumentInline]
    
    fieldsets = (
        ('Trip Information', {
            'fields': ('trip_number', 'origin', 'destination', 'priority', 'status')
        }),
        ('Assignment', {
            'fields': ('driver', 'vehicle', 'cargo_weight', 'cargo_description')
        }),
        ('Estimates', {
            'fields': ('estimated_distance', 'estimated_duration')
        }),
        ('Actuals', {
            'fields': ('actual_distance', 'actual_duration')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'actual_start_time', 'actual_end_time')
        }),
        ('Additional Information', {
            'fields': ('notes', 'cancellation_reason')
        }),
        ('System Information', {
            'fields': ('created_by', 'dispatched_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TripExpense)
class TripExpenseAdmin(admin.ModelAdmin):
    list_display = ('trip', 'expense_type', 'description', 'amount', 'date', 'created_at')
    list_filter = ('expense_type', 'date', 'created_at')
    search_fields = ('trip__trip_number', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TripCheckpoint)
class TripCheckpointAdmin(admin.ModelAdmin):
    list_display = ('trip', 'location', 'arrival_time', 'departure_time', 'is_completed', 'created_at')
    list_filter = ('is_completed', 'arrival_time', 'created_at')
    search_fields = ('trip__trip_number', 'location')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TripDocument)
class TripDocumentAdmin(admin.ModelAdmin):
    list_display = ('trip', 'title', 'document_type', 'created_at')
    list_filter = ('document_type', 'created_at')
    search_fields = ('trip__trip_number', 'title')
    readonly_fields = ('created_at', 'updated_at')

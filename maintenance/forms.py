from django import forms
from .models import MaintenanceSchedule, MaintenancePart, MaintenanceDocument, MaintenanceReminder


class MaintenanceScheduleForm(forms.ModelForm):
    class Meta:
        model = MaintenanceSchedule
        fields = [
            'vehicle', 'maintenance_type', 'title', 'description', 'priority',
            'scheduled_date', 'estimated_duration_hours', 'estimated_cost',
            'odometer_reading', 'performed_by', 'notes'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'estimated_duration_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'estimated_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'odometer_reading': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'performed_by': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MaintenancePartForm(forms.ModelForm):
    class Meta:
        model = MaintenancePart
        fields = ['part_name', 'part_number', 'quantity', 'unit_cost', 'supplier', 'notes']
        widgets = {
            'part_name': forms.TextInput(attrs={'class': 'form-control'}),
            'part_number': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class MaintenanceDocumentForm(forms.ModelForm):
    class Meta:
        model = MaintenanceDocument
        fields = ['document_type', 'title', 'file', 'notes']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class MaintenanceReminderForm(forms.ModelForm):
    class Meta:
        model = MaintenanceReminder
        fields = ['vehicle', 'reminder_type', 'description', 'trigger_odometer', 'trigger_date']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'reminder_type': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'trigger_odometer': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'trigger_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class MaintenanceFilterForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search maintenance...'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + MaintenanceSchedule.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + MaintenanceSchedule.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

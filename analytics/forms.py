from django import forms
from .models import Report, Alert


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = [
            'report_type', 'title', 'description', 'period', 'start_date',
            'end_date', 'file_format'
        ]
        widgets = {
            'report_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'period': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'file_format': forms.Select(attrs={'class': 'form-select'}),
        }


class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = [
            'alert_type', 'title', 'message', 'severity', 'vehicle',
            'driver', 'trip', 'action_required', 'due_date'
        ]
        widgets = {
            'alert_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'trip': forms.Select(attrs={'class': 'form-select'}),
            'action_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter active vehicles, drivers, and trips
        from vehicles.models import Vehicle
        from drivers.models import Driver
        from trips.models import Trip
        
        self.fields['vehicle'].queryset = Vehicle.objects.filter(is_active=True)
        self.fields['driver'].queryset = Driver.objects.filter(is_active=True)
        self.fields['trip'].queryset = Trip.objects.all()


class ReportFilterForm(forms.Form):
    report_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Report.REPORT_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    period = forms.ChoiceField(
        choices=[('', 'All Periods')] + Report.PERIOD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    is_generated = forms.ChoiceField(
        choices=[('', 'All'), ('true', 'Generated'), ('false', 'Not Generated')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class AlertFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Alert.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    severity = forms.ChoiceField(
        choices=[('', 'All Severities')] + Alert.SEVERITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    alert_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Alert.ALERT_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

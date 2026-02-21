from django import forms
from django.core.validators import MinValueValidator
from django.utils import timezone
from .models import Trip, TripExpense, TripCheckpoint, TripDocument


class TripForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter available vehicles and drivers
        from vehicles.models import Vehicle
        from drivers.models import Driver
        
        self.fields['vehicle'].queryset = Vehicle.objects.filter(
            status='available',
            is_active=True
        )
        
        self.fields['driver'].queryset = Driver.objects.filter(
            status='on_duty',
            is_active=True
        ).exclude(license_expiry__lte=timezone.now().date())
    
    class Meta:
        model = Trip
        fields = [
            'origin', 'destination', 'driver', 'vehicle', 'cargo_weight',
            'cargo_description', 'estimated_distance', 'estimated_duration',
            'priority', 'start_date', 'end_date', 'notes'
        ]
        widgets = {
            'origin': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'cargo_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cargo_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estimated_distance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estimated_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        vehicle = cleaned_data.get('vehicle')
        cargo_weight = cleaned_data.get('cargo_weight')
        
        if vehicle and cargo_weight:
            if float(cargo_weight) > float(vehicle.capacity):
                raise forms.ValidationError(
                    f'Cargo weight ({cargo_weight} kg) exceeds vehicle capacity ({vehicle.capacity} kg)'
                )
        
        return cleaned_data


class TripExpenseForm(forms.ModelForm):
    class Meta:
        model = TripExpense
        fields = ['expense_type', 'description', 'amount', 'receipt', 'date', 'notes']
        widgets = {
            'expense_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'receipt': forms.FileInput(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class TripCheckpointForm(forms.ModelForm):
    class Meta:
        model = TripCheckpoint
        fields = ['location', 'latitude', 'longitude', 'arrival_time', 'departure_time', 'notes']
        widgets = {
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'arrival_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'departure_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class TripDocumentForm(forms.ModelForm):
    class Meta:
        model = TripDocument
        fields = ['document_type', 'title', 'file', 'notes']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class TripFilterForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search trips...'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Trip.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + Trip.PRIORITY_CHOICES,
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

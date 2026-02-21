from django import forms
from .models import Vehicle, VehicleType, VehicleDocument


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'name', 'vehicle_type', 'make', 'model', 'year', 'color', 'interior_color',
            'license_plate', 'vin', 'engine_type', 'fuel_type', 'transmission', 'drive_type',
            'fuel_efficiency', 'body_type', 'wheelbase', 'gross_vehicle_weight', 'curb_weight',
            'number_of_doors', 'number_of_seats', 'capacity', 'odometer', 'fuel_capacity', 'status',
            'purchase_date', 'purchase_cost', 'current_value', 'loan_amount', 'loan_interest_rate',
            'loan_tenure_months', 'monthly_emi', 'insurance_expiry', 'registration_expiry',
            'warranty_expiry', 'road_tax_expiry', 'fitness_expiry', 'pollution_expiry',
            'last_service_date', 'next_service_due', 'current_location', 'assigned_driver',
            'chassis_number', 'engine_number', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'make': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Toyota, Ford, Mercedes'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1900', 'max': '2100'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., White, Black, Red'}),
            'interior_color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Gray, Beige, Black'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control'}),
            'vin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '17-character VIN'}),
            'engine_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2.5L Turbo Diesel'}),
            'fuel_type': forms.Select(attrs={'class': 'form-select'}),
            'transmission': forms.Select(attrs={'class': 'form-select'}),
            'drive_type': forms.Select(attrs={'class': 'form-select'}),
            'fuel_efficiency': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'km/l'}),
            'body_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Box Truck, Flatbed, Tanker'}),
            'wheelbase': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'cm'}),
            'gross_vehicle_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'kg'}),
            'curb_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'kg'}),
            'number_of_doors': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'number_of_seats': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'odometer': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fuel_capacity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '$'}),
            'current_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '$'}),
            'loan_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '$'}),
            'loan_interest_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '%'}),
            'loan_tenure_months': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'months'}),
            'monthly_emi': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '$'}),
            'insurance_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'registration_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'road_tax_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fitness_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pollution_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'last_service_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_service_due': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'current_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Current location of vehicle'}),
            'assigned_driver': forms.Select(attrs={'class': 'form-select'}),
            'chassis_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vehicle chassis number'}),
            'engine_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Engine serial number'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes about the vehicle...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle_type'].queryset = VehicleType.objects.all()
        self.fields['vehicle_type'].empty_label = "Select Vehicle Type"
        
        # Set up driver field
        from drivers.models import Driver
        self.fields['assigned_driver'].queryset = Driver.objects.filter(is_active=True)
        self.fields['assigned_driver'].empty_label = "Select Driver (Optional)"


class VehicleDocumentForm(forms.ModelForm):
    class Meta:
        model = VehicleDocument
        fields = ['document_type', 'title', 'file', 'expiry_date', 'notes']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class VehicleFilterForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search vehicles...'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Vehicle.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    vehicle_type = forms.ModelChoiceField(
        queryset=VehicleType.objects.all(),
        required=False,
        empty_label="All Types",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

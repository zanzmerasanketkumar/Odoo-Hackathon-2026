from django import forms
from .models import FuelLog, Expense, FuelBudget, FuelStation


class FuelLogForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter active vehicles and drivers
        from vehicles.models import Vehicle
        from drivers.models import Driver
        
        self.fields['vehicle'].queryset = Vehicle.objects.filter(is_active=True)
        self.fields['driver'].queryset = Driver.objects.filter(is_active=True)
        self.fields['fuel_station'].queryset = FuelStation.objects.filter(is_active=True)
    
    class Meta:
        model = FuelLog
        fields = [
            'vehicle', 'trip', 'fuel_station', 'fuel_type', 'fuel_liters',
            'cost_per_liter', 'total_cost', 'odometer_reading', 'fuel_date',
            'driver', 'receipt', 'notes'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'trip': forms.Select(attrs={'class': 'form-select'}),
            'fuel_station': forms.Select(attrs={'class': 'form-select'}),
            'fuel_type': forms.Select(attrs={'class': 'form-select'}),
            'fuel_liters': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cost_per_liter': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'total_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'odometer_reading': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fuel_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'receipt': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ExpenseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter active vehicles and drivers
        from vehicles.models import Vehicle
        from drivers.models import Driver
        
        self.fields['vehicle'].queryset = Vehicle.objects.filter(is_active=True)
        self.fields['driver'].queryset = Driver.objects.filter(is_active=True)
    
    class Meta:
        model = Expense
        fields = [
            'vehicle', 'driver', 'trip', 'expense_type', 'description',
            'amount', 'payment_method', 'expense_date', 'receipt',
            'vendor', 'category', 'notes', 'is_reimbursable'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'trip': forms.Select(attrs={'class': 'form-select'}),
            'expense_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'receipt': forms.FileInput(attrs={'class': 'form-control'}),
            'vendor': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_reimbursable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FuelBudgetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter active vehicles and drivers
        from vehicles.models import Vehicle
        from drivers.models import Driver
        
        self.fields['vehicle'].queryset = Vehicle.objects.filter(is_active=True)
        self.fields['driver'].queryset = Driver.objects.filter(is_active=True)
    
    class Meta:
        model = FuelBudget
        fields = [
            'vehicle', 'driver', 'period', 'start_date', 'end_date',
            'budget_amount', 'notes', 'is_active'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'period': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'budget_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FuelStationForm(forms.ModelForm):
    class Meta:
        model = FuelStation
        fields = [
            'name', 'address', 'city', 'state', 'postal_code',
            'country', 'latitude', 'longitude', 'phone', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FuelLogFilterForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search fuel logs...'
        })
    )
    vehicle = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Vehicles",
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from vehicles.models import Vehicle
        self.fields['vehicle'].queryset = Vehicle.objects.filter(is_active=True)


class ExpenseFilterForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search expenses...'
        })
    )
    expense_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Expense.EXPENSE_TYPES,
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

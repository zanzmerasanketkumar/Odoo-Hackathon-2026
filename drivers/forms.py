from django import forms
from django.core.validators import RegexValidator
from .models import Driver, DriverDocument, DriverAttendance


class DriverForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    emergency_phone = forms.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Driver
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'address', 'date_of_birth',
            'hire_date', 'license_number', 'license_type', 'license_expiry',
            'status', 'emergency_contact', 'emergency_phone', 'salary', 'profile_picture'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'license_type': forms.TextInput(attrs={'class': 'form-control'}),
            'license_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DriverDocumentForm(forms.ModelForm):
    class Meta:
        model = DriverDocument
        fields = ['document_type', 'title', 'file', 'issue_date', 'expiry_date', 'notes']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DriverAttendanceForm(forms.ModelForm):
    class Meta:
        model = DriverAttendance
        fields = ['date', 'check_in', 'check_out', 'status', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'check_in': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'check_out': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class DriverFilterForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search drivers...'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Driver.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    license_filter = forms.ChoiceField(
        choices=[
            ('', 'All Licenses'),
            ('expired', 'Expired Licenses'),
            ('expiring_soon', 'Expiring Soon (30 days)'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

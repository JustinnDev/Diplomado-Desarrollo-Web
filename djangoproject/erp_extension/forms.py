from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import (
    Driver, Vehicle, FuelStation,
    FuelRefill, FuelConsumption, MaintenanceLog
)
from django.core.validators import MinValueValidator

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['name', 'license_number', 'license_type', 'phone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'license_type': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_active': 'Activo'
        }

    def clean_license_number(self):
        license_number = self.cleaned_data['license_number']
        if Driver.objects.filter(license_number=license_number).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este número de licencia ya está registrado')
        return license_number

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'license_plate', 'make', 'model', 'year',
            'vehicle_type', 'fuel_type', 'fuel_capacity',
            'current_driver', 'is_active'
        ]
        widgets = {
            'license_plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ABC-123'}),
            'make': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-control'}),
            'fuel_type': forms.Select(attrs={'class': 'form-control'}),
            'fuel_capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'current_driver': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_active': 'Activo'
        }

    def clean_license_plate(self):
        license_plate = self.cleaned_data['license_plate'].upper()
        if Vehicle.objects.filter(license_plate=license_plate).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Esta placa ya está registrada')
        return license_plate

    def clean_year(self):
        year = self.cleaned_data['year']
        current_year = timezone.now().year
        if year < 1900 or year > current_year + 1:
            raise ValidationError(f'El año debe estar entre 1900 y {current_year + 1}')
        return year

class FuelStationForm(forms.ModelForm):
    class Meta:
        model = FuelStation
        fields = ['name', 'location', 'contact_phone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_active': 'Activo'
        }

class FuelRefillForm(forms.ModelForm):
    class Meta:
        model = FuelRefill
        fields = [
            'vehicle', 'driver', 'station', 'date',
            'quantity', 'price_per_unit', 'odometer_reading', 'notes'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
            'driver': forms.Select(attrs={'class': 'form-control'}),
            'station': forms.Select(attrs={'class': 'form-control'}),
 
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'price_per_unit': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'odometer_reading': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = timezone.now()

class FuelConsumptionForm(forms.ModelForm):
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            },
            format='%Y-%m-%dT%H:%M'
        ),
        initial=timezone.now
    )

    class Meta:
        model = FuelConsumption
        fields = [
            'vehicle', 'driver',
            'quantity', 'odometer_reading', 'purpose', 'notes'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
            'driver': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'odometer_reading': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'purpose': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        vehicle = cleaned_data.get('vehicle')
        odometer_reading = cleaned_data.get('odometer_reading')
        
        if vehicle and odometer_reading:
            # Verificar que la lectura del odómetro no sea menor que la anterior
            last_record = FuelConsumption.objects.filter(
                vehicle=vehicle
            ).order_by('-date').first()
            
            if last_record and odometer_reading < last_record.odometer_reading:
                raise ValidationError({
                    'odometer_reading': f'La lectura del odómetro no puede ser menor que la última registrada ({last_record.odometer_reading})'
                })
        
        return cleaned_data

class MaintenanceLogForm(forms.ModelForm):
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            },
            format='%Y-%m-%dT%H:%M'
        ),
        initial=timezone.now
    )

    class Meta:
        model = MaintenanceLog
        fields = [
            'vehicle', 'maintenance_type',
            'description', 'cost', 'odometer_reading',
            'next_maintenance_km', 'performed_by'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'odometer_reading': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'next_maintenance_km': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'performed_by': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        vehicle = cleaned_data.get('vehicle')
        odometer_reading = cleaned_data.get('odometer_reading')
        next_maintenance_km = cleaned_data.get('next_maintenance_km')
        
        if vehicle and odometer_reading:
            # Verificar que la lectura del odómetro no sea menor que la anterior
            last_maintenance = MaintenanceLog.objects.filter(
                vehicle=vehicle
            ).order_by('-date').first()
            
            if last_maintenance and odometer_reading < last_maintenance.odometer_reading:
                raise ValidationError({
                    'odometer_reading': f'La lectura del odómetro no puede ser menor que la última registrada ({last_maintenance.odometer_reading})'
                })
        
        if next_maintenance_km and odometer_reading and next_maintenance_km <= odometer_reading:
            raise ValidationError({
                'next_maintenance_km': 'El próximo mantenimiento debe ser después del kilometraje actual'
            })
        
        return cleaned_data
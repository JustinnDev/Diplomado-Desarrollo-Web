from django import forms
from .models import MaterialType, Client, MaterialReception, ReceptionMaterial, MaterialOperation

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'identification', 'phone', 'address']
        widgets = {
            'phone': forms.TextInput(attrs={'type': 'tel'}),
        }

class MaterialTypeForm(forms.ModelForm):
    class Meta:
        model = MaterialType
        fields = ['name', 'category', 'base_price']
        widgets = {
            'base_price': forms.NumberInput(attrs={'step': '0.01'}),
        }

class MaterialOperationForm(forms.ModelForm):
    class Meta:
        model = MaterialOperation
        fields = ['gross_weight', 'tare_weight']
        widgets = {
            'gross_weight': forms.NumberInput(attrs={'step': '0.01'}),
            'tare_weight': forms.NumberInput(attrs={'step': '0.01'}),
        }
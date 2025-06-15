from django import forms
from .models import Material, Client, MaterialReception

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'identification', 'phone', 'address']
        widgets = {
            'phone': forms.TextInput(attrs={'type': 'tel'}),
        }

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'category', 'subtype', 'base_price']

class MaterialReceptionForm(forms.ModelForm):
    class Meta:
        model = MaterialReception
        fields = ['client', 'material', 'gross_weight', 'rejection_weight', 'notes']
        widgets = {
            'client': forms.Select(attrs={'class': 'select2'}),
            'material': forms.Select(attrs={'class': 'select2'}),
            'gross_weight': forms.NumberInput(attrs={'step': '0.01'}),
            'rejection_weight': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['material'].widget.attrs['onchange'] = 'updatePrice(this)'
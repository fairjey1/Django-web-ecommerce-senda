from django import forms
from .models import Pedido

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'nombre', 'apellido', 'email', 'telefono', 
            'provincia', 'ciudad', 'direccion', 'codigo_postal'
        ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Tu nombre'}),
            'apellido': forms.TextInput(attrs={'placeholder': 'Tu apellido'}),
            'email': forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Calle y número'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Incluido código de área'}),
        }
from django import forms
from .models import Pedido

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'metodo_entrega', 'metodo_pago', 'nombre', 'apellido', 'email', 'telefono', 
            'provincia', 'ciudad', 'direccion', 'codigo_postal'
        ]
        
        widgets = {
            'metodo_entrega': forms.RadioSelect(),
            'metodo_pago': forms.RadioSelect(),
            'nombre': forms.TextInput(attrs={'placeholder': 'Tu nombre'}),
            'apellido': forms.TextInput(attrs={'placeholder': 'Tu apellido'}),
            'email': forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Calle y número'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Incluido código de área'}),
        }
        
    def clean(self):
        """
        Validación personalizada: Si elige envío, obligamos a que llene la dirección.
        """
        cleaned_data = super().clean()
        metodo = cleaned_data.get('metodo_entrega')
        direccion = cleaned_data.get('direccion')
        codigo_postal = cleaned_data.get('codigo_postal')

        if metodo == 'envio':
            if not direccion:
                self.add_error('direccion', 'La dirección es obligatoria para envíos a domicilio.')
            if not codigo_postal:
                self.add_error('codigo_postal', 'El código postal es obligatorio para calcular el envío.')
                
        return cleaned_data
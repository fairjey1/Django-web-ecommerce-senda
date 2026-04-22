from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegistroMayoristaForm(UserCreationForm):

    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellido")
    email = forms.EmailField(max_length=254, required=True, label="Correo Electrónico")

    class Meta:
        model = CustomUser
        # lo que se muestra en el html
        fields = (
            'first_name',
            'last_name',
            'email',
            'telefono',
            'razon_social',
            'instagram',
            'facebook',
            'mensaje',
        )

        labels = {
            'telefono': 'Teléfono o WhatsApp',
            'razon_social': 'Razón Social o Emprendimiento (opcional)',
            'instagram': 'Instagram (opcional)',
            'facebook': 'Facebook (opcional)',
            'mensaje_registro': 'Mensaje (opcional)',
        }
        
        widgets = {
            'mensaje': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Dejanos un mensaje (opcional)...'}),
        }
        
    def save(self, commit=True): # sobrescribimos el método save para asignar el email al username 
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        
        # Guardamos finalmente el usuario
        if commit:
            user.save()
        return user
class CustomLoginForm(forms.Form):
    email = forms.EmailField(label='Correo Electrónico', max_length=254, widget=forms.EmailInput(attrs={'autofocus': True}))
    password = forms.CharField(label='Contraseña', strip=False, widget=forms.PasswordInput)
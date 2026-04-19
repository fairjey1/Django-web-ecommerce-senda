from pyexpat.errors import messages
from urllib import response

from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegistroMayoristaForm

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

class AccesoMayoristasView(CreateView):
    template_name = 'users/acceso_mayoristas.html'
    form_class = RegistroMayoristaForm
    # Cuando el registro sea exitoso, lo redirigimos a la home (o a una página de éxito futura)
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        response = super().form_valid(form) # guardamos el nuevo usuario

        # logica para mandar mail al admin

        nombre = f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}"
        correo_usuario = form.cleaned_data['email']
        mensaje = form.cleaned_data.get('mensaje', 'Sin mensaje adjunto.')

        # Creamos un contexto para pasarle variables al template del email
        context = {
            'nombre': nombre,
            'email': correo_usuario,
            'mensaje': mensaje,
        }   
        
        # Renderizamos el template del email con el contexto
        html_content = render_to_string('users/new_user_request.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=f"Solicitud de usuario mayorista: {nombre}",
            body=text_content, # Versión texto plano
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.EMAIL_RECIPIENT], # A quién le llega (al dueño)
            reply_to=[correo_usuario] 
        )

        email.attach_alternative(html_content, "text/html") 
        
        try:
            email.send()
            messages.success(self.request, "¡Gracias! Tu mensaje ha sido enviado correctamente.")
        except Exception as e:
            print(f"Error enviando correo: {e}")

        return response

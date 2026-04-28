from pyexpat.errors import messages
from urllib import response

from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomLoginForm, RegistroMayoristaForm

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from django.contrib.auth.views import LoginView, LogoutView
 
class AccesoMayoristasView(CreateView):
    template_name = 'users/acceso_mayoristas.html'
    form_class = RegistroMayoristaForm
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

# login
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('core:home')
    form_class = CustomLoginForm

    # requiere que el usuario este aprobado para poder loguearse
    def form_valid(self, form):
        user = form.get_user()
        if user.esta_aprobado:
            return super().form_valid(form)
        else:
            form.add_error(None, "Tu cuenta aún no ha sido aprobada por el administrador.")
            return self.form_invalid(form)
        
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('core:home')  # Redirige a la página de inicio después de cerrar sesión


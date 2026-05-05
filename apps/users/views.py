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
from django.contrib.auth import login
from django.contrib import messages

class AccesoMayoristasView(CreateView):
    template_name = 'users/acceso_mayoristas.html'
    form_class = RegistroMayoristaForm
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        response = super().form_valid(form) # guardamos el nuevo usuario
        login(self.request, self.object) # logueamos al nuevo usuario
        messages.success(
            self.request, 
            "¡Bienvenido a Senda! Tu cuenta ha sido creada con éxito. Ya podes iniciar sesión y acceder a los precios mayoristas."
        )

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


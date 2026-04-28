from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from .views import AccesoMayoristasView, CustomLoginView, CustomLogoutView
app_name = 'users'
urlpatterns = [
    path('acceso-mayoristas/', AccesoMayoristasView.as_view(), name='acceso_mayoristas'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    
    # --- RECUPERACIÓN DE CONTRASEÑA ---
    
    # 1. Pantalla para ingresar el email
    path('recuperar-password/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html',
        email_template_name='users/password_reset_email.html',
        success_url=reverse_lazy('users:password_reset_done')
    ), name='password_reset'),

    # 2. Pantalla de éxito (Te enviamos un correo)
    path('recuperar-password/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),

    # 3. Pantalla del link del correo (Ingresar nueva clave)
    path('recuperar-password/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
        success_url=reverse_lazy('users:password_reset_complete')
    ), name='password_reset_confirm'),

    # 4. Pantalla de éxito final
    path('recuperar-password/completo/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),
]
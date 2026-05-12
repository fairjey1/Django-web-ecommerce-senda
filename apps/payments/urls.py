from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('instrucciones/<int:pedido_id>/', views.instrucciones_transferencia, name='instrucciones'),
    path('mercadopago/<int:pedido_id>/', views.procesar_mercadopago, name='procesar_mercadopago'),
    path('mp/exito/', views.mp_exito, name='mp_exito'),
    path('mp/fallo/', views.mp_fallo, name='mp_fallo'),
    path('mp/pendiente/', views.mp_pendiente, name='mp_pendiente'),
    path('webhook/', views.mp_webhook, name='mp_webhook'),
]
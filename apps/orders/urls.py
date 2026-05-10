from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('crear/', views.crear_pedido, name='crear_pedido'),
    path('exito/', views.pedido_exito, name='pedido_exito'),
]
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.carrito_detalle, name='carrito_detalle'),
    path('agregar/<int:variante_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar/<int:variante_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('pre-checkout/', views.pre_checkout, name='pre_checkout'),
]
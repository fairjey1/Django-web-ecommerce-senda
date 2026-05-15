from django.urls import path
from .views import home, cargar_mas_productos, about
from . import views

app_name = 'core'

urlpatterns = [
    path('', home, name='home'),
    path('about/', views.about, name='about'),
    path('cargar-mas/', views.cargar_mas_productos, name='cargar_mas'),
]


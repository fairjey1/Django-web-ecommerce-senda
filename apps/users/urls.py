from django.urls import path
from .views import AccesoMayoristasView
app_name = 'users'
urlpatterns = [
    path('acceso-mayoristas/', AccesoMayoristasView.as_view(), name='acceso_mayoristas')
]
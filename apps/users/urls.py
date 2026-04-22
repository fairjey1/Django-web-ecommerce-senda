from django.urls import path
from .views import AccesoMayoristasView, CustomLoginView, CustomLogoutView
app_name = 'users'
urlpatterns = [
    path('acceso-mayoristas/', AccesoMayoristasView.as_view(), name='acceso_mayoristas'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]
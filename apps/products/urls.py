from django.urls import path
from .views import CatalogoGenerosView, GeneroDetalleView, CategoriaPorGeneroView, ProductoDetailView

app_name = 'products'

urlpatterns = [
    path('', CatalogoGenerosView.as_view(), name='catalogo_generos'),

    path('detalle/<int:pk>/', ProductoDetailView.as_view(), name='producto_detalle'),
    
    path('<str:genero>/', GeneroDetalleView.as_view(), name='genero_detalle'),
    
    path('<str:genero>/<slug:slug>/', CategoriaPorGeneroView.as_view(), name='categoria_por_genero'),


]
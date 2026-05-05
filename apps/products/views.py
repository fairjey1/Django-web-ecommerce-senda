from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import DetailView
from .models import Categoria, Producto, Genero

class CatalogoGenerosView(View):
    """
    Vista Inicial: El usuario elige Hombre, Mujer o Unisex.
    """
    template_name = 'products/selector_generos.html'
    def get(self, request):
        opciones_genero = Genero.objects.values_list('nombre', flat=True).distinct()
        return render(request, self.template_name, {'generos': opciones_genero})

class GeneroDetalleView(View):
    """
    Muestra las categorías Padre que tienen productos del género elegido.
    Ej: Si elijo 'Hombre', muestra 'Remeras' y 'Pantalones' de hombre.
    """
    template_name = 'products/categorias_por_genero.html'

    def get(self, request, genero):
        categorias_con_productos = Categoria.objects.filter(
            categoria_padre__isnull=True,
            productos__generos__nombre__iexact=genero,
            productos__esta_activo=True
        ).distinct()

        context = {
            'genero': genero,
            'categorias': categorias_con_productos
        }
        return render(request, self.template_name, context)

class CategoriaPorGeneroView(View):
    """
    Muestra los productos de una categoría específica filtrados por género.
    """
    template_name = 'products/listado_productos.html'

    def get(self, request, genero, slug):
        categoria = get_object_or_404(Categoria, slug=slug)
        
        # Filtramos por categoría Y por el género seleccionado en el paso anterior
        productos = Producto.objects.filter(
            categorias=categoria, 
            generos__nombre__iexact=genero, 
            esta_activo=True
        )

        # Lógica de ordenado
        orden = request.GET.get('orden', 'recientes')
        if orden == 'precio_asc':
            productos = productos.order_by('precio_minorista')
        elif orden == 'precio_desc':
            productos = productos.order_by('-precio_minorista')
        else:
            productos = productos.order_by('-fecha_creacion')

        context = {
            'genero': genero,
            'categoria': categoria,
            'productos': productos,
            'subcategorias': categoria.subcategorias.all(), # Para el filtro lateral
            'orden_actual': orden
        }
        return render(request, self.template_name, context)

class ProductoDetailView(DetailView):
    '''
    Vista de detalle de un producto específico. Se accede desde el listado de productos.
    '''
    model = Producto
    template_name = 'products/producto_detalle.html'
    context_object_name = 'producto' 

    def get_queryset(self):
        """
        Sobrescribimos la consulta base para incluir nuestras reglas
        de productos activos y optimizar con prefetch_related.
        """
        return Producto.objects.filter(
            esta_activo=True
        ).prefetch_related('variantes__color', 'imagenes')

    def get_context_data(self, **kwargs):
        """
        Sobrescribimos el contexto para agregar variables extra (como las variantes)
        que no vienen por defecto con el producto.
        """
        # 1. Obtenemos el contexto original que armó DetailView
        context = super().get_context_data(**kwargs)
        
        # Agregamos las variantes al diccionario contexto para el html
        variantes = self.object.variantes.all()
        context['variantes'] = variantes
        context['colores_unicos'] = set(v.color for v in variantes)
        context['talles_unicos'] = set(v.talle for v in variantes)
        return context

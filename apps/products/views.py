import json
from multiprocessing import context

from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import DetailView

from django.db import models
from .models import Categoria, Producto, Genero

from django.core.paginator import Paginator

class CatalogoGenerosView(View):
    """
    Vista Inicial: El usuario elige Hombre, Mujer o Unisex.
    """
    template_name = 'products/selector_generos.html'
    def get(self, request):
        opciones_genero = Genero.objects.all()
        return render(request, self.template_name, {'generos': opciones_genero})

class GeneroDetalleView(View):
    """
    Muestra las categorías Padre que tienen productos del género elegido.
    Ej: Si elijo 'Hombre', muestra 'Remeras' y 'Pantalones' de hombre.
    """
    template_name = 'products/categorias_por_genero.html'

    def get(self, request, slug):
        
        genero = get_object_or_404(Genero, slug=slug)
        
        categorias_con_productos = Categoria.objects.filter(
            categoria_padre__isnull=True,
            productos__generos=genero,
            productos__esta_activo=True
        ).distinct()

        productos_list = Producto.objects.filter(
            generos=genero,
            esta_activo=True
        ).distinct()

        orden = request.GET.get('orden', 'novedades')
        if orden == 'precio_asc':
            productos_list = productos_list.order_by('precio_minorista')
        elif orden == 'precio_desc':
            productos_list = productos_list.order_by('-precio_minorista')
        else:
            productos_list = productos_list.order_by('-id')  

        # Ver Mas
        page = request.GET.get('page', 1)
        paginator = Paginator(productos_list, 8)
        
        try:
            productos_paginados = paginator.page(page)
        except:
            productos_paginados = paginator.page(1)

        context = {
            'genero': genero,
            'categorias': categorias_con_productos,
            'productos': productos_paginados,              
            'has_next': productos_paginados.has_next()
        }
        return render(request, self.template_name, context)

class CategoriaPorGeneroView(View):
    """
    Muestra los productos filtrados por un Género y una Categoría Padre específica,
    permitiendo sub-filtrar por subcategorías y ordenar los resultados.
    """
    template_name = 'products/listado_productos.html'

    def get(self, request, genero_slug, slug):
        genero_obj = get_object_or_404(Genero, slug=genero_slug)
        categoria_actual = get_object_or_404(Categoria, slug=slug, categoria_padre__isnull=True)
        
        subcategorias = Categoria.objects.filter(categoria_padre=categoria_actual)
        
        productos_list = Producto.objects.filter(
            generos=genero_obj,
            categorias=categoria_actual,
            esta_activo=True
        ).distinct()

        subcat_slug = request.GET.get('subcategoria')
        subcategoria_actual = None
        
        subcat_slug = request.GET.get('subcategoria')
        if subcat_slug:
            productos_list = productos_list.filter(categorias__slug=subcat_slug)
            subcategoria_actual = get_object_or_404(Categoria, slug=subcat_slug, categoria_padre=categoria_actual)
            
        orden = request.GET.get('orden', 'novedades')
        if orden == 'precio_asc':
            productos_list = productos_list.order_by('precio_minorista')
        elif orden == 'precio_desc':
            productos_list = productos_list.order_by('-precio_minorista')
        else:
            productos_list = productos_list.order_by('-id')

        page = request.GET.get('page', 1)
        paginator = Paginator(productos_list, 8)
        
        try:
            productos_paginados = paginator.page(page)
        except:
            productos_paginados = paginator.page(1)

        context = {
            'genero': genero_obj,
            'categoria_actual': categoria_actual,
            'subcategoria_actual': subcategoria_actual,
            'subcategorias': subcategorias,
            'productos': productos_paginados,
            'has_next': productos_paginados.has_next()
        }
        return render(request, self.template_name, context)

class ProductoDetailView(DetailView):
    """
    Vista de detalle de un producto específico. Se accede desde el listado de productos.
    """
    model = Producto
    template_name = 'products/producto_detalle.html'
    context_name = 'producto' 

    def get_queryset(self):
        return Producto.objects.filter(
            esta_activo=True
        ).prefetch_related('variantes__color', 'imagenes')

    def get_context_data(self, **kwargs):
        producto_actual = self.object
        context = super().get_context_data(**kwargs)
        
        variantes = self.object.variantes.all()
        context['variantes'] = variantes
        context['colores_unicos'] = sorted(set(v.color for v in variantes if v.color), key=lambda x: x.nombre)
        context['talles_unicos'] = sorted(set(v.talle for v in variantes if v.talle))
        
        stock_por_variante = {v.id: v.cantidad_stock for v in variantes}
        context['stock_por_variante'] = stock_por_variante

        # Generamos el JSON seguro para el JavaScript del Frontend
        variantes_lista = []
        for v in variantes:
            variantes_lista.append({
                'id': v.id,
                'color': v.color.nombre if v.color else '',
                'talle': v.talle if isinstance(v.talle, str) else (v.talle.nombre if hasattr(v.talle, 'nombre') else str(v.talle)),
                'stock': v.cantidad_stock
            })
        context['variantes_json'] = json.dumps(variantes_lista)

        # Productos relacionados
        categorias_ids = producto_actual.categorias.values_list('id', flat=True)
        productos_relacionados = Producto.objects.filter(
            esta_activo=True
        ).filter(
            models.Q(categorias__id__in=categorias_ids) | 
            models.Q(marca=producto_actual.marca)
        ).exclude(
            id=producto_actual.id
        ).distinct()[:4]
        context['productos_relacionados'] = productos_relacionados
        
        return context

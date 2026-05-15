from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from apps.products.models import Producto, Genero

def home(request):
    # 1. Últimos Ingresos (Carga inicial: 8 productos)
    ingresos_query = Producto.objects.filter(categorias__nombre__icontains="Ultimos Ingresos", esta_activo=True).distinct()
    ultimos_ingresos = ingresos_query[:8]
    has_more_ingresos = ingresos_query.count() > 8
    
    # 2. Ofertas: Agrupadas por Género (Carga inicial: 4 productos por género)
    generos = Genero.objects.all()
    ofertas_por_genero = []
    
    for genero in generos:
        ofertas_query = Producto.objects.filter(generos=genero, categorias__nombre__icontains="Ofertas", esta_activo=True).distinct()
        
        if ofertas_query.exists():
            ofertas_por_genero.append({
                'genero': genero,
                'productos': ofertas_query[:4],
                'has_more': ofertas_query.count() > 4
            })
    
    context = {
        'ultimos_ingresos': ultimos_ingresos,
        'has_more_ingresos': has_more_ingresos,
        'ofertas_por_genero': ofertas_por_genero,
    }
    return render(request, 'core/home.html', context)

def cargar_mas_productos(request):
    """Vista que devuelve un fragmento HTML con los nuevos productos"""
    tipo = request.GET.get('tipo')
    page = int(request.GET.get('page', 1))
    
    if tipo == 'ingresos':
        productos_list = Producto.objects.filter(categorias__nombre__icontains="Ultimos Ingresos", esta_activo=True).distinct()
        per_page = 8
        is_oferta = False
    elif tipo == 'ofertas':
        genero_id = request.GET.get('genero_id')
        productos_list = Producto.objects.filter(generos__id=genero_id, categorias__nombre__icontains="Ofertas", esta_activo=True).distinct()
        per_page = 4
        is_oferta = True
    else:
        return JsonResponse({'error': 'Tipo no válido'}, status=400)
        
    paginator = Paginator(productos_list, per_page)
    
    try:
        productos = paginator.page(page)
    except:
        return JsonResponse({'html': '', 'has_next': False})
        
    context = {
        'productos': productos, 
        'user': request.user,
        'is_oferta': is_oferta
    }

    html = render_to_string('core/partials/producto_card.html', context, request=request)
    
    return JsonResponse({'html': html, 'has_next': productos.has_next()})

def about(request):
    return render(request, 'core/about.html')
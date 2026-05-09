from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from apps.products.models import VarianteProducto
from .cart import Carrito
from django.contrib import messages
from django.http import JsonResponse

@require_POST
def agregar_al_carrito(request, variante_id):
    """Vista para procesar el botón de Agregar al Carrito."""

    carrito = Carrito(request)
    variante = get_object_or_404(VarianteProducto, id=variante_id)

    cantidad_nueva = int(request.POST.get('cantidad', 1))
    cantidad_en_carrito = carrito.obtener_cantidad_variante(variante)
    cantidad_total_deseada = cantidad_en_carrito + cantidad_nueva
    
    if cantidad_total_deseada > variante.cantidad_stock:
        disponible_para_agregar = variante.cantidad_stock - cantidad_en_carrito
        
        if disponible_para_agregar > 0:
            messages.error(
                request, 
                f"Ya tienes {cantidad_en_carrito} en el carrito. Solo puedes agregar {disponible_para_agregar} unidad(es) más de este talle/color."
            )
        else:
            messages.error(
                request, 
                "Ya tienes todo el stock disponible de esta prenda reservado en tu carrito."
            )
    else:
        # Si la suma está perfecta, lo agregamos
        carrito.agregar(variante=variante, cantidad=cantidad_nueva, sobreescribir_cantidad=False)
        messages.success(request, f"¡{variante.producto.nombre} agregado al carrito!")

    url_previa = request.META.get('HTTP_REFERER', '/')
    return redirect(url_previa)

def eliminar_del_carrito(request, variante_id):
    """Vista para quitar un item del carrito."""
    carrito = Carrito(request)
    variante = get_object_or_404(VarianteProducto, id=variante_id)
    carrito.eliminar(variante)
    return redirect('cart:carrito_detalle')

def carrito_detalle(request):
    """Muestra el carrito."""
    carrito = Carrito(request)
    return render(request, 'cart/carrito_detalle.html', {'carrito': carrito})

def pre_checkout(request):
    """
    Punto de control estricto. Revisa todo antes de pasar a la pantalla de pago o envío.
    """
    carrito = Carrito(request)

    # 1. Si está vacío, ni siquiera lo dejamos intentar pagar
    if len(carrito) == 0:
        messages.error(request, "Tu carrito está vacío. Agrega productos antes de pagar.")
        return redirect('cart:carrito_detalle')

    # 2. Ejecutamos el Doble Check de Stock
    alertas_stock = carrito.verificar_stock()

    # Si hubo cambios porque a alguien le robaron el stock, lo devolvemos al carrito y le avisamos
    if alertas_stock:
        for alerta in alertas_stock:
            messages.warning(request, alerta) # Usamos warning para que salga amarillo/naranja
        return redirect('cart:carrito_detalle')

    # 3. Verificamos la regla mayorista por seguridad extrema (por si vulneraron el HTML)
    if not carrito.cumple_minimo_mayorista():
        messages.error(request, "Acción denegada: No cumples con el monto mínimo de compra mayorista.")
        return redirect('cart:carrito_detalle')

    # ¡TODO PERFECTO! Aquí en el futuro lo mandaremos a MercadoPago o a la app Orders.
    # Por ahora, le mostramos un éxito y lo devolvemos.
    messages.success(request, "¡Stock verificado exitosamente! Tu carrito está reservado y listo para pagar (Próximamente).")
    return redirect('cart:carrito_detalle')

@require_POST
def actualizar_carrito(request, variante_id):
    """Actualiza la cantidad exacta de un producto ya existente en el carrito."""
    carrito = Carrito(request)
    variante = get_object_or_404(VarianteProducto, id=variante_id)
    
    try:
        cantidad_nueva = int(request.POST.get('cantidad'))
    except (ValueError, TypeError):
        messages.error(request, "Cantidad inválida.")
        return redirect('cart:carrito_detalle')

    # seguridad 
    if cantidad_nueva > variante.cantidad_stock:
        messages.error(request, f"No puedes pedir {cantidad_nueva}. Solo quedan {variante.cantidad_stock} unidades disponibles de {variante.producto.nombre}.")
    elif cantidad_nueva <= 0:
        # Si por algún motivo pone 0 o negativo, lo interpretamos como que quiere eliminar el producto del carrito.
        carrito.eliminar(variante)
        messages.info(request, "Producto eliminado del carrito.")
    else:
        carrito.agregar(variante=variante, cantidad=cantidad_nueva, sobreescribir_cantidad=True)
        messages.success(request, f"Cantidad actualizada correctamente.")
        
    return redirect('cart:carrito_detalle')

def limpiar_carrito(request):
    """Limpia todos los productos de la sesión del carrito."""
    carrito = Carrito(request)
    carrito.limpiar()
    messages.success(request, "Tu carrito ahora está vacío.")
    return redirect('cart:carrito_detalle')
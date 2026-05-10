from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ItemPedido, Pedido
from .forms import OrderCreateForm
from apps.cart.cart import Carrito

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .models import ItemPedido, Pedido
from .forms import OrderCreateForm
from apps.cart.cart import Carrito

def crear_pedido(request):
    carrito = Carrito(request)
    
    # Seguridad 1: Si el carrito está vacío
    if len(carrito) == 0:
        return redirect('cart:carrito_detalle')

    if request.method == 'POST':
        # Race Condition
        alertas_stock = carrito.verificar_stock()
        
        if alertas_stock:
            for alerta in alertas_stock:
                messages.warning(request, alerta)
            # Abortamos la compra 
            return redirect('cart:carrito_detalle')

        # Verificamos de nuevo el mínimo mayorista 
        if not carrito.cumple_minimo_mayorista():
            messages.error(request, "Debido a cambios de stock, tu carrito ya no cumple con el monto mínimo mayorista.")
            return redirect('cart:carrito_detalle')

        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Usamos atomic() para asegurar que si algo falla, todo se revierta y no queden datos inconsistentes
            with transaction.atomic():
                pedido = form.save(commit=False)
                
                if request.user.is_authenticated:
                    pedido.usuario = request.user
                    pedido.es_pedido_mayorista = getattr(request.user, 'es_mayorista', False)
                
                pedido.save() 

                for item in carrito:
                    variante = item['variante']
                    cantidad_pedida = item['cantidad']
                    
                    ItemPedido.objects.create(
                        pedido=pedido,
                        variante=variante,
                        precio=item['precio'],
                        cantidad=cantidad_pedida
                    )

                    # descuento de stock
                    variante.cantidad_stock -= cantidad_pedida
                    variante.save()

            carrito.limpiar()
            request.session['order_id'] = pedido.id
            
            return redirect('orders:pedido_exito')
    else:
        # Petición GET 
        alertas_stock = carrito.verificar_stock()
        if alertas_stock:
            for alerta in alertas_stock:
                messages.warning(request, alerta)
            return redirect('cart:carrito_detalle')

        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'nombre': request.user.first_name,
                'apellido': request.user.last_name,
                'email': request.user.email,
            }
        form = OrderCreateForm(initial=initial_data)

    return render(request, 'orders/pedido_crear.html', {'carrito': carrito, 'form': form})

def pedido_exito(request):
    order_id = request.session.get('order_id')
    return render(request, 'orders/pedido_exito.html', {'order_id': order_id})
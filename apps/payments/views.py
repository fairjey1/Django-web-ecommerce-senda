import os

from django.shortcuts import render, get_object_or_404
from django.urls import reverse
import mercadopago
from django.conf import settings
from django.shortcuts import redirect
from apps.orders.models import Pedido
from .models import ConfiguracionPagos

from django.contrib import messages

#webhook
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def instrucciones_transferencia(request, pedido_id):
    """Muestra los datos bancarios y el paso a paso para completar la compra."""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    config = ConfiguracionPagos.load()
    
    # Generamos un mensaje pre-armado para WhatsApp
    mensaje_ws = f"Hola, acabo de realizar el pedido #{pedido.id} por ${pedido.get_total_costo()}. Adjunto mi comprobante de transferencia."
    # Reemplazamos los espacios por %20 para que la URL de WhatsApp funcione
    mensaje_ws_codificado = mensaje_ws.replace(' ', '%20')
    
    context = {
        'pedido': pedido,
        'config': config,
        'mensaje_ws': mensaje_ws_codificado,
        'whatsapp_url': f"https://wa.me/{config.whatsapp_comprobantes}?text={mensaje_ws_codificado}"
    }
    return render(request, 'payments/transferencia_instrucciones.html', context)

def procesar_mercadopago(request, pedido_id):
    """
    Toma un pedido de nuestra base de datos, lo convierte al formato que pide
    MercadoPago y genera la URL de cobro (Checkout Pro).
    """
    pedido = get_object_or_404(Pedido, id=pedido_id)

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    # Lista de items a cobrar en MercadoPago 
    items_mp = []
    for item in pedido.items.all():
        items_mp.append({
            "title": item.variante.producto.nombre,
            "quantity": item.cantidad,
            "unit_price": float(item.precio), # MP exige que los precios sean float
            "currency_id": "ARS"
        })

    # Si hay un costo de envío
    if pedido.costo_envio > 0:
        items_mp.append({
            "title": "Costo de Envío a Domicilio",
            "quantity": 1,
            "unit_price": float(pedido.costo_envio),
            "currency_id": "ARS"
        })

    preference_data = {
        "items": items_mp,
        "payer": {
            "name": pedido.nombre or "Cliente",
            "surname": pedido.apellido or "Senda",
            "email": pedido.email or "correo@ejemplo.com",
        },
        "back_urls": {
            "success": request.build_absolute_uri(reverse('mp_exito')),
            "failure": request.build_absolute_uri(reverse('mp_fallo')),
            "pending": request.build_absolute_uri(reverse('mp_pendiente'))
        },
        "auto_return": "approved",
        "notification_url": request.build_absolute_uri(reverse('mp_webhook')),
        "external_reference": str(pedido.id) # id de pedido
    }

    # 5. Enviamos la petición a los servidores de MercadoPago
    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]
    

    # 6. Redirigimos al usuario a la pasarela de pago (Con manejo de errores)
    # Verificamos si MercadoPago nos devolvió un estado 201 (Creado exitosamente)
    if preference_response.get("status") == 201:
        link_de_pago = preference.get("init_point")
        return redirect(link_de_pago)
    else:
        error_mp = preference.get('message', 'Error desconocido de MercadoPago')
        messages.error(request, f"Hubo un problema al contactar con MercadoPago: {error_mp}")
        return redirect('cart:carrito_detalle')


def mp_exito(request):
    """El cliente pagó con éxito y MercadoPago lo devuelve aca."""
    # Capturamos el ID del pedido que enviamos en 'external_reference'
    pedido_id = request.GET.get('external_reference')
    payment_id = request.GET.get('payment_id')
    
    if pedido_id:
        pedido = Pedido.objects.filter(id=pedido_id).first()
        if pedido and pedido.estado == 'pendiente':
            pedido.estado = 'pagado'
            pedido.transaccion_id = payment_id # Guardamos el comprobante de MP en nuestro pedido
            pedido.save()
            
    return render(request, 'payments/mp_exito.html', {'pedido_id': pedido_id, 'payment_id': payment_id})

def mp_fallo(request):
    """El pago fue rechazado o el cliente decidió no pagar y MercadoPago lo devuelve aca."""
    return render(request, 'payments/mp_fallo.html')

def mp_pendiente(request):
    """El cliente eligió pagar en efectivo (Rapipago/PagoFácil) y está pendiente."""
    pedido_id = request.GET.get('external_reference')
    return render(request, 'payments/mp_pendiente.html', {'pedido_id': pedido_id})


@csrf_exempt
def mp_webhook(request):
    """Recibe las notificaciones en segundo plano de MercadoPago."""
    if request.method == 'POST':
        try:
            # Leemos el mensaje que nos mandó MP
            data = json.loads(request.body)
            
            # MP manda notificaciones de varios tipos. Solo nos interesa si es un 'payment'
            if data.get('type') == 'payment' or data.get('topic') == 'payment':
                # Obtenemos el ID del pago
                payment_id = data.get('data', {}).get('id')
                
                if payment_id:
                    # Le preguntamos a MP si este pago realmente existe y está aprobado
                    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
                    payment_info = sdk.payment().get(payment_id)
                    payment = payment_info["response"]

                    # Si el pago existe y su estado es 'approved' (aprobado)
                    if payment.get("status") == "approved":
                        # Rescatamos nuestro ID de pedido que guardamos en la referencia externa
                        pedido_id = payment.get("external_reference")
                        
                        if pedido_id:
                            pedido = Pedido.objects.filter(id=pedido_id).first()
                            
                            # Si el pedido existe y sigue pendiente, lo marcamos como pagado
                            if pedido and pedido.estado == 'pendiente':
                                pedido.estado = 'pagado'
                                pedido.transaccion_id = str(payment_id)
                                pedido.save()
                                print(f"Pedido #{pedido_id} marcado como PAGADO mediante Webhook.")

            return JsonResponse({'status': 'success'}, status=200)

        except Exception as e:
            print(f"Error en Webhook: {e}")
            return JsonResponse({'status': 'error'}, status=400)
            
    # Si alguien intenta entrar por el navegador (GET), le decimos que no está permitido
    return JsonResponse({'status': 'invalid method'}, status=405)
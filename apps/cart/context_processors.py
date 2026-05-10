from .cart import Carrito

def carrito(request):
    mi_carrito = Carrito(request)
    
    return {
        'carrito': mi_carrito, 
        'costo_envio': mi_carrito.obtener_costo_envio()
    }
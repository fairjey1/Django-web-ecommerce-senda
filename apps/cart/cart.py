from decimal import Decimal
from django.conf import settings
from apps.products.models import VarianteProducto

class Carrito:
    def __init__(self, request):
        """Inicializa el carrito de la sesión."""
        self.session = request.session
        self.request = request
        carrito = self.session.get(settings.CART_SESSION_ID)
        
        if not carrito:
            # Guarda un carrito vacío en la sesión
            carrito = self.session[settings.CART_SESSION_ID] = {}
        self.carrito = carrito

    def agregar(self, variante, cantidad=1, sobreescribir_cantidad=False):
        """Agrega un producto al carrito o actualiza su cantidad."""

        variante_id = str(variante.id)
        if variante_id not in self.carrito:
            self.carrito[variante_id] = {'cantidad': 0}
            
        if sobreescribir_cantidad:
            self.carrito[variante_id]['cantidad'] = cantidad
        else:
            self.carrito[variante_id]['cantidad'] += cantidad
            
        self.guardar()

    def guardar(self):
        """Marca la sesión como modificada para que Django la guarde."""
        self.session.modified = True

    def eliminar(self, variante):
        """Elimina un producto del carrito."""
        variante_id = str(variante.id)
        if variante_id in self.carrito:
            del self.carrito[variante_id]
            self.guardar()

    def limpiar(self):
        """Vacía el carrito por completo."""
        del self.session[settings.CART_SESSION_ID]
        self.guardar()

    def __iter__(self):
        """Itera sobre los items del carrito y obtiene los objetos de la DB."""
        variantes_ids = self.carrito.keys()
        variantes = VarianteProducto.objects.filter(id__in=variantes_ids).select_related('producto')

        variantes_validas_ids = [str(v.id) for v in variantes]
        ids_a_eliminar = [vid for vid in variantes_ids if vid not in variantes_validas_ids]
        if ids_a_eliminar:
            for vid in ids_a_eliminar:
                del self.carrito[vid]
            self.guardar()
        
        carrito_copia = self.carrito.copy()

        for variante in variantes:
            item = carrito_copia[str(variante.id)]
            item['variante'] = variante
            
            # Lógica de precio (Minorista vs Mayorista)
            user = self.request.user
            precio_final = variante.producto.precio_minorista
            if variante.producto.precio_promocional_minorista:
                precio_final = variante.producto.precio_promocional_minorista
                
            if user.is_authenticated and getattr(user, 'es_mayorista', False) and getattr(user, 'esta_aprobado', False):
                precio_final = variante.producto.precio_mayorista
                if variante.producto.precio_promocional_mayorista:
                    precio_final = variante.producto.precio_promocional_mayorista

            item['precio'] = Decimal(precio_final)
            item['precio_total'] = item['precio'] * item['cantidad']
            yield item

    def __len__(self):
        """
        Suma todas las cantidades de los productos en el carrito.
        """
        return sum(item['cantidad'] for item in self.carrito.values())

    def get_total_precio(self):
        """Calcula el costo total de los items en el carrito."""
        return sum(item['precio_total'] for item in self)

    def cumple_minimo_mayorista(self):
        """Verifica si el pedido cumple con el monto mínimo (Ej: 50.000 pesos) si el usuario es mayorista."""

        user = self.request.user
        if user.is_authenticated and getattr(user, 'es_mayorista', False) and getattr(user, 'esta_aprobado', False):
            MINIMO_MAYORISTA = Decimal('50000.00')
            return self.get_total_precio() >= MINIMO_MAYORISTA
        return True 
    
    def obtener_cantidad_variante(self, variante):
        """Devuelve la cantidad actual de una variante específica que ya está en el carrito."""
        variante_id = str(variante.id)
        if variante_id in self.carrito:
            return self.carrito[variante_id]['cantidad']
        return 0
    
    def verificar_stock(self):
        """
        Revisa la DB en tiempo real. Si un producto se agotó o bajó su stock,
        ajusta el carrito automáticamente y devuelve una lista de alertas.
        """
        alertas = []
        cambios_realizados = False

        # Usamos list() para no alterar el diccionario mientras lo iteramos
        for variante_id in list(self.carrito.keys()):
            try:
                variante = VarianteProducto.objects.get(id=variante_id)
            except VarianteProducto.DoesNotExist:
                continue 

            cantidad_en_carrito = self.carrito[variante_id]['cantidad']
            stock_real = variante.cantidad_stock

            if stock_real == 0:
                alertas.append(f"Lo sentimos, {variante.producto.nombre} se agotó mientras estaba en tu carrito. Lo hemos retirado.")
                del self.carrito[variante_id]
                cambios_realizados = True
            elif cantidad_en_carrito > stock_real:
                alertas.append(f"El stock de {variante.producto.nombre} bajó. Tu pedido se ajustó de {cantidad_en_carrito} a {stock_real} unidad(es).")
                self.carrito[variante_id]['cantidad'] = stock_real
                cambios_realizados = True

        if cambios_realizados:
            self.guardar()

        return alertas
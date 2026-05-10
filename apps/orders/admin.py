from django.contrib import admin

from apps.orders.models import Pedido
from django.contrib import messages


# Register your models here.

from django.contrib import admin
from .models import Pedido, ItemPedido

class ItemPedidoInline(admin.TabularInline):
    """Permite ver los productos de un pedido desde la misma pantalla del pedido."""
    readonly_fields = ['variante', 'precio', 'cantidad']
    model = ItemPedido
    raw_id_fields = ['variante'] 
    extra = 0 
    def has_delete_permission(self, request, obj = ...):
        return False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    # Columnas que se ven en la lista principal
    list_display = [
        'id', 'nombre', 'apellido', 'email', 
        'estado', 'es_pedido_mayorista', 'creado', 'actualizado'
    ]
    
    # Filtros laterales para encontrar pedidos rápido
    list_filter = ['estado', 'es_pedido_mayorista', 'creado', 'actualizado']
    
    # Buscador por nombre, email o ID
    search_fields = ['nombre', 'apellido', 'email', 'id']
    
    # Inyectamos los items dentro del detalle del pedido
    inlines = [ItemPedidoInline]

    def save_model(self, request, obj, form, change):
        """
        Triggers de seguridad
        """
        if change: # Solo si estamos editando un pedido existente
            
            pedido_antiguo = Pedido.objects.get(pk=obj.pk)
            
            #trigger para devolver stock si se cancela un pedido
            if pedido_antiguo.estado != 'cancelado' and obj.estado == 'cancelado':
                for item in obj.items.all():
                    variante = item.variante
                    variante.cantidad_stock += item.cantidad
                    variante.save()
                
                # Opcional: mensaje de aviso al administrador
                messages.warning(request, f"Pedido {obj.id} cancelado: Se han devuelto los productos al stock.")

            # trigger para volver a descontar stock si se reactiva un pedido cancelado
            elif pedido_antiguo.estado == 'cancelado' and obj.estado != 'cancelado':
                for item in obj.items.all():
                    variante = item.variante
                    variante.cantidad_stock -= item.cantidad
                    variante.save()
                
                messages.info(request, f"Pedido {obj.id} reactivado: Se ha vuelto a descontar el stock.")

        super().save_model(request, obj, form, change)
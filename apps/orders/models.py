from django.db import models

# Create your models here.

from django.db import models
from django.conf import settings
from apps.products.models import VarianteProducto

class Pedido(models.Model):

    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente de Pago'),
        ('pagado', 'Pagado'),
        ('enviado', 'Enviado'),
        ('cancelado', 'Cancelado'),
    )

    # Relación opcional
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='pedidos', 
        null=True, 
        blank=True
    )

    # Datos del Comprador 
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)

    # Datos de Envío
    direccion = models.CharField(max_length=250)
    codigo_postal = models.CharField(max_length=20)
    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)

    # Metadata del Pedido
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    # Para saber si se aplicó lógica mayorista en el momento de la creación
    es_pedido_mayorista = models.BooleanField(default=False)
    
    # Campo para guardar el ID de transacción de MercadoPago o comprobante de transferencia
    transaccion_id = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ('-creado',)
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f'Pedido {self.id}'

    def get_total_costo(self):
        """Calcula el costo total sumando los items."""
        return sum(item.get_costo() for item in self.items.all())


class ItemPedido(models.Model):
    """Representa cada producto dentro de un pedido."""
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    variante = models.ForeignKey(VarianteProducto, related_name='order_items', on_delete=models.PROTECT)
    
    # Guardo el precio
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'Item del Pedido {self.pedido.id}'

    def get_costo(self):
        """Calcula el subtotal de este item."""
        return self.precio * self.cantidad

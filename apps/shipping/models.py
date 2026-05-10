from django.db import models
from django.core.cache import cache

class ConfiguracionEnvio(models.Model):

    # Costos base
    costo_base = models.DecimalField(
        max_digits=10, decimal_places=2, default=500.00,
        help_text="Precio inicial."
    )
    costo_por_kg_extra = models.DecimalField(
        max_digits=10, decimal_places=2, default=100.00,
        help_text="Monto que se suma por cada kilogramo total del pedido."
    )
    
    # Envío Gratis
    minimo_compra_envio_gratis = models.DecimalField(
        max_digits=10, decimal_places=2, default=50000.00,
        help_text="Si el total del carrito supera este monto, el envío será $0."
    )

    class Meta:
        verbose_name = "Configuración de Envío"
        verbose_name_plural = "Configuraciones de Envío"

    def __str__(self):
        return "Configuración Global de Envíos"

    # SINGLETON 
    def save(self, *args, **kwargs):
        self.pk = 1
        super(ConfiguracionEnvio, self).save(*args, **kwargs)
        cache.delete('configuracion_envio')

    def delete(self, *args, **kwargs):
        pass 

    @classmethod
    def load(cls):
        """Carga la configuración desde la DB o la crea si no existe."""
        if cache.get('configuracion_envio'):
            return cache.get('configuracion_envio')
        
        obj, created = cls.objects.get_or_create(pk=1)
        cache.set('configuracion_envio', obj)
        return obj
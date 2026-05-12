from django.db import models
from django.core.cache import cache

class ConfiguracionPagos(models.Model):
    # Configuración de Transferencia
    descuento_transferencia = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.00,
        help_text="Porcentaje de descuento aplicado al subtotal por pagar con transferencia."
    )
    datos_bancarios = models.TextField(
        default="Banco: Banco Nación\nCBU: 0000000000000000000000\nAlias: MI.LOCAL.ROPA\nTitular: Juan Pérez",
        help_text="Información que verá el cliente para realizar el pago."
    )
    whatsapp_comprobantes = models.CharField(
        max_length=20, default="+5491100000000",
        help_text="Número de WhatsApp donde deben enviar el comprobante."
    )

    class Meta:
        verbose_name = "Configuración de Pagos"
        verbose_name_plural = "Configuraciones de Pagos"

    def __str__(self):
        return "Configuración Global de Pagos"

    def save(self, *args, **kwargs):
        self.pk = 1
        super(ConfiguracionPagos, self).save(*args, **kwargs)
        cache.delete('configuracion_pagos')

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        if cache.get('configuracion_pagos'):
            return cache.get('configuracion_pagos')
        obj, created = cls.objects.get_or_create(pk=1)
        cache.set('configuracion_pagos', obj)
        return obj
from django.db import models

# Create your models here.
from django.db import models

class SiteConfiguration(models.Model):
    # Información General
    site_name = models.CharField(max_length=255, default="Senda Distribuidora")
    
    # Contacto
    contact_email = models.EmailField(default="contacto@tuempresa.com")
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Ej: +54 9 11 1234-5678")
    address = models.CharField(max_length=255, blank=True, null=True)
    
    # Redes Sociales
    instagram_link = models.URLField(blank=True, null=True)
    facebook_link = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Configuración del Sitio"
        verbose_name_plural = "Configuraciones del Sitio"

    def save(self, *args, **kwargs):
        # Forzamos a que el ID siempre sea 1
        self.pk = 1
        super(SiteConfiguration, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Evitamos que se pueda eliminar la configuración desde el panel
        pass

    @classmethod
    def load(cls):
        # Este método busca la configuración o crea una por defecto si no existe
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Configuración General del Sitio"
from django.contrib import admin
from .models import ConfiguracionEnvio

@admin.register(ConfiguracionEnvio)
class ConfiguracionEnvioAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if ConfiguracionEnvio.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ['__str__', 'costo_base', 'costo_por_kg_extra', 'minimo_compra_envio_gratis']
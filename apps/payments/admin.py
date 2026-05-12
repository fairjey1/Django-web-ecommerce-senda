from django.contrib import admin

from apps.payments.models import ConfiguracionPagos

# Register your models here.
@admin.register(ConfiguracionPagos)
class ConfiguracionPagosAdmin(admin.ModelAdmin):
    list_display = ('descuento_transferencia', 'whatsapp_comprobantes')
    fieldsets = (
        (None, {
            'fields': ('descuento_transferencia', 'datos_bancarios', 'whatsapp_comprobantes')
        }),
    )

    def has_add_permission(self, request):
        return not ConfiguracionPagos.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
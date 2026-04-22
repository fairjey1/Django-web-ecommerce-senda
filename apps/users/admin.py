from django.contrib import admin
from .models import CustomUser 
# Register your models here.
@admin.register(CustomUser) # Registramos el modelo CustomUser en el admin
class UserAdmin(admin.ModelAdmin): # Personalizamos la vista del admin para el modelo CustomUser
    model = CustomUser
    admin.site.site_header = "Administración de Usuarios Mayoristas"
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('es_mayorista', 'esta_aprobado')
from django.contrib import admin
from .models import CustomUser 
# Register your models here.
@admin.register(CustomUser) # Registramos el modelo CustomUser en el admin
class UserAdmin(admin.ModelAdmin): # Personalizamos la vista del admin para el modelo CustomUser
    model = CustomUser
    #readonly fields
    readonly_fields = ('username', 'email', 'first_name', 'last_name', 'telefono', 'razon_social', 'instagram', 'facebook', 'mensaje', 'date_joined', 'last_login', 'is_staff', 'is_active', 'es_mayorista', 'is_superuser')
    list_display = ('email', 'first_name', 'last_name', 'esta_aprobado', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('es_mayorista', 'esta_aprobado')
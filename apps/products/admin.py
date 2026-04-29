from django.contrib import admin
from .models import Categoria, Marca, Color, Producto, VarianteProducto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ('nombre',)

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_hex')
    search_fields = ('nombre',)

class VarianteProductoInline(admin.TabularInline):
    model = VarianteProducto
    extra = 1  
    fields = ('sku', 'color', 'talle', 'cantidad_stock', 'peso_kg', 'largo_cm', 'ancho_cm', 'alto_cm')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'marca', 'genero', 'precio_minorista', 'precio_mayorista', 'esta_activo')
    list_filter = ('esta_activo', 'genero', 'marca', 'categorias')
    search_fields = ('nombre', 'descripcion', 'marca__nombre')
    filter_horizontal = ('categorias',)
    
    inlines = [VarianteProductoInline]

    fieldsets = (
        ('Información Principal', {
            'fields': ('nombre', 'descripcion', 'marca', 'genero', 'categorias')
        }),
        ('Gestión de Precios', {
            'fields': ('precio_minorista', 'precio_mayorista', 'precio_promocional'),
            'description': 'Los precios mayoristas solo serán visibles para usuarios aprobados.'
        }),
        ('Multimedia', {
            'fields': ('imagen',)
        }),
        ('Configuración del Sistema', {
            'fields': ('esta_activo',),
            'classes': ('collapse',) 
        }),
    )

@admin.register(VarianteProducto)
class VarianteProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'producto', 'color', 'talle', 'cantidad_stock', 'peso_kg')
    
    list_filter = ('talle', 'color')
    
    search_fields = ('sku', 'producto__nombre', 'color__nombre')
    ordering = ('cantidad_stock',)
from django.contrib import admin
from .models import Categoria, Genero, Marca, Color, Producto, VarianteProducto

@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria_padre', 'slug')
    list_filter = ('categoria_padre',)
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ('nombre', 'categoria_padre__nombre')
    ordering = ('categoria_padre__nombre', 'nombre')


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
    list_display = ('nombre', 'marca', 'precio_minorista', 'precio_mayorista', 'esta_activo')
    list_filter = ('esta_activo', 'marca', 'categorias', 'generos')
    search_fields = ('nombre', 'descripcion', 'marca__nombre')
    filter_horizontal = ('categorias', 'generos')

    inlines = [VarianteProductoInline]

    fieldsets = (
        ('Información Principal', {
            'fields': ('nombre', 'descripcion', 'marca', 'categorias', 'generos')
        }),
        ('Gestión de Precios', {
            'fields': ('precio_minorista', 'precio_mayorista', 'precio_promocional_minorista', 'precio_promocional_mayorista'),
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
    list_display = ('sku', 'producto', 'color', 'talle', 'cantidad_stock')
    
    list_filter = ('talle', 'color', 'producto__marca', 'producto__categorias', 'producto__generos')
    
    search_fields = ('sku', 'producto__nombre', 'color__nombre')
    ordering = ('cantidad_stock',)
from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Categoría")
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre

class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Marca")

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"

    def __str__(self):
        return self.nombre
    
class Color(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del Color")
    codigo_hex = models.CharField(max_length=7, blank=True, null=True, verbose_name="Código Hexadecimal")

    class Meta:
        verbose_name = "Color"
        verbose_name_plural = "Colores"

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    descripcion = models.TextField(verbose_name="Descripción")
    
    categorias = models.ManyToManyField(Categoria, related_name='productos', verbose_name="Categorías")
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, related_name='productos', verbose_name="Marca")
    genero = models.CharField(max_length=10, choices=[('Hombre', 'Hombre'), ('Mujer', 'Mujer'), ('Unisex', 'Unisex')], verbose_name="Género")
    
    precio_minorista = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Minorista")
    precio_mayorista = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Mayorista")
    precio_promocional = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio en Oferta")
    
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True, verbose_name="Imagen Principal")
    
    esta_activo = models.BooleanField(default=True, verbose_name="Activo / Visible")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto Base"
        verbose_name_plural = "Productos Base"

    def __str__(self):
        return self.nombre

class VarianteProducto(models.Model):
    """
    Esta es la variante real que ocupa espacio en el depósito (Ej: Remera Puma Oversize - Talle M).
    Aquí manejamos el stock y las dimensiones para el envío.
    """
    OPCIONES_TALLE = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Doble Extra Large'),
        ('U', 'Talle Único'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='variantes', verbose_name="Producto Base")
    color = models.ForeignKey(Color, default=None, null=True, on_delete=models.PROTECT, related_name='variantes', verbose_name="Color")
    talle = models.CharField(max_length=5, choices=OPCIONES_TALLE, verbose_name="Talle")
    
    sku = models.CharField(max_length=50, default=None, null=True, unique=True, verbose_name="SKU / Código de Artículo")

    cantidad_stock = models.PositiveIntegerField(default=0, verbose_name="Cantidad en Stock")
    
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name="Peso (kg)")
    largo_cm = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name="Largo (cm)")
    ancho_cm = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name="Ancho (cm)")
    alto_cm = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name="Alto (cm)")

    class Meta:
        verbose_name = "Variante de Producto"
        verbose_name_plural = "Variantes de Productos"
        unique_together = ('producto', 'talle', 'color') 

    def __str__(self):
        return f"{self.sku} - {self.producto.nombre} - {self.color.nombre} - Talle {self.talle}" 
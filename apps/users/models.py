from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):

    #datos sobre el negocio mayorista

    telefono = models.CharField(default='', max_length=20, blank=True)
    instagram = models.CharField(default='', max_length=100, blank=True)
    facebook = models.CharField(default='', max_length=100, blank=True)
    mensaje = models.TextField(blank=True)
    razon_social = models.CharField(default='', max_length=100, blank=True)

    es_mayorista = models.BooleanField(
        default=True, 
        help_text="Indica que el usuario es mayorista. Se establece automaticamente."
    )
    esta_aprobado = models.BooleanField( # campo para validar todo: logueo, compras, etc.
        default=False, 
        help_text="Indica si el administrador validó y aprobó la cuenta mayorista."
    )
    observaciones = models.TextField(
        blank=True,
        help_text="Campo para que el administrador deje observaciones sobre la cuenta mayorista."
    )


    def __str__(self):
        return self.username
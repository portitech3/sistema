from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    TIPO_CHOICES = [
        ('admin', 'Administrador'),
        ('autor', 'Autor'),
        ('vendedor', 'Vendedor'),
        ('cliente', 'Cliente'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='cliente')
    email = models.EmailField(unique=True)

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

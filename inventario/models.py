from django.db import models
from django.utils import timezone

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías"

class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True, help_text="Código único del producto")
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    descripcion = models.TextField(blank=True)
    fecha_ingreso = models.DateTimeField(default=timezone.now)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField(default=0)
    
    @property
    def total(self):
        """Calcula el total (precio_unitario * cantidad)"""
        return self.precio_unitario * self.cantidad
    
    @property
    def stock(self):
        """Mantiene compatibilidad con el código existente"""
        return self.cantidad

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    class Meta:
        ordering = ['-fecha_ingreso']
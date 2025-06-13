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
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField()
    fecha_ingreso = models.DateField(auto_now_add=True)

    @property
    def total(self):
        return self.precio_unitario * self.cantidad

    
    @property
    def stock(self):
        """Mantiene compatibilidad con el código existente"""
        return self.cantidad

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    class Meta:
        ordering = ['-fecha_ingreso']
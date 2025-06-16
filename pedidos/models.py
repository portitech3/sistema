
from django.db import models
from django.utils import timezone
from inventario.models import Producto  # ✅ CORRECTO


class Pedido(models.Model):
    CATEGORIAS = [
        ('venta', 'Venta'),
        ('reparacion', 'Reparación'),
    ]

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('produccion', 'En producción'),
        ('envio', 'En camino'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    descripcion = models.TextField(blank=True, help_text="Descripción del pedido o requerimiento del cliente")
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.PositiveIntegerField()

    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_recepcion = models.DateField(default=timezone.now)
    fecha_entrega_estimada = models.DateField(null=True, blank=True)
    fecha_entrega_real = models.DateField(null=True, blank=True)

    @property
    def cumplimiento_plazo(self):
        if self.fecha_entrega_real and self.fecha_entrega_estimada:
            if self.fecha_entrega_real <= self.fecha_entrega_estimada:
                return "A tiempo"
            else:
                return "Demorada"
        elif self.fecha_entrega_estimada and self.fecha_entrega_estimada == timezone.now().date():
            return "Vence hoy"
        return "-"

    @property
    def dias_de_atraso(self):
        if self.fecha_entrega_real and self.fecha_entrega_estimada:
            atraso = (self.fecha_entrega_real - self.fecha_entrega_estimada).days
            return atraso if atraso > 0 else 0
        elif not self.fecha_entrega_real and self.fecha_entrega_estimada:
            hoy = timezone.now().date()
            atraso = (hoy - self.fecha_entrega_estimada).days
            return atraso if atraso > 0 else 0
        return 0

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente}"

from django.db import models
from django.utils import timezone
from inventario.models import Producto

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

    def save(self, *args, **kwargs):
        if self.pk:
            pedido_anterior = Pedido.objects.get(pk=self.pk)
            if pedido_anterior.estado != self.estado:
                if self.estado in ['entregado', 'cancelado'] and pedido_anterior.estado not in ['entregado', 'cancelado']:
                    if self.producto and self.producto.cantidad >= self.cantidad:
                        self.producto.cantidad -= self.cantidad
                        self.producto.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente}"
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

from django.db import models
from .models import Pedido

class HistorialPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True, blank=True)
    cliente = models.CharField(max_length=255, blank=True, null=True)
    estado_anterior = models.CharField(max_length=100, blank=True, null=True)
    estado_nuevo = models.CharField(max_length=100, blank=True, null=True)
    cantidad_anterior = models.IntegerField(blank=True, null=True)  # <-- agrega esto
    cantidad_nueva = models.IntegerField(blank=True, null=True)     # <-- y esto
    producto_anterior = models.CharField(max_length=255, blank=True, null=True)
    producto_nuevo = models.CharField(max_length=255, blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

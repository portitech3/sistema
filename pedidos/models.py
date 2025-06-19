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
        # Verificar si es una actualización
        is_update = self.pk is not None
        pedido_anterior = None
        
        if is_update:
            try:
                pedido_anterior = Pedido.objects.get(pk=self.pk)
            except Pedido.DoesNotExist:
                pedido_anterior = None
        
        # Guardar el pedido primero
        super().save(*args, **kwargs)
        
        # Crear historial si hubo cambios
        if pedido_anterior:
            self._crear_historial_cambios(pedido_anterior)

    def _crear_historial_cambios(self, pedido_anterior):
        """Crear registros de historial para todos los cambios detectados"""
        cambios = []
        
        # Verificar cambio de cliente
        if pedido_anterior.cliente != self.cliente:
            HistorialPedido.objects.create(
                pedido=self,
                cliente_anterior=pedido_anterior.cliente,
                cliente_nuevo=self.cliente,
                tipo_cambio='cliente',
                observacion=f'Cliente cambiado de "{pedido_anterior.cliente}" a "{self.cliente}"'
            )
        
        # Verificar cambio de estado
        if pedido_anterior.estado != self.estado:
            # Lógica del inventario para estados finales
            if self.estado in ['entregado', 'cancelado'] and pedido_anterior.estado not in ['entregado', 'cancelado']:
                if self.producto and self.producto.cantidad >= self.cantidad:
                    self.producto.cantidad -= self.cantidad
                    self.producto.save()
            
            HistorialPedido.objects.create(
                pedido=self,
                estado_anterior=pedido_anterior.estado,
                estado_nuevo=self.estado,
                tipo_cambio='estado',
                observacion=f'Estado cambiado de "{pedido_anterior.get_estado_display()}" a "{self.get_estado_display()}"'
            )
        
        # Verificar cambio de producto
        if pedido_anterior.producto != self.producto:
            producto_anterior = str(pedido_anterior.producto) if pedido_anterior.producto else "Sin producto"
            producto_nuevo = str(self.producto) if self.producto else "Sin producto"
            
            HistorialPedido.objects.create(
                pedido=self,
                producto_anterior=producto_anterior,
                producto_nuevo=producto_nuevo,
                tipo_cambio='producto',
                observacion=f'Producto cambiado de "{producto_anterior}" a "{producto_nuevo}"'
            )
        
        # Verificar cambio de cantidad
        if pedido_anterior.cantidad != self.cantidad:
            HistorialPedido.objects.create(
                pedido=self,
                cantidad_anterior=pedido_anterior.cantidad,
                cantidad_nueva=self.cantidad,
                tipo_cambio='cantidad',
                observacion=f'Cantidad cambiada de {pedido_anterior.cantidad} a {self.cantidad}'
            )

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


class HistorialPedido(models.Model):
    TIPOS_CAMBIO = [
        ('cliente', 'Cambio de Cliente'),
        ('estado', 'Cambio de Estado'),
        ('producto', 'Cambio de Producto'),
        ('cantidad', 'Cambio de Cantidad'),
    ]
    
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='historial')
    tipo_cambio = models.CharField(max_length=20, choices=TIPOS_CAMBIO)
    
    # Campos para cliente
    cliente_anterior = models.CharField(max_length=100, blank=True, null=True)
    cliente_nuevo = models.CharField(max_length=100, blank=True, null=True)
    
    # Campos para estado
    estado_anterior = models.CharField(max_length=20, blank=True, null=True)
    estado_nuevo = models.CharField(max_length=20, blank=True, null=True)
    
    # Campos para cantidad
    cantidad_anterior = models.IntegerField(blank=True, null=True)
    cantidad_nueva = models.IntegerField(blank=True, null=True)
    
    # Campos para producto
    producto_anterior = models.CharField(max_length=255, blank=True, null=True)
    producto_nuevo = models.CharField(max_length=255, blank=True, null=True)
    
    observacion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Historial de Pedido"
        verbose_name_plural = "Historial de Pedidos"

    def __str__(self):
        return f"Historial #{self.id} - {self.get_tipo_cambio_display()} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"
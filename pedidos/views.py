from django.shortcuts import render, redirect
from .forms import PedidoForm
from .models import Pedido
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import HistorialPedido
from django.utils.dateparse import parse_date
from django.db.models import Q

def crear_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)

            # No se descuenta nada aquí aún
            pedido.save()
            messages.success(request, 'Pedido creado exitosamente.')
            return redirect('lista_pedidos')
    else:
        form = PedidoForm()
    
    return render(request, 'pedidos/crear_pedido.html', {'form': form})



def lista_pedidos(request):
    pedidos = Pedido.objects.all()

    cliente = request.GET.get('cliente')
    estado = request.GET.get('estado')
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    if cliente:
        pedidos = pedidos.filter(cliente__icontains=cliente)

    if estado:
        pedidos = pedidos.filter(estado=estado)

    if desde:
        pedidos = pedidos.filter(fecha_recepcion__gte=parse_date(desde))

    if hasta:
        pedidos = pedidos.filter(fecha_recepcion__lte=parse_date(hasta))

    return render(request, 'pedidos/lista_pedidos.html', {
        'pedidos': pedidos,
        'cliente': cliente,
        'estado': estado,
        'desde': desde,
        'hasta': hasta,
    })


def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    return render(request, 'pedidos/detalle_pedido.html', {'pedido': pedido})


# sistema/pedidos/views.py

def editar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    estado_anterior = pedido.estado
    cantidad_anterior = pedido.cantidad
    producto_anterior = pedido.producto.nombre if pedido.producto else None

    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            pedido_actualizado = form.save(commit=False)
            cambios = False

            cambios = []

            # Estado
            if estado_anterior != pedido_actualizado.estado:
                cambios.append('estado')

            # Cantidad
            if cantidad_anterior != pedido_actualizado.cantidad:
                cambios.append('cantidad')

            # Producto
            nuevo_nombre_producto = pedido_actualizado.producto.nombre if pedido_actualizado.producto else None
            if producto_anterior != nuevo_nombre_producto:
                cambios.append('producto')

            cliente_anterior = pedido.cliente.strip() if pedido.cliente else ""
            cliente_nuevo = pedido_actualizado.cliente.strip() if pedido_actualizado.cliente else ""
            if cliente_anterior != cliente_nuevo:
                cambios.append(f"cliente ({cliente_anterior} → {cliente_nuevo})")

            # Si cambia estado a entregado o cancelado, hacer descuento
            if pedido_actualizado.estado in ['cancelado', 'entregado'] and estado_anterior not in ['cancelado', 'entregado']:
                if pedido_actualizado.producto and pedido_actualizado.producto.cantidad >= pedido_actualizado.cantidad:
                    pedido_actualizado.producto.cantidad -= pedido_actualizado.cantidad
                    pedido_actualizado.producto.save()
                else:
                    messages.error(request, 'Stock insuficiente para completar el pedido.')
                    return redirect('editar_pedido', pedido_id=pedido.id)

            pedido_actualizado.save()

            if cambios:
                HistorialPedido.objects.create(
                    pedido=pedido,
                    cliente=cliente_nuevo,
                    estado_anterior=estado_anterior,
                    estado_nuevo=pedido_actualizado.estado,
                    cantidad_anterior=cantidad_anterior,
                    cantidad_nueva=pedido_actualizado.cantidad,
                    producto_anterior=producto_anterior,
                    producto_nuevo=pedido_actualizado.producto.nombre if pedido_actualizado.producto else None,
                    observacion=f"Cambio(s): {', '.join(cambios)}"
                )
            messages.success(request, 'Pedido actualizado correctamente.')
            return redirect('lista_pedidos')
    else:
        form = PedidoForm(instance=pedido)

    return render(request, 'pedidos/editar_pedido.html', {'form': form, 'pedido': pedido})


def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        # Variables necesarias para historial ANTES de eliminar el pedido
        estado_anterior = pedido.estado
        cantidad_anterior = pedido.cantidad
        producto_anterior = pedido.producto.nombre if pedido.producto else None
        cliente_actual = pedido.cliente

        if pedido.estado in ['entregado', 'cancelado'] and pedido.producto:
            pedido.producto.cantidad += pedido.cantidad
            pedido.producto.save()



        pedido.delete()
        messages.success(request, 'Pedido eliminado correctamente.')
        return redirect('lista_pedidos')

    return render(request, 'pedidos/eliminar_pedido.html', {'pedido': pedido})






def historial_pedidos(request):
    historial = HistorialPedido.objects.select_related('pedido').order_by('-fecha')
    return render(request, 'pedidos/historial_pedidos.html', {'historial': historial})

def vista_menu(request):
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    return render(request, 'base.html', {'pedidos_pendientes': pedidos_pendientes})

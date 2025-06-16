from django.shortcuts import render, redirect
from .forms import PedidoForm
from .models import Pedido
from django.shortcuts import get_object_or_404
from django.contrib import messages

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

from django.db.models import Q
from .models import Pedido
from django.utils.dateparse import parse_date

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
    producto_anterior = pedido.producto

    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            nuevo_pedido = form.save(commit=False)

            # 1️⃣ Si estaba en entregado/cancelado y ya había descontado stock, y ahora cambia a otro estado => se repone
            if estado_anterior in ['entregado', 'cancelado'] and nuevo_pedido.estado not in ['entregado', 'cancelado']:
                producto_anterior.cantidad += cantidad_anterior
                producto_anterior.save()

            # 2️⃣ Si ahora se cambia a entregado/cancelado, y antes no lo estaba => descontar
            if nuevo_pedido.estado in ['entregado', 'cancelado'] and estado_anterior not in ['entregado', 'cancelado']:
                if nuevo_pedido.producto.cantidad >= nuevo_pedido.cantidad:
                    nuevo_pedido.producto.cantidad -= nuevo_pedido.cantidad
                    nuevo_pedido.producto.save()
                else:
                    messages.error(request, 'Stock insuficiente para completar el pedido.')
                    return redirect('editar_pedido', pedido_id=pedido.id)

            nuevo_pedido.save()
            messages.success(request, 'Pedido actualizado correctamente.')
            return redirect('lista_pedidos')
    else:
        form = PedidoForm(instance=pedido)

    return render(request, 'pedidos/editar_pedido.html', {'form': form, 'pedido': pedido})

def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        if pedido.estado in ['entregado', 'cancelado']:
            # Reponer stock al eliminar si ya fue descontado
            pedido.producto.cantidad += pedido.cantidad
            pedido.producto.save()
        
        pedido.delete()
        messages.success(request, 'Pedido eliminado correctamente.')
        return redirect('lista_pedidos')

    return render(request, 'pedidos/eliminar_pedido.html', {'pedido': pedido})

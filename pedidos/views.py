
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.dateparse import parse_date
from .forms import PedidoForm
from .models import Pedido, HistorialPedido

def crear_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save()
            messages.success(request, 'Pedido creado exitosamente.')
            return redirect('lista_pedidos')
    else:
        form = PedidoForm()
    
    return render(request, 'pedidos/crear_pedido.html', {'form': form})

def lista_pedidos(request):
    pedidos = Pedido.objects.all()

    # Filtros
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
    historial = pedido.historial.all()[:10]  # Últimos 10 cambios
    return render(request, 'pedidos/detalle_pedido.html', {
        'pedido': pedido,
        'historial': historial
    })

def editar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            # Verificar stock antes de cambiar a estados finales
            pedido_actualizado = form.save(commit=False)
            
            # Validación de stock para estados finales
            if (pedido_actualizado.estado in ['entregado', 'cancelado'] and 
                pedido.estado not in ['entregado', 'cancelado']):
                if (pedido_actualizado.producto and 
                    pedido_actualizado.producto.cantidad < pedido_actualizado.cantidad):
                    messages.error(request, 'Stock insuficiente para completar el pedido.')
                    return render(request, 'pedidos/editar_pedido.html', {'form': form, 'pedido': pedido})
            
            # El historial se crea automáticamente en el modelo
            pedido_actualizado.save()
            messages.success(request, 'Pedido actualizado correctamente.')
            return redirect('lista_pedidos')
    else:
        form = PedidoForm(instance=pedido)

    return render(request, 'pedidos/editar_pedido.html', {'form': form, 'pedido': pedido})

def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        # Revertir inventario si el pedido estaba completado
        if pedido.estado in ['entregado', 'cancelado'] and pedido.producto:
            pedido.producto.cantidad += pedido.cantidad
            pedido.producto.save()

        pedido.delete()
        messages.success(request, 'Pedido eliminado correctamente.')
        return redirect('lista_pedidos')

    return render(request, 'pedidos/eliminar_pedido.html', {'pedido': pedido})

def historial_pedidos(request):
    historial = HistorialPedido.objects.select_related('pedido').order_by('-fecha')
    
    # Filtros opcionales
    pedido_id = request.GET.get('pedido_id')
    tipo_cambio = request.GET.get('tipo_cambio')
    
    if pedido_id:
        historial = historial.filter(pedido_id=pedido_id)
    if tipo_cambio:
        historial = historial.filter(tipo_cambio=tipo_cambio)
    
    return render(request, 'pedidos/historial_pedidos.html', {
        'historial': historial,
        'pedido_id': pedido_id,
        'tipo_cambio': tipo_cambio
    })

def vista_menu(request):
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    return render(request, 'base.html', {'pedidos_pendientes': pedidos_pendientes})
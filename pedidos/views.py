from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.dateparse import parse_date
from django.db import transaction
from .forms import PedidoForm
from .models import Pedido, HistorialPedido

def crear_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    pedido = form.save()
                    messages.success(request, 'Pedido creado exitosamente.')
                    return redirect('lista_pedidos')
            except ValueError as e:
                messages.error(request, str(e))
                return render(request, 'pedidos/crear_pedido.html', {'form': form})
            except Exception as e:
                messages.error(request, f'Error al crear el pedido: {str(e)}')
                return render(request, 'pedidos/crear_pedido.html', {'form': form})
    else:
        form = PedidoForm()
    
    return render(request, 'pedidos/crear_pedido.html', {'form': form})


def lista_pedidos(request):
    pedidos = Pedido.objects.all().order_by('-fecha_recepcion')

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

    # Estadísticas rápidas
    stats = {
        'borradores': pedidos.filter(estado='borrador').count(),
        'en_produccion': pedidos.filter(estado__in=['confirmado', 'produccion', 'terminacion']).count(),
        'terminados': pedidos.filter(estado='terminado').count(),
        'entregados': pedidos.filter(estado='entregado').count(),
    }

    return render(request, 'pedidos/lista_pedidos.html', {
        'pedidos': pedidos,
        'stats': stats,
        'cliente': cliente,
        'estado': estado,
        'desde': desde,
        'hasta': hasta,
    })

def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    historial = pedido.historial.all()[:15]  # Últimos 15 cambios
    
    context = {
        'pedido': pedido,
        'historial': historial,
        'puede_confirmar': pedido.puede_confirmar(),
        'stock_disponible': pedido.producto.cantidad if pedido.producto else 0,
    }
    
    return render(request, 'pedidos/detalle_pedido.html', context)

def editar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            try:
                with transaction.atomic():
                    pedido_actualizado = form.save()
                    messages.success(request, 'Pedido actualizado correctamente.')
                    return redirect('detalle_pedido', pedido_id=pedido_actualizado.id)
            except ValueError as e:
                messages.error(request, str(e))
                return render(request, 'pedidos/editar_pedido.html', {'form': form, 'pedido': pedido})
            except Exception as e:
                messages.error(request, f'Error al actualizar el pedido: {str(e)}')
                return render(request, 'pedidos/editar_pedido.html', {'form': form, 'pedido': pedido})
    else:
        form = PedidoForm(instance=pedido)

    return render(request, 'pedidos/editar_pedido.html', {'form': form, 'pedido': pedido})

def confirmar_pedido(request, pedido_id):
    """Vista específica para confirmar un pedido en borrador"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if pedido.estado != 'borrador':
        messages.error(request, 'Solo se pueden confirmar pedidos en estado borrador.')
        return redirect('detalle_pedido', pedido_id=pedido.id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                pedido.estado = 'confirmado'
                pedido.save()
                messages.success(request, f'Pedido confirmado exitosamente. Stock descontado: {pedido.cantidad} unidades.')
                return redirect('detalle_pedido', pedido_id=pedido.id)
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al confirmar el pedido: {str(e)}')
    
    return render(request, 'pedidos/confirmar_pedido.html', {'pedido': pedido})

def cancelar_pedido(request, pedido_id):
    """Vista específica para cancelar un pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if pedido.estado in ['entregado', 'cancelado']:
        messages.error(request, 'No se puede cancelar un pedido ya entregado o cancelado.')
        return redirect('detalle_pedido', pedido_id=pedido.id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                inventario_a_reponer = pedido.inventario_descontado
                pedido.estado = 'cancelado'
                pedido.save()
                
                if inventario_a_reponer:
                    messages.success(request, f'Pedido cancelado exitosamente. Stock repuesto: {pedido.cantidad} unidades.')
                else:
                    messages.success(request, 'Pedido cancelado exitosamente.')
                
                return redirect('detalle_pedido', pedido_id=pedido.id)
        except Exception as e:
            messages.error(request, f'Error al cancelar el pedido: {str(e)}')
    
    return render(request, 'pedidos/cancelar_pedido.html', {'pedido': pedido})

def avanzar_estado(request, pedido_id):
    """Vista para avanzar el pedido al siguiente estado en el flujo"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Definir el flujo de estados
    flujo_estados = {
        'borrador': 'confirmado',
        'confirmado': 'produccion',
        'produccion': 'terminacion',
        'terminacion': 'terminado',
        'terminado': 'entregado',
    }
    
    if pedido.estado not in flujo_estados:
        messages.error(request, 'Este pedido no puede avanzar al siguiente estado.')
        return redirect('detalle_pedido', pedido_id=pedido.id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                estado_anterior = pedido.estado
                pedido.estado = flujo_estados[estado_anterior]
                pedido.save()
                
                messages.success(request, f'Pedido avanzado de "{pedido.get_estado_display()}" exitosamente.')
                return redirect('detalle_pedido', pedido_id=pedido.id)
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al avanzar el pedido: {str(e)}')
    
    siguiente_estado = flujo_estados.get(pedido.estado)
    return render(request, 'pedidos/avanzar_estado.html', {
        'pedido': pedido,
        'siguiente_estado': dict(Pedido.ESTADOS).get(siguiente_estado, siguiente_estado)
    })

def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Si tenía inventario descontado, reponerlo
                if pedido.inventario_descontado and pedido.producto:
                    pedido.producto.cantidad += pedido.cantidad
                    pedido.producto.save()

                pedido.delete()
                messages.success(request, 'Pedido eliminado correctamente.')
                return redirect('lista_pedidos')
        except Exception as e:
            messages.error(request, f'Error al eliminar el pedido: {str(e)}')

    return render(request, 'pedidos/eliminar_pedido.html', {'pedido': pedido})

def historial_pedidos(request):
    historial = HistorialPedido.objects.select_related('pedido').order_by('-fecha')
    
    # Filtros opcionales
    pedido_id = request.GET.get('pedido_id')
    tipo_cambio = request.GET.get('tipo_cambio')
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    
    if pedido_id:
        historial = historial.filter(pedido_id=pedido_id)
    if tipo_cambio:
        historial = historial.filter(tipo_cambio=tipo_cambio)
    if desde:
        fecha_desde = parse_date(desde)
        if fecha_desde:
            historial = historial.filter(fecha__date__gte=fecha_desde)
    if hasta:
        fecha_hasta = parse_date(hasta)
        if fecha_hasta:
            historial = historial.filter(fecha__date__lte=fecha_hasta)
    
    # Paginación básica
    historial = historial[:100]  # Últimos 100 registros
    
    return render(request, 'pedidos/historial_pedidos.html', {
        'historial': historial,
        'pedido_id': pedido_id,
        'tipo_cambio': tipo_cambio,
        'desde': desde,
        'hasta': hasta,
    })

def dashboard_produccion(request):
    """Dashboard para el área de producción"""
    pedidos_confirmados = Pedido.objects.filter(estado='confirmado').count()
    pedidos_produccion = Pedido.objects.filter(estado='produccion').count()
    pedidos_terminacion = Pedido.objects.filter(estado='terminacion').count()
    pedidos_terminados = Pedido.objects.filter(estado='terminado').count()
    
    # Pedidos próximos a vencer
    from django.utils import timezone
    fecha_limite = timezone.now().date() + timezone.timedelta(days=3)
    pedidos_urgentes = Pedido.objects.filter(
        estado__in=['confirmado', 'produccion', 'terminacion'],
        fecha_entrega_estimada__lte=fecha_limite,
        fecha_entrega_estimada__gte=timezone.now().date()
    ).order_by('fecha_entrega_estimada')
    
    context = {
        'pedidos_confirmados': pedidos_confirmados,
        'pedidos_produccion': pedidos_produccion,
        'pedidos_terminacion': pedidos_terminacion,
        'pedidos_terminados': pedidos_terminados,
        'pedidos_urgentes': pedidos_urgentes,
    }
    
    return render(request, 'pedidos/dashboard_produccion.html', context)

def vista_menu(request):
    pedidos_borradores = Pedido.objects.filter(estado='borrador').count()
    pedidos_produccion = Pedido.objects.filter(estado__in=['confirmado', 'produccion', 'terminacion']).count()
    pedidos_terminados = Pedido.objects.filter(estado='terminado').count()
    
    return render(request, 'base.html', {
        'pedidos_borradores': pedidos_borradores,
        'pedidos_produccion': pedidos_produccion,
        'pedidos_terminados': pedidos_terminados,
    })


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Pedido  # Ajusta según tu modelo



@login_required
def actualizar_estado_pedido(request):
    """API para actualizar estado de pedido via AJAX"""
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        nuevo_estado = request.POST.get('nuevo_estado')
        
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            estado_anterior = pedido.estado
            
            # Lógica de descuento de inventario (tu código existente)
            if (estado_anterior == 'borrador' and 
                nuevo_estado in ['confirmado', 'produccion', 'terminacion', 'terminado', 'entregado'] and
                not pedido.inventario_descontado):
                
                # Descontar inventario
                pedido.descontar_inventario()  # Tu método existente
                pedido.inventario_descontado = True
            
            pedido.estado = nuevo_estado
            pedido.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'Pedido #{pedido.id} actualizado a {nuevo_estado}',
                'inventario_descontado': pedido.inventario_descontado
            })
            
        except Pedido.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pedido no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
def kanban_board(request):
    estados = ['borrador', 'confirmado', 'produccion', 'terminacion', 'terminado', 'entregado']
    pedidos_por_estado = {estado: Pedido.objects.filter(estado=estado) for estado in estados}
    
    return render(request, 'pedidos/kanban.html', {
        'pedidos_por_estado': pedidos_por_estado
    })


from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Pedido

def cambiar_estado_pedido(request, pedido_id):  # Add pedido_id parameter
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nuevo_estado = data.get('estado')

            # Use the pedido_id from URL instead of from POST data
            pedido = Pedido.objects.get(pk=pedido_id)
            pedido.estado = nuevo_estado
            pedido.save()

            return JsonResponse({'success': True})
        except Pedido.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Pedido no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
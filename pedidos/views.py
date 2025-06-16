from django.shortcuts import render, redirect
from .forms import PedidoForm
from .models import Pedido
from django.shortcuts import get_object_or_404
from django.contrib import messages

def crear_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_pedidos')
    else:
        form = PedidoForm()
    return render(request, 'pedidos/crear_pedido.html', {'form': form})

def lista_pedidos(request):
    pedidos = Pedido.objects.all()
    return render(request, 'pedidos/lista_pedidos.html', {'pedidos': pedidos})



def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    return render(request, 'pedidos/detalle_pedido.html', {'pedido': pedido})


def editar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, 'El pedido ha sido actualizado correctamente.')
            return redirect('lista_pedidos')
    else:
        form = PedidoForm(instance=pedido)

    return render(request, 'pedidos/editar_pedido.html', {
        'form': form,
        'pedido': pedido
    })

def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        pedido.delete()
        messages.success(request, f'El pedido N°{pedido.id} ha sido eliminado.')
        return redirect('lista_pedidos')

    return render(request, 'pedidos/eliminar_pedido.html', {
        'pedido': pedido
    })
from pedidos.models import Pedido

def pedidos_pendientes(request):
    cantidad = Pedido.objects.filter(estado='pendiente').count()
    return {'pedidos_pendientes': cantidad}

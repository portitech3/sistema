
from django.shortcuts import render
from .models import Producto
def inicio(request):
    return render(request, 'core/inicio.html')  # Busca inicio.html en /templates


def vista_inventario(request):
    return render(request, 'core/inventario.html')  # Asegúrate de que este archivo HTML exista






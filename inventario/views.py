from django.shortcuts import render

def vista_inventario(request):
    return render(request, 'inventario/productos.html')  # o 'core/inventario.html' según tu estructura

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Producto, Categoria
from .forms import ProductoForm, CategoriaForm

def vista_inventario(request):
    """Vista para mostrar todos los productos"""
    productos = Producto.objects.all()
    return render(request, 'inventario/productos.html', {
        'productos': productos
    })

def agregar_producto(request):
    """Vista para agregar un nuevo producto"""
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)
            # Si no hay categoría, crear una por defecto
            if not producto.categoria_id:
                categoria_default, created = Categoria.objects.get_or_create(
                    nombre="General",
                    defaults={'descripcion': 'Categoría por defecto'}
                )
                producto.categoria = categoria_default
            producto.save()
            messages.success(request, f'Producto "{producto.nombre}" agregado exitosamente.')
            return redirect('vista_inventario')
    else:
        form = ProductoForm()
    
    return render(request, 'inventario/agregar_producto_simple.html', {
        'form': form
    })

def editar_producto(request, producto_id):
    """Vista para editar un producto existente"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado exitosamente.')
            return redirect('vista_inventario')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'inventario/editar_producto.html', {
        'form': form,
        'producto': producto
    })

def eliminar_producto(request, producto_id):
    """Vista para eliminar un producto"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        nombre_producto = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre_producto}" eliminado exitosamente.')
        return redirect('vista_inventario')
    
    return render(request, 'inventario/eliminar_producto.html', {
        'producto': producto
    })

def agregar_categoria(request):
    """Vista para agregar una nueva categoría"""
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" agregada exitosamente.')
            return redirect('agregar_producto')
    else:
        form = CategoriaForm()
    
    return render(request, 'inventario/agregar_categoria.html', {
        'form': form
    })
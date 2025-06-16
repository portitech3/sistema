from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('', views.vista_inventario, name='inventario'),
    path('agregar/', views.agregar_producto, name='agregar_producto'),
    path('editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('categoria/', views.agregar_categoria, name='agregar_categoria'),
    path('agregar_stock/', views.agregar_stock, name='agregar_stock'),
    path('exportar_excel/', views.exportar_excel, name='exportar_excel'),

]

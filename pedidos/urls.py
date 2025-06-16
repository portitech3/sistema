from django.urls import path
from . import views

urlpatterns = [
    path('nuevo/', views.crear_pedido, name='crear_pedido'),
    path('', views.lista_pedidos, name='lista_pedidos'),  # si tenés una vista de listado
    path('<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('editar/<int:pedido_id>/', views.editar_pedido, name='editar_pedido'),
    path('eliminar/<int:pedido_id>/', views.eliminar_pedido, name='eliminar_pedido'),

]

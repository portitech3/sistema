from django.urls import path
from . import views

urlpatterns = [
    path('nuevo/', views.crear_pedido, name='crear_pedido'),
    path('', views.lista_pedidos, name='lista_pedidos'),  # si tenés una vista de listado
]

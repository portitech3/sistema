
from django.urls import path
from . import views

urlpatterns = [
    # Lista y creación de pedidos
    path('', views.lista_pedidos, name='lista_pedidos'),
    path('crear/', views.crear_pedido, name='crear_pedido'),
    
    # Detalle y edición de pedidos
    path('<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('<int:pedido_id>/editar/', views.editar_pedido, name='editar_pedido'),
    path('<int:pedido_id>/eliminar/', views.eliminar_pedido, name='eliminar_pedido'),
    
    # Acciones específicas de pedidos
    path('<int:pedido_id>/confirmar/', views.confirmar_pedido, name='confirmar_pedido'),
    path('<int:pedido_id>/cancelar/', views.cancelar_pedido, name='cancelar_pedido'),
    path('<int:pedido_id>/avanzar/', views.avanzar_estado, name='avanzar_estado'),
    
    # Historial y reportes
    path('historial/', views.historial_pedidos, name='historial_pedidos'),
    path('produccion/', views.dashboard_produccion, name='dashboard_produccion'),

        # ... tus otras URLs
    path('kanban/', views.kanban_board, name='kanban_board'),
    path('kanban/actualizar-estado/', views.actualizar_estado_pedido, name='actualizar_estado_pedido'),
    path('pedidos/kanban/', views.kanban_board, name='kanban_board'),

                    
]
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("pedidos/novo/", views.novo_pedido, name="novo_pedido"),
    path("pedidos/<int:pk>/", views.detalhe_pedido, name="detalhe_pedido"),
    path("pedidos/<int:pk>/status/", views.atualizar_status, name="atualizar_status"),
    path("demonstracao/", views.demonstracao_padroes, name="demonstracao"),
]

from django.contrib import admin
from .models import Cliente, Produto, Pedido, ItemPedido, HistoricoStatus


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ["nome", "email", "telefone", "criado_em"]
    search_fields = ["nome", "email"]


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ["nome", "preco", "peso_kg", "estoque"]
    list_editable = ["preco", "estoque"]


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ["preco_unitario"]


class HistoricoInline(admin.TabularInline):
    model = HistoricoStatus
    extra = 0
    readonly_fields = ["status_anterior", "status_novo", "observacao", "criado_em"]
    can_delete = False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ["pk", "cliente", "status", "metodo_pagamento", "total", "criado_em"]
    list_filter = ["status", "metodo_pagamento"]
    inlines = [ItemPedidoInline, HistoricoInline]
    readonly_fields = ["subtotal", "valor_frete", "taxa_servico", "total", "resultado_pagamento"]

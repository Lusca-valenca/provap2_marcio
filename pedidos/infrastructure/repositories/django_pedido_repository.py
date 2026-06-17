"""Implementação concreta do repositório usando Django ORM."""
from pedidos.domain.entities import PedidoEntity
from pedidos.domain.repositories import PedidoRepository
from pedidos.models import Cliente, Produto, Pedido, ItemPedido, HistoricoStatus


class DjangoPedidoRepository(PedidoRepository):
    def salvar(self, pedido: PedidoEntity, resultado_processamento: dict) -> int:
        cliente = Cliente.objects.get(pk=pedido.cliente_id)
        resumo = resultado_processamento["resumo_financeiro"]
        pedido_model = Pedido.objects.create(
            cliente=cliente,
            status="confirmado",
            metodo_pagamento=pedido.metodo_pagamento,
            opcao_frete=pedido.opcao_frete,
            parcelas=pedido.parcelas,
            cep_destino=pedido.cep_destino,
            subtotal=resumo["subtotal"],
            valor_frete=resumo["frete"],
            taxa_servico=resumo["taxa_servico"],
            total=resumo["total"],
            resultado_pagamento=resultado_processamento["pagamento"],
        )
        for item in pedido.itens:
            produto = Produto.objects.get(pk=item.produto.id)
            ItemPedido.objects.create(
                pedido=pedido_model,
                produto=produto,
                quantidade=item.quantidade,
                preco_unitario=item.produto.preco,
            )
        HistoricoStatus.objects.create(
            pedido=pedido_model,
            status_anterior="rascunho",
            status_novo="confirmado",
            observacao="Pedido criado pelo caso de uso CriarPedidoUseCase",
        )
        return pedido_model.pk

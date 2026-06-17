"""Caso de uso da aplicação.

Orquestra a criação do pedido sem conhecer detalhes de banco, views ou templates.
"""
from dataclasses import dataclass
from pedidos.design_patterns import FachadaPedido
from pedidos.domain.entities import PedidoEntity
from pedidos.domain.repositories import PedidoRepository


@dataclass
class CriarPedidoInput:
    pedido: PedidoEntity
    email_cliente: str


class CriarPedidoUseCase:
    def __init__(self, repository: PedidoRepository, fachada: FachadaPedido | None = None):
        self.repository = repository
        self.fachada = fachada or FachadaPedido()

    def executar(self, dados: CriarPedidoInput) -> dict:
        pedido = dados.pedido
        resultado = self.fachada.processar_pedido({
            "pedido_id": 0,
            "subtotal": float(pedido.subtotal),
            "metodo_pagamento": pedido.metodo_pagamento,
            "opcoes_pagamento": {"parcelas": pedido.parcelas} if pedido.metodo_pagamento == "cartao" else {},
            "frete": pedido.opcao_frete,
            "peso_kg": float(pedido.peso_total),
            "cep_destino": pedido.cep_destino,
            "email_cliente": dados.email_cliente,
        })
        if not resultado["sucesso"]:
            return resultado
        pedido_id = self.repository.salvar(pedido, resultado)
        resultado["pedido_id"] = pedido_id
        return resultado

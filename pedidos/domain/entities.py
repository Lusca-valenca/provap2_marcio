"""Entidades de domínio puras, sem dependência do Django.

Esta camada representa a regra de negócio central da aplicação.
"""
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class ProdutoEntity:
    id: int | None
    nome: str
    preco: Decimal
    peso_kg: Decimal = Decimal("0.500")


@dataclass(frozen=True)
class ItemPedidoEntity:
    produto: ProdutoEntity
    quantidade: int

    @property
    def subtotal(self) -> Decimal:
        return self.produto.preco * self.quantidade

    @property
    def peso_total(self) -> Decimal:
        return self.produto.peso_kg * self.quantidade


@dataclass
class PedidoEntity:
    cliente_id: int
    metodo_pagamento: str
    opcao_frete: str
    parcelas: int
    cep_destino: str
    itens: list[ItemPedidoEntity] = field(default_factory=list)

    @property
    def subtotal(self) -> Decimal:
        return sum((item.subtotal for item in self.itens), Decimal("0.00"))

    @property
    def peso_total(self) -> Decimal:
        return sum((item.peso_total for item in self.itens), Decimal("0.000"))

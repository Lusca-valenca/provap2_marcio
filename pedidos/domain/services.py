"""Serviços de domínio com regras reutilizáveis."""
from decimal import Decimal


class PoliticaPrecoPedido:
    """Calcula taxa e total do pedido. Mantém SRP e facilita testes."""

    def __init__(self, taxa_servico: Decimal, limite_frete_gratis: Decimal):
        self.taxa_servico = taxa_servico
        self.limite_frete_gratis = limite_frete_gratis

    def calcular_taxa(self, subtotal: Decimal) -> Decimal:
        return subtotal * self.taxa_servico

    def deve_aplicar_frete_gratis(self, subtotal: Decimal) -> bool:
        return subtotal >= self.limite_frete_gratis

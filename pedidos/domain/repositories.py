"""Contratos da camada de domínio.

Aplica DIP: casos de uso dependem de abstrações, não de ORM Django.
"""
from abc import ABC, abstractmethod
from .entities import PedidoEntity


class PedidoRepository(ABC):
    @abstractmethod
    def salvar(self, pedido: PedidoEntity, resultado_processamento: dict) -> int:
        """Persiste o pedido e retorna o ID criado."""
        raise NotImplementedError

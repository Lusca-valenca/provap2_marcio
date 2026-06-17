import os
from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class ClienteDTO:
    id: int
    nome: str
    email: str


class ClienteApiClient:
    """Cliente HTTP para comunicação com o microsserviço cliente-service."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or os.getenv("CLIENTE_SERVICE_URL", "http://cliente-service:8001")

    def obter_cliente(self, cliente_id: int) -> ClienteDTO | None:
        response = requests.get(f"{self.base_url}/clientes/{cliente_id}", timeout=5)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        return ClienteDTO(id=data["id"], nome=data["nome"], email=data["email"])

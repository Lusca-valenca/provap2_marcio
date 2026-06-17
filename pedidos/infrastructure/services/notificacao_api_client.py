import os

import requests


class NotificacaoApiClient:
    """Cliente HTTP para comunicação com o microsserviço notificacao-service."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or os.getenv("NOTIFICACAO_SERVICE_URL", "http://notificacao-service:8002")

    def enviar(self, destinatario: str, assunto: str, mensagem: str) -> dict:
        payload = {
            "destinatario": destinatario,
            "assunto": assunto,
            "mensagem": mensagem,
        }
        response = requests.post(f"{self.base_url}/notificacoes", json=payload, timeout=5)
        response.raise_for_status()
        return response.json()

from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI(title="Notificação Service", version="1.0.0")

class NotificacaoEntrada(BaseModel):
    destinatario: EmailStr
    assunto: str
    mensagem: str

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "notificacao-service"}

@app.post("/notificacoes")
def enviar_notificacao(payload: NotificacaoEntrada):
    # Simulação de envio. Em produção, aqui entraria e-mail, fila ou mensageria.
    return {
        "status": "notificacao_registrada",
        "destinatario": payload.destinatario,
        "assunto": payload.assunto,
        "enviado_em": datetime.utcnow().isoformat() + "Z",
    }

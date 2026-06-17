from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Cliente Service", version="1.0.0")

class Cliente(BaseModel):
    id: int
    nome: str
    email: str

CLIENTES = {
    1: Cliente(id=1, nome="Cliente Padrão", email="cliente@exemplo.com"),
    2: Cliente(id=2, nome="Lucas Valença", email="lucas@exemplo.com"),
}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "cliente-service"}

@app.get("/clientes/{cliente_id}", response_model=Cliente)
def obter_cliente(cliente_id: int):
    cliente = CLIENTES.get(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@app.get("/clientes", response_model=list[Cliente])
def listar_clientes():
    return list(CLIENTES.values())

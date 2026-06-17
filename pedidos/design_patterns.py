from abc import ABC, abstractmethod
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class ConfiguracaoSistema:

    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self):
        self.taxa_servico = Decimal("0.05")       # 5% de taxa
        self.frete_gratis_acima = Decimal("200.00")
        self.moeda = "BRL"
        self.nome_loja = "Django Shop"
        self.email_suporte = "suporte@djangoshop.com"

    def __repr__(self):
        return f"<ConfiguracaoSistema id={id(self)} loja='{self.nome_loja}'>"



class Pagamento(ABC):

    @abstractmethod
    def processar(self, valor: Decimal) -> dict:
        pass

    @abstractmethod
    def get_nome(self) -> str:
        pass


class PagamentoCartaoCredito(Pagamento):
    def __init__(self, parcelas: int = 1):
        self.parcelas = parcelas

    def processar(self, valor: Decimal) -> dict:
        juros = Decimal("0.0") if self.parcelas <= 3 else Decimal("0.02") * (self.parcelas - 3)
        valor_final = valor * (1 + juros)
        return {
            "metodo": "cartao_credito",
            "parcelas": self.parcelas,
            "valor_parcela": round(valor_final / self.parcelas, 2),
            "valor_total": round(valor_final, 2),
            "status": "aprovado",
        }

    def get_nome(self):
        return f"Cartão de Crédito ({self.parcelas}x)"


class PagamentoPix(Pagamento):
    def processar(self, valor: Decimal) -> dict:
        desconto = valor * Decimal("0.05")  # 5% de desconto no PIX
        return {
            "metodo": "pix",
            "valor_original": float(valor),
            "desconto": float(desconto),
            "valor_total": float(valor - desconto),
            "chave_pix": "pagamentos@djangoshop.com",
            "status": "aguardando_pagamento",
        }

    def get_nome(self):
        return "PIX (5% de desconto)"


class PagamentoBoleto(Pagamento):
    def processar(self, valor: Decimal) -> dict:
        return {
            "metodo": "boleto",
            "valor_total": float(valor),
            "vencimento": "3 dias úteis",
            "codigo_barras": "34191.09008 63521.700007 00000.004308 9 99780000010000",
            "status": "aguardando_pagamento",
        }

    def get_nome(self):
        return "Boleto Bancário"


class PagamentoFactory:
   
    _metodos = {
        "cartao": PagamentoCartaoCredito,
        "pix": PagamentoPix,
        "boleto": PagamentoBoleto,
    }

    @staticmethod
    def criar(metodo: str, **kwargs) -> Pagamento:
        cls = PagamentoFactory._metodos.get(metodo)
        if not cls:
            raise ValueError(f"Método de pagamento '{metodo}' não suportado. "
                             f"Opções: {list(PagamentoFactory._metodos.keys())}")

        # Clean Code + SOLID: a Factory deve proteger os clientes de detalhes
        # de construção. Apenas CartaoCredito precisa de parcelas; PIX e Boleto
        # são criados sem argumentos para evitar acoplamento e erros de kwargs.
        if cls is PagamentoCartaoCredito:
            return cls(parcelas=kwargs.get("parcelas", 1))

        return cls()

    @staticmethod
    def metodos_disponiveis() -> list:
        return list(PagamentoFactory._metodos.keys())


class ObservadorPedido(ABC):
   

    @abstractmethod
    def atualizar(self, pedido_id: int, status_anterior: str, status_novo: str, dados: dict):
        pass


class NotificadorEmail(ObservadorPedido):
    

    def atualizar(self, pedido_id, status_anterior, status_novo, dados):
        mensagens = {
            "confirmado": f"✅ Pedido #{pedido_id} confirmado! Obrigado pela compra.",
            "em_separacao": f"📦 Pedido #{pedido_id} está sendo preparado.",
            "enviado": f"🚚 Pedido #{pedido_id} foi enviado! Rastreie seu pedido.",
            "entregue": f"🎉 Pedido #{pedido_id} foi entregue com sucesso!",
            "cancelado": f"❌ Pedido #{pedido_id} foi cancelado.",
        }
        msg = mensagens.get(status_novo, f"Pedido #{pedido_id} atualizado para: {status_novo}")
        logger.info(f"[EMAIL] Para: {dados.get('email_cliente', 'N/A')} | {msg}")
        return {"canal": "email", "mensagem": msg}


class NotificadorEstoque(ObservadorPedido):

    def atualizar(self, pedido_id, status_anterior, status_novo, dados):
        if status_novo == "confirmado":
            logger.info(f"[ESTOQUE] Reservando itens do pedido #{pedido_id}")
            return {"canal": "estoque", "acao": "reservar_itens"}
        elif status_novo == "cancelado":
            logger.info(f"[ESTOQUE] Devolvendo itens do pedido #{pedido_id} ao estoque")
            return {"canal": "estoque", "acao": "devolver_itens"}
        return {"canal": "estoque", "acao": "nenhuma"}


class NotificadorAdministrador(ObservadorPedido):

    def atualizar(self, pedido_id, status_anterior, status_novo, dados):
        if status_novo == "cancelado":
            logger.warning(f"[ADMIN] ALERTA: Pedido #{pedido_id} cancelado!")
            return {"canal": "admin", "alerta": True}
        return {"canal": "admin", "alerta": False}


class GerenciadorEventosPedido:
    
    def __init__(self):
        self._observadores: list[ObservadorPedido] = []

    def adicionar_observador(self, obs: ObservadorPedido):
        self._observadores.append(obs)

    def remover_observador(self, obs: ObservadorPedido):
        self._observadores.remove(obs)

    def notificar(self, pedido_id: int, status_anterior: str, status_novo: str, dados: dict) -> list:
        resultados = []
        for obs in self._observadores:
            resultado = obs.atualizar(pedido_id, status_anterior, status_novo, dados)
            if resultado:
                resultados.append(resultado)
        return resultados



class EstrategiaFrete(ABC):

    @abstractmethod
    def calcular(self, peso_kg: float, cep_destino: str) -> dict:
        pass

    @abstractmethod
    def get_nome(self) -> str:
        pass


class FreteCorreiosPAC(EstrategiaFrete):

    def calcular(self, peso_kg: float, cep_destino: str) -> dict:
        valor = Decimal("8.00") + Decimal(str(peso_kg)) * Decimal("2.00")
        return {
            "modalidade": "PAC",
            "valor": float(valor),
            "prazo_dias": "8 a 12 dias úteis",
            "transportadora": "Correios",
        }

    def get_nome(self):
        return "PAC - Correios (econômico)"


class FreteCorreiosSedex(EstrategiaFrete):

    def calcular(self, peso_kg: float, cep_destino: str) -> dict:
        valor = Decimal("18.00") + Decimal(str(peso_kg)) * Decimal("5.00")
        return {
            "modalidade": "SEDEX",
            "valor": float(valor),
            "prazo_dias": "1 a 3 dias úteis",
            "transportadora": "Correios",
        }

    def get_nome(self):
        return "SEDEX - Correios (expresso)"


class FreteRetiradaLoja(EstrategiaFrete):

    def calcular(self, peso_kg: float, cep_destino: str) -> dict:
        return {
            "modalidade": "retirada",
            "valor": 0.0,
            "prazo_dias": "Disponível em 1 dia útil",
            "transportadora": "Retirada na loja",
        }

    def get_nome(self):
        return "Retirada na Loja (grátis)"


class CalculadoraFrete:
    _estrategias = {
        "pac": FreteCorreiosPAC,
        "sedex": FreteCorreiosSedex,
        "retirada": FreteRetiradaLoja,
    }

    def __init__(self, estrategia: EstrategiaFrete = None):
        self._estrategia = estrategia or FreteCorreiosPAC()

    def definir_estrategia(self, nome: str):
        cls = self._estrategias.get(nome)
        if not cls:
            raise ValueError(f"Estratégia '{nome}' não encontrada. "
                             f"Opções: {list(self._estrategias.keys())}")
        self._estrategia = cls()

    def calcular(self, peso_kg: float, cep: str) -> dict:
        return self._estrategia.calcular(peso_kg, cep)

    @staticmethod
    def opcoes_disponiveis():
        return list(CalculadoraFrete._estrategias.keys())


class FachadaPedido:
    
    def __init__(self):
        self.config = ConfiguracaoSistema()  # Singleton
        self.gerenciador_eventos = GerenciadorEventosPedido()

        # Registra todos os observadores
        self.gerenciador_eventos.adicionar_observador(NotificadorEmail())
        self.gerenciador_eventos.adicionar_observador(NotificadorEstoque())
        self.gerenciador_eventos.adicionar_observador(NotificadorAdministrador())

    def processar_pedido(self, dados: dict) -> dict:
        
        erros = self._validar(dados)
        if erros:
            return {"sucesso": False, "erros": erros}

        calculadora = CalculadoraFrete()
        calculadora.definir_estrategia(dados.get("frete", "pac"))
        info_frete = calculadora.calcular(
            peso_kg=float(dados.get("peso_kg", 0.5)),
            cep=dados.get("cep_destino", "00000-000"),
        )

        subtotal = Decimal(str(dados["subtotal"]))
        valor_frete = Decimal(str(info_frete["valor"]))

        if subtotal >= self.config.frete_gratis_acima:
            valor_frete = Decimal("0.00")
            info_frete["valor"] = 0.0
            info_frete["observacao"] = "Frete grátis aplicado!"

        taxa = subtotal * self.config.taxa_servico
        total = subtotal + valor_frete + taxa

        pagamento = PagamentoFactory.criar(
            dados.get("metodo_pagamento", "pix"),
            **dados.get("opcoes_pagamento", {}),
        )
        resultado_pagamento = pagamento.processar(total)

        notificacoes = self.gerenciador_eventos.notificar(
            pedido_id=dados.get("pedido_id", 0),
            status_anterior="rascunho",
            status_novo="confirmado",
            dados={"email_cliente": dados.get("email_cliente", "")},
        )

        return {
            "sucesso": True,
            "pedido_id": dados.get("pedido_id"),
            "resumo_financeiro": {
                "subtotal": float(subtotal),
                "frete": float(valor_frete),
                "taxa_servico": float(taxa),
                "total": float(total),
                "moeda": self.config.moeda,
            },
            "frete": info_frete,
            "pagamento": resultado_pagamento,
            "notificacoes_disparadas": notificacoes,
            "padroes_utilizados": [
                "Singleton (ConfiguracaoSistema)",
                "Factory Method (PagamentoFactory)",
                "Observer (NotificadorEmail, NotificadorEstoque, NotificadorAdministrador)",
                "Strategy (CalculadoraFrete)",
                "Facade (FachadaPedido)",
            ],
        }

    def atualizar_status(self, pedido_id: int, status_anterior: str,
                         status_novo: str, email_cliente: str) -> dict:
        notificacoes = self.gerenciador_eventos.notificar(
            pedido_id=pedido_id,
            status_anterior=status_anterior,
            status_novo=status_novo,
            dados={"email_cliente": email_cliente},
        )
        return {
            "sucesso": True,
            "pedido_id": pedido_id,
            "status_novo": status_novo,
            "notificacoes": notificacoes,
        }

    def _validar(self, dados: dict) -> list:
        erros = []
        if not dados.get("subtotal"):
            erros.append("Campo 'subtotal' é obrigatório.")
        if dados.get("metodo_pagamento") not in PagamentoFactory.metodos_disponiveis():
            erros.append(f"Método de pagamento inválido. Opções: {PagamentoFactory.metodos_disponiveis()}")
        if dados.get("frete") not in CalculadoraFrete.opcoes_disponiveis():
            erros.append(f"Opção de frete inválida. Opções: {CalculadoraFrete.opcoes_disponiveis()}")
        return erros

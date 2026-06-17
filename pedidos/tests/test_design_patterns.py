from decimal import Decimal
from django.test import SimpleTestCase
from pedidos.design_patterns import ConfiguracaoSistema, PagamentoFactory, CalculadoraFrete, FachadaPedido
from pedidos.domain.services import PoliticaPrecoPedido


class DesignPatternsTests(SimpleTestCase):
    def test_singleton_retorna_mesma_instancia(self):
        assert ConfiguracaoSistema() is ConfiguracaoSistema()

    def test_factory_cria_pagamento_pix_com_desconto(self):
        pagamento = PagamentoFactory.criar("pix")
        resultado = pagamento.processar(Decimal("100.00"))
        assert resultado["metodo"] == "pix"
        assert resultado["valor_total"] == 95.0

    def test_strategy_troca_frete_para_retirada(self):
        calculadora = CalculadoraFrete()
        calculadora.definir_estrategia("retirada")
        resultado = calculadora.calcular(2.0, "24900-000")
        assert resultado["valor"] == 0.0

    def test_facade_processa_pedido_valido(self):
        resultado = FachadaPedido().processar_pedido({
            "pedido_id": 1,
            "subtotal": 150,
            "metodo_pagamento": "boleto",
            "frete": "pac",
            "peso_kg": 1.0,
            "cep_destino": "24900-000",
            "email_cliente": "cliente@email.com",
        })
        assert resultado["sucesso"] is True
        assert len(resultado["padroes_utilizados"]) >= 4


class TDDPoliticaPrecoTests(SimpleTestCase):
    def test_deve_calcular_taxa_de_servico_de_5_porcento(self):
        politica = PoliticaPrecoPedido(Decimal("0.05"), Decimal("200.00"))
        assert politica.calcular_taxa(Decimal("100.00")) == Decimal("5.0000")

    def test_deve_aplicar_frete_gratis_a_partir_de_200_reais(self):
        politica = PoliticaPrecoPedido(Decimal("0.05"), Decimal("200.00"))
        assert politica.deve_aplicar_frete_gratis(Decimal("200.00")) is True

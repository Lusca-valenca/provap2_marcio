from behave import given, when, then
from pedidos.design_patterns import FachadaPedido


@given("que existe um pedido com subtotal de {subtotal:d} reais")
def step_pedido_subtotal(context, subtotal):
    context.dados = {
        "pedido_id": 1,
        "subtotal": subtotal,
        "peso_kg": 1.0,
        "cep_destino": "24900-000",
        "email_cliente": "cliente@email.com",
    }


@when("o pedido for processado com pagamento {pagamento} e frete {frete}")
def step_processar(context, pagamento, frete):
    context.dados["metodo_pagamento"] = pagamento
    context.dados["frete"] = frete
    context.resultado = FachadaPedido().processar_pedido(context.dados)


@then("o pedido deve ser processado com sucesso")
def step_sucesso(context):
    assert context.resultado["sucesso"] is True


@then("o resultado deve conter resumo financeiro e notificações")
def step_resumo(context):
    assert "resumo_financeiro" in context.resultado
    assert len(context.resultado["notificacoes_disparadas"]) >= 1


@then("o pedido deve ser recusado")
def step_recusado(context):
    assert context.resultado["sucesso"] is False

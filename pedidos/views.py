from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
import json

from .models import Pedido, Cliente, Produto, ItemPedido, HistoricoStatus
from .design_patterns import (
    FachadaPedido, PagamentoFactory, CalculadoraFrete, ConfiguracaoSistema
)


def home(request):
    config = ConfiguracaoSistema()  # Singleton
    produtos = Produto.objects.filter(estoque__gt=0)
    pedidos = Pedido.objects.select_related("cliente").all()[:10]
    context = {
        "config": config,
        "produtos": produtos,
        "pedidos": pedidos,
        "metodos_pagamento": PagamentoFactory.metodos_disponiveis(),
        "opcoes_frete": CalculadoraFrete.opcoes_disponiveis(),
        "total_pedidos": Pedido.objects.count(),
        "titulo": "Django Shop — Padrões de Projeto",
    }
    return render(request, "pedidos/home.html", context)


def novo_pedido(request):
    clientes = Cliente.objects.all()
    produtos = Produto.objects.filter(estoque__gt=0)

    if request.method == "POST":
        try:
            cliente_id = request.POST.get("cliente_id")
            metodo_pagamento = request.POST.get("metodo_pagamento")
            opcao_frete = request.POST.get("opcao_frete")
            parcelas = int(request.POST.get("parcelas", 1))
            cep = request.POST.get("cep_destino", "00000-000")

            produto_ids = request.POST.getlist("produto_id")
            quantidades = request.POST.getlist("quantidade")

            cliente = get_object_or_404(Cliente, pk=cliente_id)

            itens_data = []
            subtotal = Decimal("0")
            peso_total = 0.0
            for pid, qtd in zip(produto_ids, quantidades):
                produto = get_object_or_404(Produto, pk=pid)
                qtd = int(qtd)
                subtotal += produto.preco * qtd
                peso_total += float(produto.peso_kg) * qtd
                itens_data.append((produto, qtd))

            fachada = FachadaPedido()
            resultado = fachada.processar_pedido({
                "pedido_id": 0,  # ainda não salvo
                "subtotal": float(subtotal),
                "metodo_pagamento": metodo_pagamento,
                "opcoes_pagamento": {"parcelas": parcelas} if metodo_pagamento == "cartao" else {},
                "frete": opcao_frete,
                "peso_kg": peso_total,
                "cep_destino": cep,
                "email_cliente": cliente.email,
            })

            if not resultado["sucesso"]:
                messages.error(request, f"Erros: {resultado['erros']}")
                return render(request, "pedidos/novo_pedido.html",
                              {"clientes": clientes, "produtos": produtos})

            resumo = resultado["resumo_financeiro"]
            pedido = Pedido.objects.create(
                cliente=cliente,
                status="confirmado",
                metodo_pagamento=metodo_pagamento,
                opcao_frete=opcao_frete,
                parcelas=parcelas,
                cep_destino=cep,
                subtotal=resumo["subtotal"],
                valor_frete=resumo["frete"],
                taxa_servico=resumo["taxa_servico"],
                total=resumo["total"],
                resultado_pagamento=resultado["pagamento"],
            )

            for produto, qtd in itens_data:
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    quantidade=qtd,
                    preco_unitario=produto.preco,
                )

            HistoricoStatus.objects.create(
                pedido=pedido,
                status_anterior="rascunho",
                status_novo="confirmado",
                observacao="Pedido criado e processado via FachadaPedido",
            )

            messages.success(request, f"Pedido #{pedido.pk} criado com sucesso!")
            return redirect("detalhe_pedido", pk=pedido.pk)

        except Exception as e:
            messages.error(request, f"Erro ao processar pedido: {str(e)}")

    return render(request, "pedidos/novo_pedido.html",
                  {"clientes": clientes, "produtos": produtos})


def detalhe_pedido(request, pk):
    pedido = get_object_or_404(
        Pedido.objects.select_related("cliente").prefetch_related("itens__produto", "historico"),
        pk=pk,
    )
    proximos_status = {
        "confirmado": "em_separacao",
        "em_separacao": "enviado",
        "enviado": "entregue",
    }
    proximo = proximos_status.get(pedido.status)
    return render(request, "pedidos/detalhe_pedido.html",
                  {"pedido": pedido, "proximo_status": proximo})


def atualizar_status(request, pk):
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    pedido = get_object_or_404(Pedido, pk=pk)
    novo_status = request.POST.get("novo_status")
    status_validos = [s[0] for s in pedido._meta.get_field("status").choices]

    if novo_status not in status_validos:
        messages.error(request, "Status inválido.")
        return redirect("detalhe_pedido", pk=pk)

    status_anterior = pedido.status

    fachada = FachadaPedido()
    resultado = fachada.atualizar_status(
        pedido_id=pedido.pk,
        status_anterior=status_anterior,
        status_novo=novo_status,
        email_cliente=pedido.cliente.email,
    )

    pedido.status = novo_status
    pedido.save()

    HistoricoStatus.objects.create(
        pedido=pedido,
        status_anterior=status_anterior,
        status_novo=novo_status,
        observacao=f"Notificacoes disparadas: {len(resultado['notificacoes'])} observadores",
    )

    messages.success(
        request,
        f"Status atualizado para '{pedido.get_status_display()}'. "
        f"{len(resultado['notificacoes'])} observadores notificados (Observer)."
    )
    return redirect("detalhe_pedido", pk=pk)


def demonstracao_padroes(request):
    config1 = ConfiguracaoSistema()
    config2 = ConfiguracaoSistema()

    demos = {
        "singleton": {
            "nome": "Singleton — ConfiguracaoSistema",
            "descricao": "Ambas as variáveis apontam para o MESMO objeto na memória.",
            "mesma_instancia": config1 is config2,
            "id_config1": id(config1),
            "id_config2": id(config2),
            "dados": {
                "taxa_servico": str(config1.taxa_servico),
                "frete_gratis_acima": str(config1.frete_gratis_acima),
                "moeda": config1.moeda,
            },
        },
        "factory": {
            "nome": "Factory Method — PagamentoFactory",
            "descricao": "Cria objetos de pagamento sem expor a lógica de construção.",
            "metodos": [],
        },
        "strategy": {
            "nome": "Strategy — CalculadoraFrete",
            "descricao": "Troca o algoritmo de frete em tempo de execução.",
            "calculos": [],
        },
        "observer": {
            "nome": "Observer — GerenciadorEventosPedido",
            "descricao": "3 observadores são notificados automaticamente na mudança de status.",
            "observadores": [
                "NotificadorEmail — envia e-mail ao cliente",
                "NotificadorEstoque — reserva/devolve itens no estoque",
                "NotificadorAdministrador — alerta admin em cancelamentos",
            ],
        },
        "facade": {
            "nome": "Facade — FachadaPedido",
            "descricao": "Uma única chamada orquestra Singleton + Factory + Strategy + Observer.",
            "metodo": "fachada.processar_pedido(dados)",
            "subsistemas": [
                "Singleton (ConfiguracaoSistema)",
                "Factory Method (PagamentoFactory)",
                "Strategy (CalculadoraFrete)",
                "Observer (GerenciadorEventosPedido)",
            ],
        },
    }

    for metodo in PagamentoFactory.metodos_disponiveis():
        pagamento = PagamentoFactory.criar(metodo, parcelas=3 if metodo == "cartao" else 1)
        resultado = pagamento.processar(Decimal("150.00"))
        demos["factory"]["metodos"].append({
            "nome": pagamento.get_nome(),
            "resultado": resultado,
        })

    calc = CalculadoraFrete()
    for opcao in CalculadoraFrete.opcoes_disponiveis():
        calc.definir_estrategia(opcao)
        resultado = calc.calcular(peso_kg=1.5, cep="22041-001")
        demos["strategy"]["calculos"].append(resultado)

    return render(request, "pedidos/demonstracao.html", {"demos": demos})

from django.db import models


class Cliente(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"


class Produto(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    peso_kg = models.DecimalField(max_digits=5, decimal_places=3, default=0.5)
    estoque = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nome} - R$ {self.preco}"

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"


STATUS_PEDIDO = [
    ("rascunho", "Rascunho"),
    ("confirmado", "Confirmado"),
    ("em_separacao", "Em Separação"),
    ("enviado", "Enviado"),
    ("entregue", "Entregue"),
    ("cancelado", "Cancelado"),
]

METODO_PAGAMENTO = [
    ("cartao", "Cartão de Crédito"),
    ("pix", "PIX"),
    ("boleto", "Boleto Bancário"),
]

OPCAO_FRETE = [
    ("pac", "PAC - Correios (econômico)"),
    ("sedex", "SEDEX - Correios (expresso)"),
    ("retirada", "Retirada na Loja (grátis)"),
]


class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="pedidos")
    status = models.CharField(max_length=20, choices=STATUS_PEDIDO, default="rascunho")
    metodo_pagamento = models.CharField(max_length=20, choices=METODO_PAGAMENTO, default="pix")
    opcao_frete = models.CharField(max_length=20, choices=OPCAO_FRETE, default="pac")
    parcelas = models.PositiveSmallIntegerField(default=1)
    cep_destino = models.CharField(max_length=9, default="00000-000")

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxa_servico = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    resultado_pagamento = models.JSONField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido #{self.pk} - {self.cliente.nome} [{self.get_status_display()}]"

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-criado_em"]


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"


class HistoricoStatus(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="historico")
    status_anterior = models.CharField(max_length=20)
    status_novo = models.CharField(max_length=20)
    observacao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.pedido_id}: {self.status_anterior} -> {self.status_novo}"

    class Meta:
        verbose_name = "Historico de Status"
        verbose_name_plural = "Historicos de Status"
        ordering = ["-criado_em"]

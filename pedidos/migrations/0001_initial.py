import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('telefone', models.CharField(blank=True, max_length=20)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
            },
        ),
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('descricao', models.TextField(blank=True)),
                ('preco', models.DecimalField(decimal_places=2, max_digits=10)),
                ('peso_kg', models.DecimalField(decimal_places=3, default=0.5, max_digits=5)),
                ('estoque', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Produto',
                'verbose_name_plural': 'Produtos',
            },
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('rascunho', 'Rascunho'), ('confirmado', 'Confirmado'), ('em_separacao', 'Em Separação'), ('enviado', 'Enviado'), ('entregue', 'Entregue'), ('cancelado', 'Cancelado')], default='rascunho', max_length=20)),
                ('metodo_pagamento', models.CharField(choices=[('cartao', 'Cartão de Crédito'), ('pix', 'PIX'), ('boleto', 'Boleto Bancário')], default='pix', max_length=20)),
                ('opcao_frete', models.CharField(choices=[('pac', 'PAC - Correios (econômico)'), ('sedex', 'SEDEX - Correios (expresso)'), ('retirada', 'Retirada na Loja (grátis)')], default='pac', max_length=20)),
                ('parcelas', models.PositiveSmallIntegerField(default=1)),
                ('cep_destino', models.CharField(default='00000-000', max_length=9)),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('valor_frete', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('taxa_servico', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('resultado_pagamento', models.JSONField(blank=True, null=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pedidos', to='pedidos.cliente')),
            ],
            options={
                'verbose_name': 'Pedido',
                'verbose_name_plural': 'Pedidos',
                'ordering': ['-criado_em'],
            },
        ),
        migrations.CreateModel(
            name='HistoricoStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_anterior', models.CharField(max_length=20)),
                ('status_novo', models.CharField(max_length=20)),
                ('observacao', models.TextField(blank=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historico', to='pedidos.pedido')),
            ],
            options={
                'verbose_name': 'Historico de Status',
                'verbose_name_plural': 'Historicos de Status',
                'ordering': ['-criado_em'],
            },
        ),
        migrations.CreateModel(
            name='ItemPedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.PositiveIntegerField(default=1)),
                ('preco_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='pedidos.pedido')),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='pedidos.produto')),
            ],
            options={
                'verbose_name': 'Item do Pedido',
                'verbose_name_plural': 'Itens do Pedido',
            },
        ),
    ]

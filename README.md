# Django Shop — Aplicação de Padrões de Projeto

## Domínio: Sistema de E-commerce

Aplicação Django que demonstra **5 padrões de projeto** integrados em um sistema real de pedidos online.

---

## Padrões Implementados

### 1. Singleton (Criacional) — `ConfiguracaoSistema`
**Arquivo:** `pedidos/design_patterns.py`

Garante que apenas **uma instância** das configurações globais exista em toda a aplicação. Qualquer parte do código que instanciar `ConfiguracaoSistema()` recebe sempre o mesmo objeto.

```python
config1 = ConfiguracaoSistema()
config2 = ConfiguracaoSistema()
assert config1 is config2  # True — mesma instância
```

---

### 2. Factory Method (Criacional) — `PagamentoFactory`
**Arquivo:** `pedidos/design_patterns.py`

Centraliza a **criação de objetos de pagamento** (PIX, Cartão de Crédito, Boleto). O código cliente não conhece nem precisa conhecer as classes concretas.

```python
pagamento = PagamentoFactory.criar("pix")
resultado = pagamento.processar(Decimal("150.00"))
# {'metodo': 'pix', 'desconto': 7.5, 'valor_total': 142.5, ...}
```

---

### 3. Strategy (Comportamental) — `CalculadoraFrete`
**Arquivo:** `pedidos/design_patterns.py`

Permite **trocar o algoritmo de cálculo de frete** em tempo de execução. O contexto (`CalculadoraFrete`) é desacoplado das estratégias concretas (`FreteCorreiosPAC`, `FreteCorreiosSedex`, `FreteRetiradaLoja`).

```python
calc = CalculadoraFrete()
calc.definir_estrategia("sedex")   # troca o algoritmo
resultado = calc.calcular(1.5, "22041-001")
```

---

### 4. Observer (Comportamental) — `GerenciadorEventosPedido`
**Arquivo:** `pedidos/design_patterns.py`

Quando o status de um pedido muda, o **Sujeito** (`GerenciadorEventosPedido`) notifica automaticamente todos os **Observadores** registrados:
- `NotificadorEmail` — envia e-mail ao cliente
- `NotificadorEstoque` — reserva/devolve itens no estoque
- `NotificadorAdministrador` — alerta admin em cancelamentos

---

### 5. Facade (Estrutural) — `FachadaPedido`
**Arquivo:** `pedidos/design_patterns.py`

Fornece uma **interface simplificada** para o subsistema completo de pedidos. A `view` do Django faz apenas uma chamada e toda a complexidade (Singleton, Factory, Strategy, Observer, validações) é abstraída.

```python
fachada = FachadaPedido()
resultado = fachada.processar_pedido(dados)  # orquestra tudo
```

---

## Como Executar

```bash
# 1. Instalar dependências
pip install django

# 2. Aplicar migrações
python manage.py migrate

# 3. Criar superusuário
python manage.py createsuperuser

# 4. Popular dados de exemplo (opcional)
python manage.py shell < seed_data.py

# 5. Iniciar servidor
python manage.py runserver
```

## Acesso

- **Home:** http://localhost:8000/
- **Novo Pedido:** http://localhost:8000/pedidos/novo/
- **Demonstração dos Padrões:** http://localhost:8000/demonstracao/
- **Admin Django:** http://localhost:8000/admin/ (admin / admin123)

---

## Estrutura do Projeto

```
ecommerce/           ← configurações Django
pedidos/
  design_patterns.py ← TODOS os padrões de projeto
  models.py          ← modelos de dados
  views.py           ← lógica das rotas
  urls.py            ← roteamento
  admin.py           ← painel administrativo
templates/pedidos/
  base.html          ← template base
  home.html          ← página inicial
  novo_pedido.html   ← formulário de pedido
  detalhe_pedido.html← detalhes e mudança de status
  demonstracao.html  ← demonstração interativa dos padrões
```

---

# Complementação da Entrega — Clean Code, SOLID, TDD, BDD, Docker e Deploy

Este projeto foi complementado com uma estrutura acadêmica para demonstrar Clean Code, SOLID, Design Patterns, TDD, BDD, Arquitetura Limpa, divisão lógica em microsserviços, Docker e preparação para deploy.

## Novos arquivos principais

```text
pedidos/domain/                         # Entidades, contratos e serviços de domínio
pedidos/application/use_cases/           # Casos de uso
pedidos/infrastructure/repositories/     # Persistência com Django ORM
pedidos/tests/test_design_patterns.py    # Testes TDD
features/criacao_pedido.feature          # Cenários BDD
features/steps/pedido_steps.py           # Steps do Behave
Dockerfile                               # Container da aplicação
docker-compose.yml                       # Execução local com Docker
render.yaml                              # Configuração para deploy no Render
Procfile                                 # Deploy Heroku/Render/Railway
docs/ENTREGA_ACADEMICA.md                # Documento explicando toda a entrega
requirements.txt                         # Dependências
.env.example                             # Variáveis de ambiente exemplo
```

## Rodar localmente

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Rodar testes

```bash
pytest
```

## Rodar BDD

```bash
behave
```

## Rodar com Docker

```bash
docker compose up --build
```

Depois acesse `http://localhost:8000/`.

## Documento para apresentar

Abra o arquivo:

```text
docs/ENTREGA_ACADEMICA.md
```

Ele contém a descrição do problema, arquitetura, microsserviços, SOLID, padrões, TDD, BDD, Docker, deploy e justificativa técnica.

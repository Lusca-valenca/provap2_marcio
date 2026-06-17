# Entrega acadêmica — Django Shop

## 1. Descrição do problema escolhido
O projeto resolve o problema de gerenciamento de pedidos em um e-commerce simples. A aplicação permite cadastrar clientes, produtos, criar pedidos, calcular frete, processar pagamento simulado e acompanhar mudanças de status do pedido.

## 2. Divisão da solução em microsserviços
Para a entrega acadêmica, o domínio foi separado em serviços lógicos, deixando o projeto pronto para evolução para microsserviços físicos:

- **Serviço de Catálogo:** produtos, preço, estoque e peso.
- **Serviço de Pedidos:** criação do pedido, itens, histórico e status.
- **Serviço de Pagamento:** processamento simulado por PIX, cartão e boleto.
- **Serviço de Frete:** cálculo de PAC, SEDEX e retirada.
- **Serviço de Notificações:** e-mail, estoque e administrador via Observer.

A implementação continua em um monólito modular Django por ser mais simples para executar localmente, mas a separação por camadas e contratos permite extrair cada serviço futuramente.

## 3. Arquitetura Limpa
A estrutura foi organizada em camadas:

```text
pedidos/
  domain/                 # Entidades, contratos e regras puras
  application/use_cases/   # Casos de uso da aplicação
  infrastructure/          # Implementações com Django ORM
  presentation/            # Camada reservada para adaptação de views/API
  tests/                   # Testes automatizados
```

A regra de negócio principal fica em `domain` e `application`, evitando dependência direta de templates ou banco de dados.

## 4. Aplicação dos princípios SOLID
- **SRP:** `PoliticaPrecoPedido` calcula preço/taxa; `DjangoPedidoRepository` persiste pedidos; `CriarPedidoUseCase` orquestra a regra.
- **OCP:** novas formas de frete e pagamento podem ser adicionadas criando novas classes, sem alterar a view principal.
- **LSP:** estratégias de frete implementam o contrato `EstrategiaFrete` e podem ser substituídas entre si.
- **ISP:** contratos pequenos, como `PedidoRepository`, expõem apenas o necessário.
- **DIP:** o caso de uso depende da abstração `PedidoRepository`, não diretamente do ORM.

## 5. Design Patterns aplicados
Foram aplicados mais de 4 padrões:

1. **Singleton:** `ConfiguracaoSistema` centraliza configurações globais.
2. **Factory Method:** `PagamentoFactory` cria os métodos de pagamento.
3. **Strategy:** `CalculadoraFrete` alterna algoritmos de frete.
4. **Observer:** notificadores reagem à mudança de status do pedido.
5. **Facade:** `FachadaPedido` simplifica o processamento completo do pedido.
6. **Repository:** `PedidoRepository` e `DjangoPedidoRepository` isolam persistência.
7. **Use Case / Application Service:** `CriarPedidoUseCase` representa uma ação de negócio.

## 6. Evidências de Clean Code
- Nomes claros e em português coerente com o domínio.
- Funções pequenas com responsabilidades definidas.
- Separação entre domínio, aplicação e infraestrutura.
- Redução de acoplamento com contratos e injeção de dependência.
- Testes cobrindo regras críticas.
- Configurações externas via variáveis de ambiente.

## 7. Testes criados com TDD
Os testes estão em `pedidos/tests/test_design_patterns.py`. Eles validam Singleton, Factory, Strategy, Facade e regras de preço.

Executar:

```bash
pytest
```

Ou:

```bash
python manage.py test
```

## 8. Cenários BDD
Os cenários estão em `features/criacao_pedido.feature`, com steps em `features/steps/pedido_steps.py`.

Executar:

```bash
behave
```

## 9. Docker / Docker Compose
Arquivos criados:

- `Dockerfile`
- `docker-compose.yml`

Executar com Docker:

```bash
docker compose up --build
```

Acessar:

```text
http://localhost:8000/
```

## 10. Deploy em servidor
Foram adicionados arquivos para deploy:

- `render.yaml` para Render.
- `Procfile` para Render/Heroku/Railway.
- `requirements.txt` com Gunicorn e WhiteNoise.

Passos resumidos no Render:

1. Subir o projeto para um repositório no GitHub.
2. Entrar no Render e criar um **Web Service**.
3. Conectar o repositório.
4. Usar:
   - Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start command: `gunicorn ecommerce.wsgi:application`
5. Configurar variáveis:
   - `DEBUG=0`
   - `SECRET_KEY=<chave-segura>`
   - `ALLOWED_HOSTS=*`

## 11. Link de acesso ao sistema publicado
Campo para preencher após publicar:

```text
Link: ______________________________
```

Não foi possível publicar automaticamente porque isso exige acesso à conta do aluno em uma plataforma como Render, Railway, Heroku, AWS, Azure ou Google Cloud.

## 12. Justificativa técnica das escolhas
Django foi mantido por já existir no projeto e por entregar rapidamente autenticação, ORM, rotas, templates e painel administrativo. A Arquitetura Limpa foi aplicada para reduzir acoplamento e facilitar testes. Docker foi escolhido para padronizar o ambiente. Render/Railway foram sugeridos por serem simples para publicar aplicações acadêmicas com Python. O monólito modular foi escolhido como etapa inicial, pois é mais fácil de demonstrar e mantém separação lógica de microsserviços sem adicionar complexidade operacional desnecessária.

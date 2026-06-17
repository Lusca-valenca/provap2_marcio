# — Django Shop

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

## Complemento: Divisão real em microsserviços

Após a primeira organização como monólito modular, a solução foi adaptada para demonstrar uma divisão real em microsserviços usando Docker Compose. A aplicação principal Django passa a representar o **pedido-service**, responsável pela interface web, cadastro e alteração de pedidos. Além dele, foram adicionados dois serviços independentes em FastAPI:

| Serviço | Tecnologia | Porta | Responsabilidade |
|---|---|---:|---|
| pedido-service | Django | 8000 | Interface web, cadastro, consulta e atualização de pedidos |
| cliente-service | FastAPI | 8001 | Consulta e centralização de dados de clientes |
| notificacao-service | FastAPI | 8002 | Registro/envio simulado de notificações de pedidos |

Essa divisão foi escolhida porque cada serviço possui uma responsabilidade específica, respeitando o princípio da responsabilidade única. O serviço de pedidos não precisa conhecer detalhes internos do cadastro de clientes nem do envio de notificações, comunicando-se por HTTP através de classes clientes localizadas na camada de infraestrutura.

### Comunicação entre os serviços

A comunicação entre os microsserviços ocorre via REST/HTTP dentro da rede criada pelo Docker Compose:

- `pedido-service` chama `cliente-service` usando `CLIENTE_SERVICE_URL=http://cliente-service:8001`.
- `pedido-service` chama `notificacao-service` usando `NOTIFICACAO_SERVICE_URL=http://notificacao-service:8002`.
- Cada microsserviço possui seu próprio `Dockerfile` e pode ser executado de forma independente.

### Como executar os microsserviços

```bash
docker compose up --build
```

Após a subida dos containers, os serviços ficam disponíveis em:

- Aplicação principal: `http://localhost:8000`
- Cliente Service: `http://localhost:8001/health`
- Notificação Service: `http://localhost:8002/health`

### Justificativa técnica da adaptação

A separação em microsserviços foi adotada para aumentar a modularidade, reduzir acoplamento e permitir evolução independente das partes do sistema. O Django foi mantido no serviço principal por já conter a interface e as regras de pedido, enquanto FastAPI foi utilizado nos serviços auxiliares por ser leve, simples e adequado para APIs REST. O Docker Compose permite subir todos os serviços de forma padronizada, demonstrando um ambiente distribuído mesmo em máquina local.

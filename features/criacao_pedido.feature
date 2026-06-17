# language: pt
Funcionalidade: Criação de pedido no Django Shop
  Como cliente de um e-commerce
  Quero criar pedidos com frete e pagamento
  Para comprar produtos de forma organizada

  Cenário: Pedido válido com PIX e frete PAC
    Dado que existe um pedido com subtotal de 100 reais
    Quando o pedido for processado com pagamento pix e frete pac
    Então o pedido deve ser processado com sucesso
    E o resultado deve conter resumo financeiro e notificações

  Cenário: Pedido com método de pagamento inválido
    Dado que existe um pedido com subtotal de 100 reais
    Quando o pedido for processado com pagamento dinheiro e frete pac
    Então o pedido deve ser recusado

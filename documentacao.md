# Documentação do Sistema de Gerenciamento de Depósito

## Visão Geral

O Sistema de Gerenciamento de Depósito é uma aplicação desktop desenvolvida em Python utilizando a biblioteca Tkinter para interface gráfica. O sistema permite o gerenciamento completo de depósitos empresariais, incluindo controle de estoque, gestão de produtos, usuários, fornecedores, pedidos e rastreamento de entregas.

## Arquitetura do Sistema

### Tecnologias Utilizadas

- **Linguagem**: Python
- **Interface Gráfica**: Tkinter/ttk
- **Banco de Dados**: SQLite3
- **Manipulação de Imagens**: PIL (Python Imaging Library)

### Estrutura de Arquivos

- **main.py**: Arquivo principal contendo toda a lógica do sistema
- **logos/**: Diretório para armazenar os logos das empresas cadastradas
- **deposito_empresas/**: Diretório para armazenar os bancos de dados específicos de cada empresa
- **deposito_principal.db**: Banco de dados principal que armazena informações das empresas cadastradas
- **icons/**: Diretório contendo ícones utilizados na interface

## Modelo de Dados

### Banco de Dados Principal (deposito_principal.db)

#### Tabela: empresas
- Armazena informações sobre as empresas cadastradas no sistema
- Campos principais: id, nome, razao_social, senha, logo_path, db_nome, cnpj, etc.

### Banco de Dados da Empresa (deposito_empresas/[nome_empresa].db)

#### Tabela: produtos
- Armazena informações sobre os produtos cadastrados
- Campos principais: id, codigo_barras, sku, nome, descricao, categoria, quantidade, etc.

#### Tabela: usuarios
- Armazena informações sobre os usuários do sistema
- Campos principais: id, codigo_empresa, usuario, nome_completo, senha, tipo_acesso, etc.

#### Tabela: movimentacoes_estoque
- Registra todas as movimentações de estoque
- Campos principais: id, produto_id, tipo_movimentacao, quantidade, motivo, etc.

#### Tabela: depositos
- Armazena informações sobre os depósitos da empresa
- Campos principais: id, nome, tipo, endereco, capacidade_total, etc.

#### Tabela: localizacao_produtos
- Registra a localização dos produtos nos depósitos
- Campos principais: id, deposito_id, produto_id, quantidade, corredor, prateleira, etc.

#### Tabela: fornecedores
- Armazena informações sobre os fornecedores
- Campos principais: id, razao_social, nome_fantasia, cnpj, etc.

#### Tabela: pedidos
- Registra os pedidos realizados
- Campos principais: id, numero_pedido, cliente_id, usuario_id, status, etc.

#### Tabela: itens_pedido
- Armazena os itens de cada pedido
- Campos principais: id, pedido_id, produto_id, quantidade, preco_unitario, etc.

#### Tabela: rastreamento_entregas
- Registra o rastreamento das entregas
- Campos principais: id, pedido_id, status, localizacao, data_atualizacao, etc.

## Fluxos Principais

### 1. Cadastro e Login de Empresas

1. O sistema inicia na tela de login
2. Novas empresas podem ser cadastradas através da opção "Cadastrar Empresa"
3. Após o cadastro, a empresa pode fazer login com suas credenciais

### 2. Gestão de Produtos

1. Cadastro de novos produtos com informações detalhadas
2. Visualização e edição de produtos existentes
3. Controle de estoque com histórico de movimentações
4. Localização de produtos nos depósitos

### 3. Gestão de Usuários

1. Cadastro de usuários com diferentes níveis de acesso (CEO, Administrador, Gerente, Operador)
2. Gerenciamento de permissões por tipo de usuário
3. Controle de acesso às funcionalidades do sistema

### 4. Gestão de Depósitos

1. Cadastro de múltiplos depósitos
2. Controle de capacidade e ocupação
3. Organização de produtos por localização (corredor, prateleira, nível, posição)

### 5. Gestão de Fornecedores

1. Cadastro de fornecedores com informações de contato
2. Associação de produtos a fornecedores

### 6. Gestão de Pedidos

1. Criação de pedidos com múltiplos itens
2. Acompanhamento do status dos pedidos
3. Rastreamento de entregas

## Níveis de Acesso

### CEO
- Acesso completo a todas as funcionalidades do sistema
- Pode cadastrar e gerenciar todos os usuários
- Visualiza relatórios gerenciais

### Administrador
- Acesso a quase todas as funcionalidades, exceto algumas configurações avançadas
- Pode cadastrar e gerenciar usuários (exceto CEOs)
- Acesso a relatórios gerenciais

### Gerente
- Acesso à gestão de produtos, depósitos e pedidos
- Pode visualizar relatórios operacionais
- Não pode alterar configurações do sistema

### Operador
- Acesso limitado às operações diárias
- Pode registrar movimentações de estoque
- Pode criar e atualizar pedidos
- Acesso restrito a relatórios básicos

## Guia de Uso

### Tela de Login
- Digite o nome da empresa e senha
- Clique em "Entrar" para acessar o sistema
- Ou clique em "Cadastrar Empresa" para criar uma nova empresa

### Menu Principal
- Navegue pelas diferentes funcionalidades através do menu lateral
- O cabeçalho mostra informações da empresa logada

### Cadastro de Produtos
1. Acesse a opção "Produtos" no menu
2. Clique em "Novo Produto"
3. Preencha as informações solicitadas
4. Clique em "Salvar"

### Movimentação de Estoque
1. Acesse a opção "Estoque" no menu
2. Selecione o produto desejado
3. Clique em "Movimentar"
4. Selecione o tipo de movimentação (entrada, saída, ajuste)
5. Informe a quantidade e o motivo
6. Clique em "Confirmar"

### Criação de Pedidos
1. Acesse a opção "Pedidos" no menu
2. Clique em "Novo Pedido"
3. Selecione o tipo de pedido e o cliente
4. Adicione os produtos desejados
5. Informe as quantidades e preços
6. Clique em "Finalizar Pedido"

## Considerações Técnicas

### Segurança
- Senhas armazenadas com hash criptográfico
- Controle de acesso baseado em perfis de usuário
- Validação de dados em formulários

### Banco de Dados
- Utilização de SQLite para facilitar a portabilidade
- Banco de dados separado para cada empresa
- Relacionamentos entre tabelas para garantir integridade dos dados

### Interface
- Design responsivo adaptável a diferentes resoluções
- Estilo visual consistente em todas as telas
- Mensagens de feedback para o usuário

## Solução de Problemas

### Problemas de Login
- Verifique se o nome da empresa e senha estão corretos
- Certifique-se de que a empresa está cadastrada no sistema

### Erros de Banco de Dados
- Verifique se os arquivos de banco de dados existem nas pastas corretas
- Certifique-se de que o usuário tem permissão para acessar os arquivos

### Problemas com Imagens
- Verifique se as imagens estão nos formatos suportados (JPEG, PNG)
- Certifique-se de que a pasta "logos" existe e tem permissão de escrita

## Extensões Futuras

- Implementação de relatórios avançados
- Integração com sistemas de nota fiscal
- Aplicativo móvel para inventário
- Módulo de análise preditiva de estoque
- Integração com e-commerce
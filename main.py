# Importação de bibliotecas padrão do Python
import os          # Manipulação de arquivos e diretórios
import re          # Expressões regulares para validação de dados
import sqlite3     # Banco de dados SQLite para armazenamento local
import hashlib     # Funções de hash para criptografia de senhas

# Importação de bibliotecas para interface gráfica
import tkinter as tk                          # Biblioteca principal para GUI
from tkinter import ttk, messagebox, filedialog  # Componentes adicionais de interface

# Importação de biblioteca para manipulação de imagens
from PIL import Image, ImageTk                # Processamento e exibição de imagens

class SistemaGerenciamentoDeposito:
    """Classe principal que implementa o sistema de gerenciamento de depósito.
    
    Esta classe é responsável por gerenciar todo o fluxo do sistema, incluindo:
    - Autenticação e cadastro de empresas
    - Gerenciamento de produtos e estoque
    - Controle de usuários com diferentes níveis de acesso
    - Gestão de depósitos, fornecedores e pedidos
    - Interface gráfica para todas as operações
    """

    def __init__(self):
        """Inicializa o sistema de gerenciamento de depósito.
        
        Este método configura o ambiente inicial do sistema, incluindo:
        - Criação das pastas necessárias para armazenamento de dados
        - Inicialização do banco de dados principal
        - Configuração da janela principal e estilos visuais
        - Preparação da tela de login
        - Definição de métodos auxiliares para mensagens
        """
        # Definição da paleta de cores como atributo da classe
        self.cores = {
            "fundo": "#F0F7FF",            # Azul muito claro para fundo
            "fundo_alt": "#E1EBFA",       # Azul claro alternativo
            "primaria": "#1E88E5",        # Azul vibrante
            "primaria_escura": "#1565C0", # Azul escuro
            "secundaria": "#26C6DA",      # Ciano
            "destaque": "#FF5722",       # Laranja vibrante
            "sucesso": "#2E7D32",        # Verde escuro
            "alerta": "#D32F2F",         # Vermelho
            "texto": "#263238",          # Quase preto
            "texto_claro": "#FFFFFF",    # Branco
            "borda": "#BBDEFB",          # Azul muito claro para bordas
            "hover": "#E3F2FD",          # Azul muito claro para hover
            "sombra": "rgba(0,0,0,0.1)"  # Sombra sutil para elementos
        }
        
        # Cria as pastas necessárias para o funcionamento do sistema
        self.criar_pastas()
        # Inicializa o banco de dados principal
        self.criar_banco_principal()

        # Configuração da janela principal
        self.root = tk.Tk()
        self.root.title("Sistema de Gerenciamento de Depósito")
        self.root.geometry("1000x700")  # Define o tamanho inicial da janela
        self.configurar_estilos()  # Aplica estilos visuais personalizados

        # Inicialização de variáveis importantes
        self.empresa_logada = None  # Armazena dados da empresa logada
        self.logo_path = None       # Caminho para o logo da empresa
        self.preview_logo = None    # Armazena referência da imagem do logo para exibição
        
        # Exibe a tela de login inicial
        self.tela_login()

        # Definição de métodos auxiliares para exibição de mensagens
        def exibir_mensagem_aviso(titulo, mensagem):
            """Exibe uma mensagem de aviso sem fechar ou alterar a tela atual.
            
            Args:
                titulo (str): Título da mensagem de aviso
                mensagem (str): Conteúdo da mensagem de aviso
            """
            messagebox.showwarning(titulo, mensagem)

        self.exibir_mensagem_aviso = exibir_mensagem_aviso

        def exibir_mensagem_erro(titulo, mensagem):
            """Exibe uma mensagem de erro sem fechar ou alterar a tela atual.
            
            Args:
                titulo (str): Título da mensagem de erro
                mensagem (str): Conteúdo da mensagem de erro
            """
            messagebox.showerror(titulo, mensagem)

        self.exibir_mensagem_erro = exibir_mensagem_erro

    def criar_pastas(self):
        """Cria as pastas necessárias para logos e bancos de dados das empresas.
        
        Este método verifica se as pastas essenciais existem e as cria caso necessário:
        - 'logos': Armazena as imagens de logo das empresas cadastradas
        - 'deposito_empresas': Armazena os bancos de dados específicos de cada empresa
        """
        # Verifica e cria a pasta para armazenar logos das empresas
        if not os.path.exists("logos"):
            os.makedirs("logos")
            
        # Verifica e cria a pasta para armazenar os bancos de dados das empresas
        if not os.path.exists("deposito_empresas"):
            os.makedirs("deposito_empresas")

    def criar_banco_principal(self):
        """Cria o banco de dados principal do sistema.
        
        Este método é responsável por:
        - Criar o arquivo de banco de dados principal (deposito_principal.db) se não existir
        - Criar a tabela 'empresas' com todos os campos necessários
        - Garantir que colunas adicionais existam na tabela 'empresas'
        - Criar tabelas auxiliares para o sistema (movimentações, depósitos, etc.)
        
        O banco de dados principal armazena informações sobre as empresas cadastradas
        e serve como ponto central para o sistema.
        """
        conn = sqlite3.connect("deposito_principal.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empresas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                logo_path TEXT,
                db_nome TEXT UNIQUE NOT NULL,
                admin_user TEXT NOT NULL,
                tipo_usuario TEXT DEFAULT 'CEO',
                cnpj TEXT,
                endereco TEXT,
                telefone TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        conn = sqlite3.connect("deposito_principal.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS empresas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                razao_social TEXT,
                senha TEXT NOT NULL,
                logo_path TEXT,
                db_nome TEXT UNIQUE NOT NULL,
                cnpj TEXT DEFAULT '',
                inscricao_estadual TEXT DEFAULT '',
                endereco TEXT DEFAULT '',
                cidade TEXT DEFAULT '',
                estado TEXT DEFAULT '',
                cep TEXT DEFAULT '',
                telefone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                website TEXT DEFAULT '',
                admin_user TEXT DEFAULT '',
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                plano_assinatura TEXT DEFAULT 'basic',
                status TEXT DEFAULT 'active'
            )
        """
        )

        # Garante que as colunas 'cnpj', 'endereco', 'telefone' e 'admin_user' existam.
        for coluna in ["cnpj", "endereco", "telefone", "admin_user"]:
            try:
                cursor.execute(
                    f"ALTER TABLE empresas ADD COLUMN {coluna} TEXT DEFAULT ''"
                )
            except sqlite3.OperationalError:
                pass

        # Criar tabela de movimentações de estoque
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                tipo_movimentacao TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                motivo TEXT,
                nota_fiscal TEXT,
                usuario_id INTEGER NOT NULL,
                data_movimentacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (produto_id) REFERENCES produtos (id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
            """
        )

        # Criar tabela de depósitos
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS depositos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL,
                endereco TEXT,
                cidade TEXT,
                estado TEXT,
                cep TEXT,
                responsavel_id INTEGER,
                capacidade_total REAL,
                status TEXT DEFAULT 'ativo',
                FOREIGN KEY (responsavel_id) REFERENCES usuarios (id)
            )
            """
        )

        # Criar tabela de localização de produtos nos depósitos
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS localizacao_produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deposito_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                corredor TEXT,
                prateleira TEXT,
                nivel TEXT,
                posicao TEXT,
                data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deposito_id) REFERENCES depositos (id),
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            )
            """
        )

        # Criar tabela de fornecedores
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS fornecedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                razao_social TEXT NOT NULL,
                nome_fantasia TEXT,
                cnpj TEXT UNIQUE,
                inscricao_estadual TEXT,
                endereco TEXT,
                cidade TEXT,
                estado TEXT,
                cep TEXT,
                telefone TEXT,
                email TEXT,
                contato_nome TEXT,
                prazo_entrega INTEGER,
                condicao_pagamento TEXT,
                status TEXT DEFAULT 'ativo'
            )
            """
        )

        # Criar tabela de pedidos
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_pedido TEXT UNIQUE NOT NULL,
                cliente_id INTEGER,
                usuario_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pendente',
                tipo_pedido TEXT NOT NULL,
                data_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_entrega_prevista DATE,
                data_entrega_real DATE,
                valor_total REAL,
                observacoes TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
            """
        )

        # Criar tabela de itens do pedido
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS itens_pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                desconto REAL DEFAULT 0,
                subtotal REAL NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            )
            """
        )

        # Criar tabela de rastreamento de entregas
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rastreamento_entregas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                localizacao TEXT,
                data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                observacoes TEXT,
                usuario_id INTEGER NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
            """
        )

        conn.commit()
        conn.close()

    def criar_banco_empresa(self, db_nome):
        """Cria o banco de dados específico para a empresa com as tabelas de produtos e usuários."""
        caminho_db = f"deposito_empresas/{db_nome}.db"
        if os.path.exists(caminho_db):
            try:
                os.remove(caminho_db)
            except PermissionError:
                # Se não conseguir remover, tenta usar um nome alternativo
                import time
                caminho_db = f"deposito_empresas/{db_nome}_{int(time.time())}.db"

        conn = sqlite3.connect(caminho_db)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_barras TEXT UNIQUE,
                sku TEXT UNIQUE,
                nome TEXT NOT NULL,
                descricao TEXT,
                categoria TEXT,
                marca TEXT,
                quantidade INTEGER NOT NULL,
                quantidade_minima INTEGER DEFAULT 0,
                preco_custo REAL NOT NULL,
                preco_venda REAL NOT NULL,
                localizacao TEXT,
                fornecedor TEXT,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                ultima_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'"
        )
        tabela_existe = cursor.fetchone()

        if not tabela_existe:
            cursor.execute(
                """
                CREATE TABLE usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo_empresa TEXT NOT NULL,
                    empresa_nome TEXT NOT NULL,
                    usuario TEXT NOT NULL,
                    nome_completo TEXT NOT NULL,
                    nome_supervisor TEXT NOT NULL,
                    turno TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    senha TEXT NOT NULL,
                    tipo_acesso TEXT NOT NULL CHECK(tipo_acesso IN ('CEO', 'Administrador', 'Gerente', 'Operador')),
                    departamento TEXT,
                    cargo TEXT,
                    data_admissao DATE,
                    ultimo_acesso DATETIME,
                    criado_por TEXT,
                    FOREIGN KEY (criado_por) REFERENCES usuarios(id)
                )
                """
            )
        else:
            colunas_necessarias = [
                "codigo_empresa",
                "empresa_nome",
                "usuario",
                "nome_supervisor",
                "turno",
            ]
            for coluna in colunas_necessarias:
                try:
                    cursor.execute(
                        f"""
                        ALTER TABLE usuarios 
                        ADD COLUMN {coluna} TEXT NOT NULL DEFAULT ''
                    """
                    )
                except sqlite3.OperationalError:
                    pass

        # Criar tabela de movimentações de estoque
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                tipo_movimentacao TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                motivo TEXT,
                nota_fiscal TEXT,
                usuario_id INTEGER NOT NULL,
                data_movimentacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (produto_id) REFERENCES produtos (id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
            """
        )

        # Criar tabela de depósitos
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS depositos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL,
                endereco TEXT,
                cidade TEXT,
                estado TEXT,
                cep TEXT,
                responsavel_id INTEGER,
                capacidade_total REAL,
                status TEXT DEFAULT 'ativo',
                FOREIGN KEY (responsavel_id) REFERENCES usuarios (id)
            )
            """
        )

        # Criar tabela de localização de produtos nos depósitos
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS localizacao_produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deposito_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                corredor TEXT,
                prateleira TEXT,
                nivel TEXT,
                posicao TEXT,
                data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deposito_id) REFERENCES depositos (id),
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            )
            """
        )

        # Criar tabela de fornecedores
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS fornecedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                razao_social TEXT NOT NULL,
                nome_fantasia TEXT,
                cnpj TEXT UNIQUE,
                inscricao_estadual TEXT,
                endereco TEXT,
                cidade TEXT,
                estado TEXT,
                cep TEXT,
                telefone TEXT,
                email TEXT,
                contato_nome TEXT,
                prazo_entrega INTEGER,
                condicao_pagamento TEXT,
                status TEXT DEFAULT 'ativo'
            )
            """
        )

        # Criar tabela de pedidos
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_pedido TEXT UNIQUE NOT NULL,
                cliente_id INTEGER,
                usuario_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pendente',
                tipo_pedido TEXT NOT NULL,
                data_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_entrega_prevista DATE,
                data_entrega_real DATE,
                valor_total REAL,
                observacoes TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
            """
        )

        # Criar tabela de itens do pedido
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS itens_pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                desconto REAL DEFAULT 0,
                subtotal REAL NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            )
            """
        )

        # Criar tabela de rastreamento de entregas
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rastreamento_entregas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                localizacao TEXT,
                data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                observacoes TEXT,
                usuario_id INTEGER NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
            """
        )

        conn.commit()
        conn.close()

    def obter_conexao_empresa(self):
        """Retorna a conexão com o banco de dados da empresa logada."""
        if self.empresa_logada:
            return sqlite3.connect(
                f'deposito_empresas/{self.empresa_logada["db_nome"]}.db'
            )
        return None

    # Métodos para gerenciamento de depósitos
    def criar_deposito(self, nome, tipo, endereco, cidade, estado, cep, responsavel_id, capacidade_total):
        """Cria um novo depósito no sistema.
        
        Args:
            nome (str): Nome do depósito
            tipo (str): Tipo do depósito (ex: 'Geral', 'Refrigerado', etc)
            endereco (str): Endereço completo do depósito
            cidade (str): Cidade onde está localizado
            estado (str): Estado onde está localizado
            cep (str): CEP do endereço
            responsavel_id (int): ID do usuário responsável pelo depósito
            capacidade_total (float): Capacidade total de armazenamento
            
        Returns:
            int: ID do depósito criado ou None em caso de erro
        """
        try:
            conn = self.obter_conexao_empresa()
            if not conn:
                self.exibir_mensagem_erro("Erro", "Empresa não está logada")
                return None
                
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO depositos 
                (nome, tipo, endereco, cidade, estado, cep, responsavel_id, capacidade_total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome, tipo, endereco, cidade, estado, cep, responsavel_id, capacidade_total))
            
            deposito_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return deposito_id
            
        except sqlite3.Error as e:
            self.exibir_mensagem_erro("Erro ao criar depósito", str(e))
            return None

    def obter_deposito(self, deposito_id):
        """Obtém os dados de um depósito específico.
        
        Args:
            deposito_id (int): ID do depósito a ser consultado
            
        Returns:
            dict: Dicionário com os dados do depósito ou None se não encontrado
        """
        try:
            conn = self.obter_conexao_empresa()
            if not conn:
                return None
                
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nome, tipo, endereco, cidade, estado, cep, 
                       responsavel_id, capacidade_total, status
                FROM depositos
                WHERE id = ?
            """, (deposito_id,))
            
            deposito = cursor.fetchone()
            conn.close()
            
            if deposito:
                return {
                    'id': deposito[0],
                    'nome': deposito[1],
                    'tipo': deposito[2],
                    'endereco': deposito[3],
                    'cidade': deposito[4],
                    'estado': deposito[5],
                    'cep': deposito[6],
                    'responsavel_id': deposito[7],
                    'capacidade_total': deposito[8],
                    'status': deposito[9]
                }
            return None
            
        except sqlite3.Error as e:
            self.exibir_mensagem_erro("Erro ao consultar depósito", str(e))
            return None

    def listar_depositos(self, filtro=None):
        """Lista todos os depósitos cadastrados com opção de filtro.
        
        Args:
            filtro (dict, optional): Dicionário com filtros a serem aplicados
            
        Returns:
            list: Lista de dicionários com dados dos depósitos
        """
        try:
            conn = self.obter_conexao_empresa()
            if not conn:
                return []
                
            cursor = conn.cursor()
            query = """
                SELECT id, nome, tipo, endereco, cidade, estado, cep, 
                       responsavel_id, capacidade_total, status
                FROM depositos
                WHERE 1=1
            """
            
            params = []
            if filtro:
                if 'status' in filtro:
                    query += " AND status = ?"
                    params.append(filtro['status'])
                if 'tipo' in filtro:
                    query += " AND tipo = ?"
                    params.append(filtro['tipo'])
                if 'cidade' in filtro:
                    query += " AND cidade = ?"
                    params.append(filtro['cidade'])
            
            cursor.execute(query, params)
            depositos = cursor.fetchall()
            conn.close()
            
            return [{
                'id': d[0],
                'nome': d[1],
                'tipo': d[2],
                'endereco': d[3],
                'cidade': d[4],
                'estado': d[5],
                'cep': d[6],
                'responsavel_id': d[7],
                'capacidade_total': d[8],
                'status': d[9]
            } for d in depositos]
            
        except sqlite3.Error as e:
            self.exibir_mensagem_erro("Erro ao listar depósitos", str(e))
            return []

    def atualizar_deposito(self, deposito_id, dados):
        """Atualiza os dados de um depósito existente.
        
        Args:
            deposito_id (int): ID do depósito a ser atualizado
            dados (dict): Dicionário com os campos a serem atualizados
            
        Returns:
            bool: True se atualizado com sucesso, False caso contrário
        """
        try:
            conn = self.obter_conexao_empresa()
            if not conn:
                return False
                
            cursor = conn.cursor()
            campos_permitidos = [
                'nome', 'tipo', 'endereco', 'cidade', 'estado', 'cep',
                'responsavel_id', 'capacidade_total', 'status'
            ]
            
            updates = [f"{campo} = ?" for campo in dados.keys() 
                      if campo in campos_permitidos]
            valores = [dados[campo] for campo in dados.keys() 
                      if campo in campos_permitidos]
            
            if not updates:
                return False
                
            query = f"""
                UPDATE depositos
                SET {', '.join(updates)}
                WHERE id = ?
            """
            valores.append(deposito_id)
            
            cursor.execute(query, valores)
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            self.exibir_mensagem_erro("Erro ao atualizar depósito", str(e))
            return False

    def excluir_deposito(self, deposito_id):
        """Exclui um depósito do sistema (exclusão lógica).
        
        Args:
            deposito_id (int): ID do depósito a ser excluído
            
        Returns:
            bool: True se excluído com sucesso, False caso contrário
        """
        try:
            conn = self.obter_conexao_empresa()
            if not conn:
                return False
                
            cursor = conn.cursor()
            # Verifica se existem produtos no depósito
            cursor.execute("""
                SELECT COUNT(*) FROM localizacao_produtos
                WHERE deposito_id = ?
            """, (deposito_id,))
            
            if cursor.fetchone()[0] > 0:
                self.exibir_mensagem_erro(
                    "Erro",
                    "Não é possível excluir o depósito pois existem produtos vinculados"
                )
                conn.close()
                return False
            
            # Realiza exclusão lógica
            cursor.execute("""
                UPDATE depositos
                SET status = 'inativo'
                WHERE id = ?
            """, (deposito_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            self.exibir_mensagem_erro("Erro ao excluir depósito", str(e))
            return False

    # Métodos para gerenciamento de fornecedores
    def criar_fornecedor(self, razao_social, nome_fantasia, cnpj, inscricao_estadual, 
                        endereco, cidade, estado, cep, telefone, email, 
                        contato_nome, prazo_entrega, condicao_pagamento):
        """Cria um novo fornecedor no sistema.
        
        Args:
            razao_social (str): Razão social do fornecedor
            nome_fantasia (str): Nome fantasia do fornecedor
            cnpj (str): CNPJ do fornecedor
            inscricao_estadual (str): Inscrição estadual
            endereco (str): Endereço completo
            cidade (str): Cidade
            estado (str): Estado
            cep (str): CEP
            telefone (str): Telefone de contato
            email (str): Email de contato
            contato_nome (str): Nome da pessoa de contato
            prazo_entrega (int): Prazo médio de entrega em dias
            condicao_pagamento (str): Condições de pagamento
            
        Returns:
            int: ID do fornecedor criado ou None em caso de erro
        """
        try:
            conn = self.obter_conexao_empresa()
            if not conn:
                self.exibir_mensagem_erro("Erro", "Empresa não está logada")
                return None
                
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fornecedores (
                    razao_social, nome_fantasia, cnpj, inscricao_estadual,
                    endereco, cidade, estado, cep, telefone, email,
                    contato_nome, prazo_entrega, condicao_pagamento
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (razao_social, nome_fantasia, cnpj, inscricao_estadual,
                  endereco, cidade, estado, cep, telefone, email,
                  contato_nome, prazo_entrega, condicao_pagamento))
            
            fornecedor_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return fornecedor_id
            
        except sqlite3.Error as e:
            self.exibir_mensagem_erro("Erro ao criar fornecedor", str(e))
            return None

    def obter_fornecedor(self, fornecedor_id):
        """Obtém os dados de um fornecedor específico.
        
        Args:
            fornecedor_id (int): ID do fornecedor a ser consultado
            
        Returns:
            dict: Dicionário com os dados do fornecedor ou None se não encontrado
        """
        try:
            conn = self.obter_conexao_empresa()
            if not conn:
                return None
                
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, razao_social, nome_fantasia, cnpj, inscricao_estadual,
                       endereco, cidade, estado, cep, telefone, email,
                       contato_nome, prazo_entrega, condicao_pagamento, status
                FROM fornecedores
                WHERE id = ?
            """, (fornecedor_id,))
            
            fornecedor = cursor.fetchone()
            conn.close()
            
            if fornecedor:
                return {
                    'id': fornecedor[0],
                    'razao_social': fornecedor[1],
                    'nome_fantasia': fornecedor[2],
                    'cnpj': fornecedor[3],
                    'inscricao_estadual': fornecedor[4],
                    'endereco': fornecedor[5],
                    'cidade': fornecedor[6],
                    'estado': fornecedor[7],
                    'cep': fornecedor[8],
                    'telefone': fornecedor[9],
                    'email': fornecedor[10],
                    'contato_nome': fornecedor[11],
                    'prazo_entrega': fornecedor[12],
                    'condicao_pagamento': fornecedor[13],
                    'status': fornecedor[14]
                }
            return None
            
        except sqlite3.Error as e:
            self.exibir_mensagem_erro("Erro ao consultar fornecedor", str(e))
            return None

    def listar_fornecedores(self, filtro=None):
        """Lista todos os fornecedores cadastrados com opção de filtro.
        
        Args:
            filtro (dict, optional): Dicionário com filtros a serem aplicados
            
        Returns:
            list: Lista de dicionários com dados dos fornecedores
        """
        try:
            conn = self.obter_conexao_empresa()
            if not conn:
                return []
                
            cursor = conn.cursor()
            query = """
                SELECT id, razao_social, nome_fantasia, cnpj, inscricao_estadual,
                       endereco, cidade, estado, cep, telefone, email,
                       contato_nome, prazo_entrega, condicao_pagamento, status
                FROM fornecedores
                WHERE 1=1
            """
            
            params = []
            if filtro:
                if 'status' in filtro:
                    query += " AND status = ?"
                    params.append(filtro['status'])
                if 'cidade' in filtro:
                    query += " AND cidade = ?"
                    params.append(filtro['cidade'])
                if 'estado' in filtro:
                    query += " AND estado = ?"
                    params.append(filtro['estado'])
            
            cursor.execute(query, params)
            fornecedores = cursor.fetchall()
            conn.close()
            
            return [{
                'id': f[0],
                'razao_social': f[1],
                'nome_fantasia': f[2],
                'cnpj': f[3],
                'inscricao_estadual': f[4],
                'endereco': f[5],
                'cidade': f[6],
                'estado': f[7],
                'cep': f[8],
                'telefone': f[9],
                'email': f[10],
                'contato_nome': f[11],
                'prazo_entrega': f[12],
                'condicao_pagamento': f[13],
                'status': f[14]
            } for f in fornecedores]
            
        except sqlite3.Error as e:
            self.exibir_mensagem_erro("Erro ao listar fornecedores", str(e))
            return []

    def atualizar_fornecedor(self, fornecedor_id, dados):
        """Atualiza os dados de um fornecedor existente.
        
        Args:
            fornecedor_id (int): ID do fornecedor a ser atualizado
            dados (dict): Dicionário com os campos a serem atualizados
            
        Returns:
            bool: True se atualizado com sucesso, False caso contrário
        """
        try:
            conn = self.obter_conexao_empresa()
            if not conn:
                return False
                
            cursor = conn.cursor()
            campos_permitidos = [
                'razao_social', 'nome_fantasia', 'cnpj', 'inscricao_estadual',
                'endereco', 'cidade', 'estado', 'cep', 'telefone', 'email',
                'contato_nome', 'prazo_entrega', 'condicao_pagamento', 'status'
            ]
            
            updates = [f"{campo} = ?" for campo in dados.keys() 
                      if campo in campos_permitidos]
            valores = [dados[campo] for campo in dados.keys() 
                      if campo in campos_permitidos]
            
            if not updates:
                return False
                
            query = f"""
                UPDATE fornecedores
                SET {', '.join(updates)}
                WHERE id = ?
            """
            valores.append(fornecedor_id)
            
            cursor.execute(query, valores)
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            self.exibir_mensagem_erro("Erro ao atualizar fornecedor", str(e))
            return False

    def excluir_fornecedor(self, fornecedor_id):
        """Exclui um fornecedor do sistema (exclusão lógica).
        
        Args:
            fornecedor_id (int): ID do fornecedor a ser excluído
            
        Returns:
            bool: True se excluído com sucesso, False caso contrário
        """
        try:
            conn = self.obter_conexao_empresa()
            if not conn:
                return False
                
            cursor = conn.cursor()
            # Verifica se existem produtos vinculados ao fornecedor
            cursor.execute("""
                SELECT COUNT(*) FROM produtos
                WHERE fornecedor = ?
            """, (fornecedor_id,))
            
            if cursor.fetchone()[0] > 0:
                self.exibir_mensagem_erro(
                    "Erro",
                    "Não é possível excluir o fornecedor pois existem produtos vinculados"
                )
                conn.close()
                return False
            
            # Realiza exclusão lógica
            cursor.execute("""
                UPDATE fornecedores
                SET status = 'inativo'
                WHERE id = ?
            """, (fornecedor_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            self.exibir_mensagem_erro("Erro ao excluir fornecedor", str(e))
            return False

    # Métodos para gerenciamento de produtos
    def criar_produto(self, codigo_barras, sku, nome, descricao, categoria, marca,
                     quantidade, quantidade_minima, preco_custo, preco_venda,
                     localizacao, fornecedor):
        """Cria um novo produto no sistema.
        
        Args:
            codigo_barras (str): Código de barras do produto
            sku (str): SKU (Stock Keeping Unit) do produto
            nome (str): Nome do produto
            descricao (str): Descrição detalhada do produto
            categoria (str): Categoria do produto
            marca (str): Marca do produto
            quantidade (int): Quantidade inicial em estoque
            quantidade_minima (int): Quantidade mínima para alerta de estoque
            preco_custo (float): Preço de custo do produto
            preco_venda (float): Preço de venda do produto
            localizacao (str): Localização no depósito
            fornecedor (str): Fornecedor do produto
            
        Returns:
            int: ID do produto criado ou None em caso de erro
        """
        try:
            conn = self.obter_conexao_empresa()
            if not conn:
                self.exibir_mensagem_erro("Erro", "Empresa não está logada")
                return None
                
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO produtos (
                    codigo_barras, sku, nome, descricao, categoria, marca,
                    quantidade, quantidade_minima, preco_custo, preco_venda,
                    localizacao, fornecedor
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (codigo_barras, sku, nome, descricao, categoria, marca,
                  quantidade, quantidade_minima, preco_custo, preco_venda,
                  localizacao, fornecedor))
            
            produto_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return produto_id
            
        except sqlite3.Error as e:
            self.exibir_mensagem_erro("Erro ao criar produto", str(e))
            return None

    def obter_produto(self, produto_id):
        """Obtém os dados de um produto específico.
        
        Args:
            produto_id (int): ID do produto a ser consultado
            
        Returns:
            dict: Dicionário com os dados do produto ou None se não encontrado
        """
        try:
            conn = self.obter_conexao_empresa()
            if not conn:
                return None
                
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, codigo_barras, sku, nome, descricao, categoria, marca,
                       quantidade, quantidade_minima, preco_custo, preco_venda,
                       localizacao, fornecedor, data_cadastro, ultima_atualizacao
                FROM produtos
                WHERE id = ?
            """, (produto_id,))
            
            produto = cursor.fetchone()
            conn.close()
            
            if produto:
                return {
                    'id': produto[0],
                    'codigo_barras': produto[1],
                    'sku': produto[2],
                    'nome': produto[3],
                    'descricao': produto[4],
                    'categoria': produto[5],
                    'marca': produto[6],
                    'quantidade': produto[7],
                    'quantidade_minima': produto[8],
                    'preco_custo': produto[9],
                    'preco_venda': produto[10],
                    'localizacao': produto[11],
                    'fornecedor': produto[12],
                    'data_cadastro': produto[13],
                    'ultima_atualizacao': produto[14]
                }
            return None
            
        except sqlite3.Error as e:
            self.exibir_mensagem_erro("Erro ao consultar produto", str(e))
            return None

    def listar_produtos(self, filtro=None):
        """Lista todos os produtos cadastrados com opção de filtro.
        
        Args:
            filtro (dict, optional): Dicionário com filtros a serem aplicados
            
        Returns:
            list: Lista de dicionários com dados dos produtos
        """
        try:
            conn = self.obter_conexao_empresa()
            if not conn:
                return []
                
            cursor = conn.cursor()
            query = """
                SELECT id, codigo_barras, sku, nome, descricao, categoria, marca,
                       quantidade, quantidade_minima, preco_custo, preco_venda,
                       localizacao, fornecedor, data_cadastro, ultima_atualizacao
                FROM produtos
                WHERE 1=1
            """
            
            params = []
            if filtro:
                if 'categoria' in filtro:
                    query += " AND categoria = ?"
                    params.append(filtro['categoria'])
                if 'marca' in filtro:
                    query += " AND marca = ?"
                    params.append(filtro['marca'])
                if 'fornecedor' in filtro:
                    query += " AND fornecedor = ?"
                    params.append(filtro['fornecedor'])
                if 'estoque_baixo' in filtro and filtro['estoque_baixo']:
                    query += " AND quantidade <= quantidade_minima"
            
            cursor.execute(query, params)
            produtos = cursor.fetchall()
            conn.close()
            
            return [{
                'id': p[0],
                'codigo_barras': p[1],
                'sku': p[2],
                'nome': p[3],
                'descricao': p[4],
                'categoria': p[5],
                'marca': p[6],
                'quantidade': p[7],
                'quantidade_minima': p[8],
                'preco_custo': p[9],
                'preco_venda': p[10],
                'localizacao': p[11],
                'fornecedor': p[12],
                'data_cadastro': p[13],
                'ultima_atualizacao': p[14]
            } for p in produtos]
            
        except sqlite3.Error as e:
            self.exibir_mensagem_erro("Erro ao listar produtos", str(e))
            return []

    def atualizar_produto(self, produto_id, dados):
        """Atualiza os dados de um produto existente.
        
        Args:
            produto_id (int): ID do produto a ser atualizado
            dados (dict): Dicionário com os campos a serem atualizados
            
        Returns:
            bool: True se atualizado com sucesso, False caso contrário
        """
        try:
            conn = self.obter_conexao_empresa()
            if not conn:
                return False
                
            cursor = conn.cursor()
            campos_permitidos = [
                'codigo_barras', 'sku', 'nome', 'descricao', 'categoria', 'marca',
                'quantidade', 'quantidade_minima', 'preco_custo', 'preco_venda',
                'localizacao', 'fornecedor'
            ]
            
            updates = [f"{campo} = ?" for campo in dados.keys() 
                      if campo in campos_permitidos]
            valores = [dados[campo] for campo in dados.keys() 
                      if campo in campos_permitidos]
            
            if not updates:
                return False
                
            # Adiciona atualização do campo ultima_atualizacao
            updates.append("ultima_atualizacao = CURRENT_TIMESTAMP")
            
            query = f"""
                UPDATE produtos
                SET {', '.join(updates)}
                WHERE id = ?
            """
            valores.append(produto_id)
            
            cursor.execute(query, valores)
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            self.exibir_mensagem_erro("Erro ao atualizar produto", str(e))
            return False

    def excluir_produto(self, produto_id):
        """Exclui um produto do sistema.
        
        Args:
            produto_id (int): ID do produto a ser excluído
            
        Returns:
            bool: True se excluído com sucesso, False caso contrário
        """
        try:
            conn = self.obter_conexao_empresa()
            if not conn:
                return False
                
            cursor = conn.cursor()
            # Verifica se existem movimentações para o produto
            cursor.execute("""
                SELECT COUNT(*) FROM movimentacoes_estoque
                WHERE produto_id = ?
            """, (produto_id,))
            
            if cursor.fetchone()[0] > 0:
                self.exibir_mensagem_erro(
                    "Erro",
                    "Não é possível excluir o produto pois existem movimentações registradas"
                )
                conn.close()
                return False
            
            # Verifica se o produto está em algum pedido
            cursor.execute("""
                SELECT COUNT(*) FROM itens_pedido
                WHERE produto_id = ?
            """, (produto_id,))
            
            if cursor.fetchone()[0] > 0:
                self.exibir_mensagem_erro(
                    "Erro",
                    "Não é possível excluir o produto pois ele está vinculado a pedidos"
                )
                conn.close()
                return False
            
            # Remove o produto
            cursor.execute("""
                DELETE FROM produtos
                WHERE id = ?
            """, (produto_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            self.exibir_mensagem_erro("Erro ao excluir produto", str(e))
            return False

    def configurar_estilos(self):
        """Configura os estilos do Tkinter usando ttk.Style."""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Paleta de cores moderna e vibrante já definida no __init__
        
        # Configuração do tema geral
        self.root.configure(background=self.cores["fundo"])
        
        # Estilo para mensagens
        self.style.configure("Sucesso.TLabel", foreground=self.cores["sucesso"], font=("Segoe UI", 10, "bold"))
        self.style.configure("Alerta.TLabel", foreground=self.cores["alerta"], font=("Segoe UI", 10, "bold"))
        
        # Estilo para efeito de foco nos campos
        self.style.configure("FocusIn.TEntry", fieldbackground="#E3F2FD", bordercolor=self.cores["primaria"], borderwidth=2)
        
        # Cabeçalho
        self.style.configure(
            "Cabecalho.TFrame", 
            background=self.cores["primaria"],
            relief="raised",
            borderwidth=1
        )
        self.style.configure(
            "Cabecalho.TLabel",
            font=("Segoe UI", 18, "bold"),
            foreground=self.cores["texto_claro"],
            background=self.cores["primaria"],
            padding=(15, 10),
        )
        
        # Labels
        self.style.configure(
            "TLabel",
            background=self.cores["fundo"],
            foreground=self.cores["texto"],
            font=("Segoe UI", 10),
            padding=3
        )
        self.style.configure(
            "Titulo.TLabel", 
            font=("Segoe UI", 18, "bold"), 
            foreground=self.cores["primaria"],
            background=self.cores["fundo"],
            padding=(0, 10)
        )
        self.style.configure(
            "Subtitulo.TLabel", 
            font=("Segoe UI", 14, "bold"), 
            foreground=self.cores["primaria_escura"],
            background=self.cores["fundo"],
            padding=(0, 5)
        )
        
        # Botões
        self.style.configure(
            "TButton", 
            font=("Segoe UI", 10),
            padding=8,
            relief="raised",
            borderwidth=1
        )
        self.style.map(
            "TButton",
            foreground=[("active", self.cores["texto_claro"]), ("!disabled", self.cores["texto_claro"])],
            background=[
                ("active", self.cores["primaria_escura"]),
                ("!disabled", self.cores["primaria"]),
            ],
            relief=[("pressed", "sunken"), ("!pressed", "raised")]
        )
        
        # Adicionar efeito de hover nos botões
        self.root.bind_class("TButton", "<Enter>", lambda e: e.widget.configure(cursor="hand2"))
        self.root.bind_class("TButton", "<Leave>", lambda e: e.widget.configure(cursor=""))
        
        # Botão de destaque
        self.style.configure(
            "Destaque.TButton", 
            font=("Segoe UI", 10, "bold"),
            padding=8
        )
        self.style.map(
            "Destaque.TButton",
            foreground=[("active", self.cores["texto_claro"]), ("!disabled", self.cores["texto_claro"])],
            background=[
                ("active", "#E64A19"),  # Laranja mais escuro
                ("!disabled", self.cores["destaque"]),
            ]
        )
        
        # Campos de entrada
        self.style.configure(
            "TEntry", 
            fieldbackground="white", 
            font=("Segoe UI", 10),
            borderwidth=1,
            relief="solid",
            padding=5
        )
        
        # Combobox personalizado
        self.style.configure(
            "TCombobox",
            fieldbackground="white",
            background=self.cores["primaria"],
            foreground=self.cores["texto"],
            arrowcolor=self.cores["primaria"],
            font=("Segoe UI", 10),
            padding=5
        )
        self.style.map(
            "TCombobox",
            fieldbackground=[("readonly", "white")],
            selectbackground=[("readonly", self.cores["primaria"])],
            selectforeground=[("readonly", self.cores["texto_claro"])]
        )
        
        # Cabeçalho de navegação
        self.style.configure(
            "Header.TFrame", 
            background=self.cores["fundo_alt"], 
            padding=8,
            relief="flat",
            borderwidth=0
        )
        self.style.configure(
            "Header.TButton", 
            font=("Segoe UI", 9), 
            width=12, 
            padding=6, 
            anchor="center"
        )
        self.style.map(
            "Header.TButton",
            foreground=[("active", self.cores["texto_claro"]), ("!disabled", self.cores["texto_claro"])],
            background=[
                ("active", self.cores["primaria_escura"]),
                ("!disabled", self.cores["primaria"]),
            ],
        )
        
        # Menu lateral
        self.style.configure(
            "Submenu.TFrame", 
            background=self.cores["fundo_alt"], 
            borderwidth=1, 
            relief="groove"
        )
        self.style.configure(
            "Submenu.TButton",
            font=("Segoe UI", 11),
            width=18,
            padding=10,
            anchor="w",
            background=self.cores["fundo_alt"],
            foreground=self.cores["texto"],
        )
        self.style.map(
            "Submenu.TButton",
            background=[
                ("active", self.cores["secundaria"]),
                ("!disabled", self.cores["fundo_alt"]),
            ],
            foreground=[
                ("active", self.cores["texto_claro"]),
                ("!disabled", self.cores["texto"]),
            ],
        )
        
        # Treeview (tabelas)
        self.style.configure(
            "Treeview", 
            background=self.cores["fundo"],
            fieldbackground=self.cores["fundo"],
            foreground=self.cores["texto"],
            font=("Segoe UI", 10),
            borderwidth=1,
            relief="solid",
            rowheight=25
        )
        self.style.configure(
            "Treeview.Heading",
            background=self.cores["primaria"],
            foreground=self.cores["texto_claro"],
            font=("Segoe UI", 10, "bold"),
            relief="raised",
            padding=5
        )
        self.style.map(
            "Treeview",
            background=[("selected", self.cores["secundaria"]), ("hover", self.cores["hover"])],
            foreground=[("selected", self.cores["texto_claro"])]
        )
        
        # Adicionar efeito de hover nas linhas da Treeview
        self.root.bind_class("Treeview", "<Motion>", self._treeview_motion)
        
    def _treeview_motion(self, event):
        """Implementa o efeito de hover nas linhas da Treeview."""
        tree = event.widget
        item = tree.identify_row(event.y)
        
        # Verifica se o cursor está sobre um item válido
        if item:
            # Obtém o item que tinha a tag 'hover' anteriormente
            hover_items = [i for i in tree.get_children() if 'hover' in tree.item(i, 'tags')]
            
            # Remove a tag 'hover' apenas do item anterior
            for i in hover_items:
                if i != item:  # Não remove do item atual se for o mesmo
                    tree.item(i, tags=())
            
            # Aplica a tag 'hover' apenas ao item atual se ainda não tiver
            current_tags = tree.item(item, 'tags')
            if 'hover' not in current_tags:
                tree.item(item, tags=('hover',))
        
        # Scrollbars personalizados
        self.style.configure(
            "TScrollbar",
            background=self.cores["fundo"],
            arrowcolor=self.cores["primaria"],
            bordercolor=self.cores["borda"],
            troughcolor=self.cores["fundo_alt"],
            relief="flat"
        )
        self.style.map(
            "TScrollbar",
            background=[("active", self.cores["primaria_escura"]), ("!disabled", self.cores["primaria"])]
        )

    def criar_header_acoes(self, container):
        """Cria a barra de navegação e ações (CRUD) no container fornecido.
        
        Este método cria dois frames com botões para navegação e operações CRUD.
        
        Args:
            container: O container onde o header será criado
        """
        nav_frame = ttk.Frame(container, style="Header.TFrame")
        nav_frame.pack(fill=tk.X, pady=2)

        botoes_nav = [
            ("⏮️ Primeiro", self.primeiro_registro),
            ("◀ Anterior", self.registro_anterior),
            ("Próximo ▶", self.proximo_registro),
            ("⏭️ Último", self.ultimo_registro),
            ("🔍 Pesquisar", self.pesquisar_registro),
            ("📂 Pesquisar Range", self.pesquisar_range),
        ]

        for texto, comando in botoes_nav:
            ttk.Button(
                nav_frame, text=texto, style="Header.TButton", command=comando
            ).pack(side=tk.LEFT, padx=2)

        crud_frame = ttk.Frame(container, style="Header.TFrame")
        crud_frame.pack(fill=tk.X, pady=2)

        botoes_crud = [
            ("➕ Criar", self.criar_registro),
            ("✏️ Atualizar", self.atualizar_registro),
            ("⎘ Copiar", self.copiar_registro),
            ("❌ Deletar", self.deletar_registro),
            ("💾 Salvar", self.salvar_usuario),  # Alterado para salvar usuário
            ("↩️ Reset", self.reset_edicao),
            ("🚫 Cancelar", self.cancelar_edicao),
        ]

        for texto, comando in botoes_crud:
            ttk.Button(
                crud_frame, text=texto, style="Header.TButton", command=comando
            ).pack(side=tk.LEFT, padx=2)
    
    def primeiro_registro(self):
        """Navega para o primeiro registro da lista atual.
        
        Esta função atualiza a visualização para mostrar o primeiro item
        da lista de registros atual, seja produtos, usuários ou outros.
        """
        # Implementação dependerá do contexto atual (produtos, usuários, etc.)
        self.exibir_mensagem_aviso("Navegação", "Primeiro registro selecionado")
        # Aqui seria implementada a lógica para selecionar o primeiro registro
        
    def registro_anterior(self):
        """Navega para o registro anterior ao atual na lista.
        
        Esta função atualiza a visualização para mostrar o item anterior
        ao atual na lista de registros.
        """
        # Implementação dependerá do contexto atual
        self.exibir_mensagem_aviso("Navegação", "Registro anterior selecionado")
        # Aqui seria implementada a lógica para selecionar o registro anterior
        
    def proximo_registro(self):
        """Navega para o próximo registro na lista atual.
        
        Esta função atualiza a visualização para mostrar o próximo item
        na lista de registros após o atual.
        """
        # Implementação dependerá do contexto atual
        self.exibir_mensagem_aviso("Navegação", "Próximo registro selecionado")
        # Aqui seria implementada a lógica para selecionar o próximo registro
        
    def ultimo_registro(self):
        """Navega para o último registro da lista atual.
        
        Esta função atualiza a visualização para mostrar o último item
        da lista de registros atual.
        """
        # Implementação dependerá do contexto atual
        self.exibir_mensagem_aviso("Navegação", "Último registro selecionado")
        # Aqui seria implementada a lógica para selecionar o último registro
        
    def pesquisar_registro(self):
        """Abre uma interface para pesquisar registros específicos.
        
        Esta função exibe um diálogo que permite ao usuário inserir critérios
        de pesquisa para encontrar registros específicos no sistema.
        """
        # Implementação de uma janela de pesquisa
        self.exibir_mensagem_aviso("Pesquisa", "Função de pesquisa acionada")
        # Aqui seria implementada a lógica para abrir uma janela de pesquisa
        
    def pesquisar_range(self):
        """Abre uma interface para pesquisar registros dentro de um intervalo.
        
        Esta função exibe um diálogo que permite ao usuário definir um intervalo
        de valores para filtrar registros no sistema.
        """
        # Implementação de uma janela de pesquisa por intervalo
        self.exibir_mensagem_aviso("Pesquisa por Intervalo", "Função de pesquisa por intervalo acionada")
        # Aqui seria implementada a lógica para abrir uma janela de pesquisa por intervalo
        
    def criar_registro(self):
        """Prepara a interface para a criação de um novo registro.
        
        Esta função limpa os campos de entrada e prepara a interface
        para que o usuário possa inserir dados para um novo registro.
        """
        # Implementação para preparar a criação de um novo registro
        self.exibir_mensagem_aviso("Criar", "Modo de criação de registro ativado")
        # Aqui seria implementada a lógica para preparar a criação de um novo registro
        
    def atualizar_registro(self):
        """Prepara a interface para a atualização do registro atual.
        
        Esta função habilita a edição dos campos para que o usuário
        possa modificar os dados do registro atualmente selecionado.
        """
        # Implementação para habilitar a edição do registro atual
        self.exibir_mensagem_aviso("Atualizar", "Modo de atualização de registro ativado")
        # Aqui seria implementada a lógica para habilitar a edição do registro atual
        
    def copiar_registro(self):
        """Cria uma cópia do registro atual para edição.
        
        Esta função duplica o registro atual e prepara a interface
        para que o usuário possa editar a cópia antes de salvá-la.
        """
        # Implementação para copiar o registro atual
        self.exibir_mensagem_aviso("Copiar", "Registro atual copiado para edição")
        # Aqui seria implementada a lógica para copiar o registro atual
        
    def deletar_registro(self):
        """Remove o registro atual do sistema após confirmação.
        
        Esta função exibe um diálogo de confirmação e, se confirmado,
        remove o registro atual do banco de dados.
        """
        # Implementação para deletar o registro atual com confirmação
        confirmacao = messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir este registro?")
        if confirmacao:
            self.exibir_mensagem_aviso("Deletar", "Registro excluído com sucesso")
            # Aqui seria implementada a lógica para deletar o registro atual
        
    def salvar_usuario(self):
        """Salva os dados do usuário atual no banco de dados.
        
        Esta função valida os dados inseridos e, se válidos,
        salva o usuário atual no banco de dados da empresa.
        """
        # Implementação para salvar o usuário atual
        self.exibir_mensagem_aviso("Salvar", "Usuário salvo com sucesso")
        # Aqui seria implementada a lógica para salvar o usuário atual
        
    def reset_edicao(self):
        """Redefine os campos de edição para seus valores originais.
        
        Esta função descarta as alterações não salvas e restaura
        os campos para os valores originais do registro.
        """
        # Implementação para resetar os campos de edição
        self.exibir_mensagem_aviso("Reset", "Campos redefinidos para valores originais")
        # Aqui seria implementada a lógica para resetar os campos de edição
        
    def cancelar_edicao(self):
        """Cancela a edição atual e retorna à visualização anterior.
        
        Esta função descarta as alterações não salvas e retorna
        à visualização anterior ou fecha a janela de edição.
        """
        # Implementação para cancelar a edição atual
        self.exibir_mensagem_aviso("Cancelar", "Edição cancelada")
        # Aqui seria implementada a lógica para cancelar a edição atual
        
    def criar_botoes_navegacao(self, container):
        """Cria os botões de navegação principal no cabeçalho do sistema.
        
        Esta função adiciona botões para navegação entre os diferentes módulos
        do sistema, configurações e logout.
        
        Args:
            container: O container onde os botões serão criados
        """
        # Estilo para botões do cabeçalho
        estilo_botao = {
            "background": self.style.lookup("Cabecalho.TFrame", "background"),
            "foreground": "#FFFFFF",
            "font": ("Segoe UI", 10, "bold"),
            "borderwidth": 0,
            "highlightthickness": 0,
            "activebackground": self.style.lookup("Cabecalho.TFrame", "background"),
            "activeforeground": "#FFFFFF",
            "padx": 10,
            "pady": 5
        }
        
        # Botões de navegação principal
        botoes = [
            ("🏠 Início", self.navegar_para_inicio),
            ("📦 Produtos", self.navegar_para_produtos),
            ("👥 Usuários", self.navegar_para_usuarios),
            ("🏭 Depósitos", self.navegar_para_depositos),
            ("🔧 Configurações", self.abrir_configuracoes),
            ("🚪 Logout", self.realizar_logout)
        ]
        
        for texto, comando in botoes:
            btn = tk.Button(container, text=texto, command=comando, **estilo_botao)
            btn.pack(side=tk.LEFT, padx=5)
            
            # Adicionar efeito hover
            btn.bind("<Enter>", lambda e, b=btn: self.botao_hover_enter(b))
            btn.bind("<Leave>", lambda e, b=btn: self.botao_hover_leave(b))
    
    def botao_hover_enter(self, botao):
        """Aplica efeito visual quando o mouse passa sobre o botão.
        
        Args:
            botao: O botão que receberá o efeito
        """
        botao.config(background="#1565C0")  # Cor mais escura ao passar o mouse
    
    def botao_hover_leave(self, botao):
        """Remove o efeito visual quando o mouse sai do botão.
        
        Args:
            botao: O botão que terá o efeito removido
        """
        botao.config(background=self.style.lookup("Cabecalho.TFrame", "background"))
    
    def navegar_para_inicio(self):
        """Navega para a tela inicial do sistema.
        
        Esta função carrega a tela principal do sistema com o dashboard
        e informações resumidas.
        """
        self.exibir_mensagem_aviso("Navegação", "Navegando para a tela inicial")
        # Implementação da navegação para a tela inicial
        # self.carregar_tela_inicial()
    
    def navegar_para_produtos(self):
        """Navega para o módulo de gerenciamento de produtos.
        
        Esta função carrega a interface de gerenciamento de produtos,
        permitindo visualizar, adicionar, editar e excluir produtos.
        """
        self.exibir_mensagem_aviso("Navegação", "Navegando para o módulo de produtos")
        # Implementação da navegação para o módulo de produtos
        # self.carregar_modulo_produtos()
    
    def navegar_para_usuarios(self):
        """Navega para o módulo de gerenciamento de usuários.
        
        Esta função carrega a interface de gerenciamento de usuários,
        permitindo visualizar, adicionar, editar e excluir usuários.
        """
        self.exibir_mensagem_aviso("Navegação", "Navegando para o módulo de usuários")
        # Implementação da navegação para o módulo de usuários
        # self.carregar_modulo_usuarios()
    
    def navegar_para_depositos(self):
        """Navega para o módulo de gerenciamento de depósitos.
        
        Esta função carrega a interface de gerenciamento de depósitos,
        permitindo visualizar, adicionar, editar e excluir depósitos.
        """
        self.exibir_mensagem_aviso("Navegação", "Navegando para o módulo de depósitos")
        # Implementação da navegação para o módulo de depósitos
        # self.carregar_modulo_depositos()
    
    def abrir_configuracoes(self):
        """Abre a tela de configurações do sistema.
        
        Esta função carrega a interface de configurações, permitindo
        ao usuário personalizar diversos aspectos do sistema.
        """
        self.exibir_mensagem_aviso("Configurações", "Abrindo configurações do sistema")
        # Implementação para abrir a tela de configurações
        # self.abrir_tela_configuracoes()
    
    def realizar_logout(self):
        """Realiza o logout do usuário atual.
        
        Esta função encerra a sessão do usuário atual, fecha todas as janelas
        abertas e retorna para a tela de login.
        """
        confirmacao = messagebox.askyesno("Confirmar Logout", "Tem certeza que deseja sair do sistema?")
        if confirmacao:
            # Limpar dados da sessão atual
            self.empresa_logada = None
            
            # Fechar todas as janelas abertas exceto a principal
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Voltar para a tela de login
            self.tela_login()
            
            self.exibir_mensagem_aviso("Logout", "Logout realizado com sucesso")


    def tela_login(self):
        """Exibe a tela de login do sistema."""
        for widget in self.root.winfo_children():
            widget.destroy()

        # Configurar o fundo da janela principal
        self.root.configure(background=self.style.lookup("TFrame", "background"))

        # Frame principal com efeito de sombra
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Container com borda arredondada (simulada com padding e cor de fundo)
        container = ttk.Frame(main_frame, style="Submenu.TFrame")
        container.pack(expand=True, padx=50, pady=50, ipadx=30, ipady=30)

        # Título com ícone
        titulo_frame = ttk.Frame(container, style="Submenu.TFrame")
        titulo_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Tentar carregar um ícone de depósito se existir
        try:
            if os.path.exists("icons/empresa.png"):
                logo = Image.open("icons/empresa.png")
                logo = logo.resize((64, 64), Image.LANCZOS)
                logo_tk = ImageTk.PhotoImage(logo)
                logo_label = ttk.Label(titulo_frame, image=logo_tk, background=self.style.lookup("Submenu.TFrame", "background"))
                logo_label.image = logo_tk
                logo_label.pack(side=tk.TOP, pady=10)
        except Exception as e:
            print(f"Erro ao carregar ícone: {e}")

        ttk.Label(
            titulo_frame, text="Sistema de Gerenciamento de Depósito", style="Titulo.TLabel", background=self.style.lookup("Submenu.TFrame", "background")
        ).pack(pady=5)
        
        ttk.Label(
            titulo_frame, text="Acesso Empresarial", style="Subtitulo.TLabel", background=self.style.lookup("Submenu.TFrame", "background")
        ).pack(pady=5)

        # Linha separadora
        separator = ttk.Separator(container, orient="horizontal")
        separator.pack(fill=tk.X, padx=20, pady=10)

        # Formulário com visual melhorado
        form_frame = ttk.Frame(container, style="Submenu.TFrame")
        form_frame.pack(pady=20, padx=30, fill=tk.X)

        # Label com ícone (simulado com emoji)
        ttk.Label(form_frame, text="🏢 Nome da Empresa:", background=self.style.lookup("Submenu.TFrame", "background")).grid(
            row=0, column=0, padx=10, pady=10, sticky="e"
        )

        entry_frame = ttk.Frame(form_frame, style="Submenu.TFrame")
        entry_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.entry_nome = ttk.Entry(entry_frame, width=30)
        self.entry_nome.pack(fill=tk.X)

        # Listbox com estilo melhorado
        self.listbox = tk.Listbox(
            entry_frame,
            height=4,
            bg="white",
            fg=self.style.lookup("TLabel", "foreground"),
            font=("Segoe UI", 10),
            selectbackground=self.style.lookup("TButton", "background"),
            selectforeground="white",
            borderwidth=1,
            relief="solid"
        )
        self.listbox.pack(fill=tk.X)
        self.listbox.pack_forget()

        # Carrega empresas cadastradas
        conn = sqlite3.connect("deposito_principal.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM empresas")
        empresas = cursor.fetchall()
        self.lista_empresas = [empresa[0] for empresa in empresas]
        conn.close()

        self.entry_nome.bind("<KeyRelease>", self.atualizar_sugestoes)
        self.listbox.bind("<<ListboxSelect>>", self.selecionar_empresa)
        self.entry_nome.bind("<FocusOut>", lambda e: self.verificar_foco())
        self.listbox.bind("<FocusOut>", lambda e: self.verificar_foco())

        ttk.Label(form_frame, text="👤 Usuário:", background=self.style.lookup("Submenu.TFrame", "background")).grid(
            row=1, column=0, padx=10, pady=10, sticky="e"
        )
        self.entry_admin = ttk.Entry(form_frame, width=30)
        self.entry_admin.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(form_frame, text="🔒 Senha:", background=self.style.lookup("Submenu.TFrame", "background")).grid(
            row=2, column=0, padx=10, pady=10, sticky="e"
        )
        self.entry_senha = ttk.Entry(form_frame, show="•", width=30)
        self.entry_senha.grid(row=2, column=1, padx=10, pady=10)
        
        # Adicionar efeito de foco nos campos
        def on_entry_focus_in(event):
            event.widget.configure(style="FocusIn.TEntry")
        
        def on_entry_focus_out(event):
            event.widget.configure(style="TEntry")
        
        # Estilo para entrada com foco
        self.style.configure(
            "FocusIn.TEntry",
            fieldbackground="#E1F5FE",
            borderwidth=2,
            relief="solid"
        )
        
        # Aplicar efeito de foco aos campos
        self.entry_nome.bind("<FocusIn>", on_entry_focus_in)
        self.entry_nome.bind("<FocusOut>", on_entry_focus_out)
        self.entry_senha.bind("<FocusIn>", on_entry_focus_in)
        self.entry_senha.bind("<FocusOut>", on_entry_focus_out)
        
        # Adicionar evento de tecla Enter para acionar o botão de login
        def verificar_enter_login(event):
            if self.entry_nome.get() and self.entry_senha.get() and self.entry_admin.get():
                self.fazer_login()
        
        self.entry_nome.bind("<Return>", verificar_enter_login)
        self.entry_admin.bind("<Return>", verificar_enter_login)
        self.entry_senha.bind("<Return>", verificar_enter_login)

        # Linha separadora antes dos botões
        separator_frame = ttk.Frame(form_frame)
        separator_frame.grid(row=3, column=0, columnspan=2, pady=10)
        separator = ttk.Separator(separator_frame, orient="horizontal")
        separator.pack(fill=tk.X, padx=20, pady=5)
        
        # Aplicar efeito de foco ao campo de usuário
        self.entry_admin.bind("<FocusIn>", on_entry_focus_in)
        self.entry_admin.bind("<FocusOut>", on_entry_focus_out)
        
        # Frame para botões com espaçamento melhorado
        btn_frame = ttk.Frame(form_frame, style="Submenu.TFrame")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)

        # Botão de login com estilo de destaque
        login_btn = ttk.Button(btn_frame, text="✓ Entrar", command=self.fazer_login, style="Destaque.TButton")
        login_btn.pack(side=tk.LEFT, padx=10, ipadx=10)
        
        # Botão de cadastro com estilo normal
        cadastro_btn = ttk.Button(btn_frame, text="➕ Cadastrar Empresa", command=self.tela_cadastro_empresa)
        cadastro_btn.pack(side=tk.LEFT, padx=10, ipadx=10)
        
        # Botão de sair
        sair_btn = ttk.Button(btn_frame, text="🚪 Sair", command=self.root.quit)
        sair_btn.pack(side=tk.LEFT, padx=10, ipadx=10)
        
        # Adicionar mensagem de status na parte inferior
        status_frame = ttk.Frame(container, style="Submenu.TFrame")
        status_frame.pack(fill=tk.X, pady=(15, 0), side=tk.BOTTOM)
        
        status_label = ttk.Label(
            status_frame, 
            text="Sistema de Gerenciamento de Depósito v1.4", 
            anchor="center",
            background=self.style.lookup("Submenu.TFrame", "background"),
            foreground="#757575",
            font=("Segoe UI", 8)
        )
        status_label.pack(fill=tk.X)

    def atualizar_sugestoes(self, event):
        """Atualiza as sugestões conforme o usuário digita o nome da empresa."""
        texto = self.entry_nome.get().lower()
        if texto:
            sugestoes = [
                empresa
                for empresa in self.lista_empresas
                if empresa.lower().startswith(texto)
            ]
            self.listbox.delete(0, tk.END)
            for empresa in sugestoes:
                self.listbox.insert(tk.END, empresa)
            self.listbox.pack() if sugestoes else self.listbox.pack_forget()
        else:
            self.listbox.pack_forget()

    def selecionar_empresa(self, event):
        """Seleciona a empresa da listbox e preenche a entrada de nome."""
        if selecao := self.listbox.curselection():
            empresa_selecionada = self.listbox.get(selecao[0])
            self.entry_nome.delete(0, tk.END)
            self.entry_nome.insert(0, empresa_selecionada)
            self.listbox.pack_forget()
            self.entry_admin.focus()

    def verificar_foco(self):
        """Verifica o foco dos widgets para esconder a listbox quando necessário."""
        if self.root.focus_get() not in (self.entry_nome, self.listbox):
            self.listbox.pack_forget()

    def tela_cadastro_empresa(self):
        """Exibe a tela de cadastro de empresa."""
        for widget in self.root.winfo_children():
            widget.destroy()

        # Configurar o fundo da janela principal
        self.root.configure(background=self.style.lookup("TFrame", "background"))

        # Frame principal com efeito de sombra
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Container com borda arredondada (simulada com padding e cor de fundo)
        container = ttk.Frame(main_frame, style="Submenu.TFrame")
        container.pack(expand=True, padx=50, pady=50, ipadx=30, ipady=30)

        # Título com ícone
        titulo_frame = ttk.Frame(container, style="Submenu.TFrame")
        titulo_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Tentar carregar um ícone de empresa se existir
        try:
            if os.path.exists("icons/empresa.png"):
                logo = Image.open("icons/empresa.png")
                logo = logo.resize((64, 64), Image.LANCZOS)
                logo_tk = ImageTk.PhotoImage(logo)
                logo_label = ttk.Label(titulo_frame, image=logo_tk, background=self.style.lookup("Submenu.TFrame", "background"))
                logo_label.image = logo_tk
                logo_label.pack(side=tk.TOP, pady=10)
        except Exception as e:
            print(f"Erro ao carregar ícone: {e}")

        ttk.Label(
            titulo_frame, text="Cadastro de Empresa", style="Titulo.TLabel", background=self.style.lookup("Submenu.TFrame", "background")
        ).pack(pady=5)

        # Formulário com visual melhorado
        form_frame = ttk.Frame(container, style="Submenu.TFrame")
        form_frame.pack(pady=20, padx=30, fill=tk.X)

        # Campos de formulário com ícones
        ttk.Label(form_frame, text="🏢 Nome da Empresa:", background=self.style.lookup("Submenu.TFrame", "background")).grid(
            row=0, column=0, padx=10, pady=10, sticky="e"
        )
        self.entry_nome_cadastro = ttk.Entry(form_frame, width=30)
        self.entry_nome_cadastro.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(form_frame, text="👤 Usuário:", background=self.style.lookup("Submenu.TFrame", "background")).grid(
            row=1, column=0, padx=10, pady=10, sticky="e"
        )
        self.entry_admin_cadastro = ttk.Entry(form_frame, width=30)
        self.entry_admin_cadastro.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(form_frame, text="🔒 Senha:", background=self.style.lookup("Submenu.TFrame", "background")).grid(
            row=2, column=0, padx=10, pady=10, sticky="e"
        )
        self.entry_senha_cadastro = ttk.Entry(form_frame, show="•", width=30)
        self.entry_senha_cadastro.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(form_frame, text="🖼️ Logo da Empresa:", background=self.style.lookup("Submenu.TFrame", "background")).grid(
            row=3, column=0, padx=10, pady=10, sticky="e"
        )
        
        # Frame para o botão de logo e preview
        logo_frame = ttk.Frame(form_frame, style="Submenu.TFrame")
        logo_frame.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        self.btn_logo = ttk.Button(
            logo_frame, text="📂 Selecionar Arquivo", command=self.selecionar_logo
        )
        self.btn_logo.pack(side=tk.LEFT, padx=5)

        # Label para preview da logo com borda
        preview_frame = ttk.Frame(form_frame, style="Submenu.TFrame", borderwidth=1, relief="solid")
        preview_frame.grid(row=4, column=1, padx=10, pady=10, sticky="w")
        
        self.lbl_preview = ttk.Label(preview_frame, text="Prévia da logo", background=self.style.lookup("Submenu.TFrame", "background"))
        self.lbl_preview.pack(padx=10, pady=10)

        # Adicionar efeito de foco nos campos
        def on_entry_focus_in(event):
            event.widget.configure(style="FocusIn.TEntry")
        
        def on_entry_focus_out(event):
            event.widget.configure(style="TEntry")
        
        # Aplicar efeito de foco aos campos
        self.entry_nome_cadastro.bind("<FocusIn>", on_entry_focus_in)
        self.entry_nome_cadastro.bind("<FocusOut>", on_entry_focus_out)
        self.entry_senha_cadastro.bind("<FocusIn>", on_entry_focus_in)
        self.entry_senha_cadastro.bind("<FocusOut>", on_entry_focus_out)
        self.entry_admin_cadastro.bind("<FocusIn>", on_entry_focus_in)
        self.entry_admin_cadastro.bind("<FocusOut>", on_entry_focus_out)
        
        # Adicionar evento de tecla Enter para acionar o botão de cadastro
        def verificar_enter_cadastro(event):
            if self.entry_nome_cadastro.get() and self.entry_senha_cadastro.get() and self.entry_admin_cadastro.get():
                self.cadastrar_empresa()
        
        self.entry_nome_cadastro.bind("<Return>", verificar_enter_cadastro)
        self.entry_admin_cadastro.bind("<Return>", verificar_enter_cadastro)
        self.entry_senha_cadastro.bind("<Return>", verificar_enter_cadastro)

        # Botões diretamente no container principal para maior visibilidade
        botoes_frame = ttk.Frame(container, style="Submenu.TFrame")
        botoes_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        # Botão de cadastro com estilo de destaque
        cadastrar_btn = ttk.Button(
            botoes_frame, 
            text="✓ Cadastrar", 
            command=self.cadastrar_empresa, 
            style="Destaque.TButton",
            width=15
        )
        cadastrar_btn.pack(side=tk.LEFT, padx=(20, 10), pady=10, expand=True)
        
        # Botão de voltar
        voltar_btn = ttk.Button(
            botoes_frame, 
            text="↩️ Voltar", 
            command=self.tela_login,
            width=15
        )
        voltar_btn.pack(side=tk.RIGHT, padx=(10, 20), pady=10, expand=True)

    def cadastrar_empresa(self):
        """Processa o cadastro de uma nova empresa e cria o usuário CEO."""
        try:
            nome = self.entry_nome_cadastro.get().strip()
            senha = self.entry_senha_cadastro.get().strip()
            admin_user = self.entry_admin_cadastro.get().strip()

            # Validações básicas
            if not nome or not senha:
                self.exibir_mensagem_erro("Erro", "Nome da empresa e senha são obrigatórios!")
                return
                
            # Validação específica para o usuário administrador
            if not admin_user:
                self.exibir_mensagem_erro("Erro", "O nome do usuário administrador (dono) é obrigatório!")
                return

            # Gerar nome do banco de dados único
            db_nome = re.sub(r'[^a-zA-Z0-9]', '_', nome.lower())
            db_nome = f"{db_nome}_{hashlib.sha256(nome.encode()).hexdigest()[:6]}"

            # Conectar ao banco de dados principal
            conn = sqlite3.connect("deposito_principal.db")
            cursor = conn.cursor()

            # Hash da senha
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()

            # Processar logo se existir
            logo_final = None
            if hasattr(self, 'logo_path') and self.logo_path:
                nome_arquivo = f"logo_{db_nome}.{self.logo_path.split('.')[-1]}"
                caminho_final = os.path.join("logos", nome_arquivo)
                os.replace(self.logo_path, caminho_final)
                logo_final = caminho_final

            # Inserir empresa no banco de dados
            cursor.execute(
                "INSERT INTO empresas (nome, senha, logo_path, db_nome, admin_user) VALUES (?, ?, ?, ?, ?)",
                (nome, senha_hash, logo_final, db_nome, admin_user)
            )

            # Criar banco de dados específico da empresa
            self.criar_banco_empresa(db_nome)
            
            # Adicionar o usuário administrador (dono/CEO) no banco da empresa
            try:
                empresa_conn = sqlite3.connect(f"deposito_empresas/{db_nome}.db")
                empresa_cursor = empresa_conn.cursor()
                
                # Hash da senha para o usuário administrador
                admin_senha_hash = hashlib.sha256(senha.encode()).hexdigest()
                
                # Verificar se a tabela de usuários existe
                empresa_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
                if not empresa_cursor.fetchone():
                    # Se a tabela não existir, criar a tabela de usuários
                    empresa_cursor.execute(
                        """
                        CREATE TABLE usuarios (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            codigo_empresa TEXT NOT NULL,
                            empresa_nome TEXT NOT NULL,
                            usuario TEXT NOT NULL,
                            nome_completo TEXT NOT NULL,
                            nome_supervisor TEXT NOT NULL,
                            turno TEXT NOT NULL,
                            email TEXT UNIQUE NOT NULL,
                            senha TEXT NOT NULL,
                            tipo_acesso TEXT NOT NULL CHECK(tipo_acesso IN ('CEO', 'Administrador', 'Gerente', 'Operador')),
                            departamento TEXT,
                            cargo TEXT,
                            data_admissao DATE,
                            ultimo_acesso DATETIME,
                            criado_por TEXT
                        )
                        """
                    )
                
                # Inserir o usuário administrador com tipo_acesso 'CEO'
                empresa_cursor.execute(
                    """INSERT INTO usuarios (
                        codigo_empresa, empresa_nome, usuario, nome_completo, 
                        nome_supervisor, turno, email, senha, tipo_acesso,
                        departamento, cargo, data_admissao, criado_por,
                        ultimo_acesso
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, DATE('now'), ?, CURRENT_TIMESTAMP)""",
                    (db_nome, nome, admin_user, admin_user, "N/A", "Integral", 
                     f"{admin_user}@{nome.lower().replace(' ', '')}.com", admin_senha_hash, "CEO",
                     "Diretoria", "CEO", "SISTEMA", "SISTEMA")
                )
                empresa_conn.commit()
                empresa_conn.close()
            except Exception as e:
                self.exibir_mensagem_erro("Erro", f"Erro ao criar usuário administrador: {str(e)}")
                # Se houver erro na criação do usuário, tenta remover o banco de dados para evitar inconsistências
                try:
                    if os.path.exists(f"deposito_empresas/{db_nome}.db"):
                        os.remove(f"deposito_empresas/{db_nome}.db")
                except:
                    pass
                raise e

            conn.commit()
            self.exibir_mensagem_aviso("Sucesso", "Empresa cadastrada com sucesso!")
            self.tela_login()

        except sqlite3.IntegrityError:
            self.exibir_mensagem_erro("Erro", "Já existe uma empresa cadastrada com este nome!")
        except Exception as e:
            self.exibir_mensagem_erro("Erro", f"Erro ao cadastrar empresa: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def selecionar_logo(self):
        """Abre o diálogo para selecionar a logo da empresa e exibe o preview."""
        try:
            filetypes = [
                ("Imagens", "*.png"),
                ("Imagens", "*.jpg"),
                ("Imagens", "*.jpeg"),
                ("Todos arquivos", "*.*"),
            ]
            filepath = filedialog.askopenfilename(filetypes=filetypes)
            if not filepath:
                return

            # Carrega e redimensiona mantendo o aspect ratio
            img = Image.open(filepath)
            img.thumbnail((150, 150), Image.LANCZOS)
            self.preview_logo = ImageTk.PhotoImage(img)
            self.lbl_preview.config(image=self.preview_logo)
            self.btn_logo.config(text="✓ Logo Selecionado", style="Sucesso.TLabel")
            self.logo_path = filepath
            self.root.update_idletasks()
        except Exception as e:
            self.logo_path = None
            self.preview_logo = None
            self.lbl_preview.config(image="")
            self.btn_logo.config(text="Selecionar Logo")
            messagebox.showerror("Erro", f"Falha ao carregar imagem:\n{str(e)}")

    def cadastrar_empresa(self):
        """Realiza o cadastro da empresa, salvando logo, credenciais e criando banco de dados."""
        nome = self.entry_nome_cadastro.get().strip()
        senha = self.entry_senha_cadastro.get().strip()
        admin = self.entry_admin_cadastro.get().strip()
        
        # Validação de campos vazios
        if not nome or not senha or not admin:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
            
        # Validação de caracteres especiais no nome da empresa
        if not re.match(r'^[\w\s\-\.]+$', nome):
            messagebox.showerror("Erro", "O nome da empresa contém caracteres inválidos. Use apenas letras, números, espaços, hífens e pontos.")
            return
            
        # Validação de tamanho mínimo de senha
        if len(senha) < 6:
            messagebox.showerror("Erro", "A senha deve ter pelo menos 6 caracteres.")
            return

        try:
            db_nome = re.sub(r"\W+", "_", nome.lower())
            db_nome = f"{db_nome}_{hashlib.sha256(nome.encode()).hexdigest()[:6]}"
            
            # Verifica se já existe um banco de dados com esse nome e tenta removê-lo
            db_path = f"deposito_empresas/{db_nome}.db"
            if os.path.exists(db_path):
                try:
                    os.remove(db_path)
                except PermissionError:
                    messagebox.showerror("Erro", "O banco de dados está em uso. Feche todas as conexões e tente novamente.")
                    return
                except Exception as e:
                    messagebox.showerror("Erro", f"Não foi possível remover o banco de dados existente: {str(e)}")
                    return

            conn = None
            try:
                conn = sqlite3.connect("deposito_principal.db")
                cursor = conn.cursor()

                # Verificar se a empresa já existe antes de tentar inserir
                cursor.execute("SELECT id FROM empresas WHERE nome = ?", (nome,))
                if cursor.fetchone():
                    messagebox.showerror("Erro", "Empresa já cadastrada!")
                    return

                senha_hash = hashlib.sha256(senha.encode()).hexdigest()
                logo_final = None

                if self.logo_path:
                    try:
                        nome_arquivo = f"logo_{nome}.{self.logo_path.split('.')[-1]}"
                        caminho_final = os.path.join("logos", nome_arquivo)
                        os.replace(self.logo_path, caminho_final)
                        logo_final = caminho_final
                    except Exception as e:
                        messagebox.showwarning("Aviso", f"Não foi possível salvar o logo: {str(e)}. O cadastro continuará sem o logo.")

                cursor.execute(
                    "INSERT INTO empresas (nome, senha, logo_path, db_nome, admin_user) VALUES (?, ?, ?, ?, ?)",
                    (nome, senha_hash, logo_final, db_nome, admin),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Empresa já cadastrada!")
                return
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao cadastrar empresa: {str(e)}")
                return
            finally:
                if conn:
                    conn.close()

            # Tenta criar o banco da empresa após fechar a conexão principal
            for tentativa in range(3):  # Tenta 3 vezes
                try:
                    self.criar_banco_empresa(db_nome)
                    
                    # Criar o usuário administrador no banco da empresa
                    try:
                        empresa_conn = sqlite3.connect(f"deposito_empresas/{db_nome}.db")
                        empresa_cursor = empresa_conn.cursor()
                        
                        # Verificar se a tabela de usuários existe
                        empresa_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
                        if not empresa_cursor.fetchone():
                            messagebox.showerror("Erro", "Tabela de usuários não encontrada!")
                            return
                            
                        # Verificar se o usuário já existe
                        empresa_cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", (admin,))
                        if empresa_cursor.fetchone():
                            # Usuário já existe, não precisa criar novamente
                            pass
                        else:
                            # Criar o usuário administrador
                            admin_senha_hash = hashlib.sha256(senha.encode()).hexdigest()
                            empresa_cursor.execute(
                                """INSERT INTO usuarios (
                                    codigo_empresa, empresa_nome, usuario, nome_completo, 
                                    nome_supervisor, turno, email, senha, tipo_acesso,
                                    departamento, cargo, data_admissao, criado_por
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, DATE('now'), ?)""",
                                (db_nome, nome, admin, admin, "N/A", "Integral", 
                                 f"{admin}@{nome.lower().replace(' ', '')}.com", admin_senha_hash, "CEO",
                                 "Diretoria", "CEO", "SISTEMA")
                            )
                            empresa_conn.commit()
                    except Exception as e:
                        messagebox.showerror("Erro", f"Erro ao criar usuário administrador: {str(e)}")
                        return
                    finally:
                        if 'empresa_conn' in locals():
                            empresa_conn.close()
                    
                    messagebox.showinfo("Sucesso", "Empresa cadastrada com sucesso!")
                    self.tela_login()
                    return
                except PermissionError:
                    if tentativa < 2:  # Se não for a última tentativa
                        import time
                        time.sleep(1)  # Espera 1 segundo antes de tentar novamente
                    else:
                        messagebox.showerror("Erro", "Não foi possível criar o banco de dados da empresa. Tente novamente mais tarde.")
                        return
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao criar banco de dados da empresa: {str(e)}")
                    return

        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
            return

    def fazer_login(self):
        """Valida as credenciais e realiza o login da empresa.
        
        Este método é responsável por:
        - Validar as credenciais da empresa e do usuário
        - Verificar o nível de acesso do usuário (CEO, Administrador, Gerente, Operador)
        - Carregar as informações da empresa e do usuário logado
        - Redirecionar para o menu principal após autenticação bem-sucedida
        
        O processo de login segue estas etapas:
        1. Validação dos campos obrigatórios
        2. Verificação da existência da empresa
        3. Verificação do banco de dados específico da empresa
        4. Autenticação do usuário com suas credenciais
        5. Verificação do nível de acesso
        6. Carregamento das informações necessárias
        """
        nome = self.entry_nome.get().strip()
        senha = self.entry_senha.get().strip()
        usuario = self.entry_admin.get().strip()

        if not nome or not senha or not usuario:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return

        try:
            # Primeiro, verificar se a empresa existe
            conn = sqlite3.connect("deposito_principal.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM empresas WHERE nome = ?", (nome,))
            empresa = cursor.fetchone()
            
            if not empresa:
                messagebox.showerror("Erro", "Empresa não encontrada!")
                return
                
            # Verificar se o banco de dados da empresa existe
            db_path = f'deposito_empresas/{empresa["db_nome"]}.db'
            if not os.path.exists(db_path):
                messagebox.showerror("Erro", "Banco de dados da empresa não encontrado!")
                return
                
            # Agora verificar o usuário no banco da empresa
            empresa_conn = sqlite3.connect(db_path)
            empresa_conn.row_factory = sqlite3.Row
            empresa_cursor = empresa_conn.cursor()
            
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            
            # Primeiro verificar se o usuário existe - busca mais flexível
            empresa_cursor.execute(
                "SELECT * FROM usuarios WHERE usuario = ? OR nome_completo = ? OR email = ?",
                (usuario, usuario, usuario)
            )
            
            usuario_encontrado = empresa_cursor.fetchone()
            
            if not usuario_encontrado:
                # Verificar a estrutura da tabela para debug
                try:
                    empresa_cursor.execute("PRAGMA table_info(usuarios)")
                    colunas = empresa_cursor.fetchall()
                    colunas_nomes = [col[1] for col in colunas]
                    
                    if 'usuario' not in colunas_nomes:
                        messagebox.showerror("Erro", "Estrutura da tabela de usuários incorreta!")
                    else:
                        # Tentar buscar qualquer usuário para verificar se a tabela tem dados
                        empresa_cursor.execute("SELECT * FROM usuarios LIMIT 1")
                        qualquer_usuario = empresa_cursor.fetchone()
                        if not qualquer_usuario:
                            messagebox.showerror("Erro", "Nenhum usuário cadastrado para esta empresa!")
                        else:
                            messagebox.showerror("Erro", "Usuário não encontrado!")
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao verificar tabela de usuários: {str(e)}")
                
                empresa_conn.close()
                conn.close()
                return
                
            # Verificar se a senha está correta
            if usuario_encontrado["senha"] != senha_hash:
                messagebox.showerror("Erro", "Senha incorreta!")
                empresa_conn.close()
                conn.close()
                return
                
            # Verificar o tipo de acesso do usuário
            tipo_acesso = usuario_encontrado["tipo_acesso"].upper()
            if tipo_acesso not in ["CEO", "ADMINISTRADOR", "GERENTE", "OPERADOR"]:
                messagebox.showerror("Erro", "Tipo de acesso inválido!")
                empresa_conn.close()
                conn.close()
                return
                
            # Armazenar informações da empresa e do usuário logado
            self.empresa_logada = {
                "id": empresa["id"],
                "nome": empresa["nome"],
                "logo_path": empresa["logo_path"],
                "db_nome": empresa["db_nome"],
                "cnpj": empresa["cnpj"] if "cnpj" in empresa.keys() else "",
                "endereco": (empresa["endereco"] if "endereco" in empresa.keys() else ""),
                "telefone": (empresa["telefone"] if "telefone" in empresa.keys() else ""),
                "usuario": usuario_encontrado["usuario"],
                "tipo_acesso": usuario_encontrado["tipo_acesso"]
            }
            
            # Atualizar último acesso
            empresa_cursor.execute(
                "UPDATE usuarios SET ultimo_acesso = CURRENT_TIMESTAMP WHERE id = ?",
                (usuario_encontrado["id"],)
            )
            empresa_conn.commit()
            empresa_conn.close()
            conn.close()
            
            self.tela_menu()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro no login: {str(e)}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()

    def tela_menu(self):
        """Exibe a tela principal após o login da empresa."""
        for widget in self.root.winfo_children():
            widget.destroy()

        # Configurar o fundo da janela principal
        self.root.configure(background=self.style.lookup("TFrame", "background"))
        
        # Criar frame principal com padding
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Cabeçalho com visual moderno e efeito de elevação
        header = ttk.Frame(main_frame, style="Cabecalho.TFrame")
        header.pack(fill=tk.X, padx=5, pady=5)

        # Exibe logo da empresa se existir
        if self.empresa_logada["logo_path"] and os.path.exists(
            self.empresa_logada["logo_path"]
        ):
            try:
                logo = Image.open(self.empresa_logada["logo_path"])
                logo = logo.resize((200, 80), Image.LANCZOS)
                logo_tk = ImageTk.PhotoImage(logo)
                logo_label = ttk.Label(header, image=logo_tk)
                logo_label.image = logo_tk
                logo_label.pack(side=tk.LEFT, padx=10, pady=5)
            except Exception as e:
                print(f"Erro ao carregar logo: {e}")

        # Informações da empresa e do usuário logado
        info_frame = ttk.Frame(header, style="Cabecalho.TFrame")
        info_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(
            info_frame,
            text=f"Bem-vindo, {self.empresa_logada['nome']}",
            style="Cabecalho.TLabel",
        ).pack(side=tk.TOP, anchor="w")
        
        # Mostrar informações do usuário logado
        ttk.Label(
            info_frame,
            text=f"Usuário: {self.empresa_logada['usuario']} | Nível de acesso: {self.empresa_logada['tipo_acesso']}",
            foreground="#FFFFFF",
            background=self.style.lookup("Cabecalho.TFrame", "background"),
            font=("Segoe UI", 10)
        ).pack(side=tk.TOP, anchor="w", pady=(0, 5))
        
        # Adicionar botões de navegação no cabeçalho
        botoes_frame = ttk.Frame(header, style="Cabecalho.TFrame")
        botoes_frame.pack(side=tk.RIGHT, padx=10)
        
        # Botões de navegação principal
        self.criar_botoes_navegacao(botoes_frame)

        menu_container = ttk.Frame(main_frame)
        menu_container.pack(expand=True, fill=tk.BOTH, pady=20)

        # Menu lateral com visual aprimorado
        menu_lateral = ttk.Frame(menu_container, width=220, style="Submenu.TFrame")
        menu_lateral.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        # Título do menu
        menu_titulo = ttk.Label(
            menu_lateral, 
            text="Menu Principal", 
            style="Subtitulo.TLabel",
            background=self.style.lookup("Submenu.TFrame", "background"),
            anchor="center"
        )
        menu_titulo.pack(fill=tk.X, pady=10, padx=5)
        
        # Separador após o título
        ttk.Separator(menu_lateral, orient="horizontal").pack(fill=tk.X, padx=10, pady=5)

        # Frame para conteúdo principal
        self.conteudo_frame = ttk.Frame(menu_container)
        self.conteudo_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10)

        # Botões de menu com ícones e melhor espaçamento
        # Definir botões com base no nível de acesso do usuário
        botoes_menu = []
        
        # Todos os usuários podem ver produtos e relatórios
        botoes_menu.append(("📦 Produtos", self.tela_consulta_produtos))
        botoes_menu.append(("📊 Relatórios", self.tela_relatorio_estoque))
        
        # Apenas CEO e Administrador podem acessar cadastros
        if self.empresa_logada["tipo_acesso"] in ["CEO", "Administrador"]:
            botoes_menu.insert(0, ("👤 Cadastros", self.mostrar_submenu_cadastros))
        
        # Apenas CEO pode acessar configurações
        if self.empresa_logada["tipo_acesso"] == "CEO":
            botoes_menu.append(("⚙️ Configurações", self.tela_manutencao_empresa))
        
        # Todos podem sair
        botoes_menu.append(("🚪 Sair", self.tela_login))

        for texto, comando in botoes_menu:
            btn = ttk.Button(
                menu_lateral, text=texto, command=comando, style="Submenu.TButton"
            )
            btn.pack(pady=5, fill=tk.X)

    def mostrar_submenu_cadastros(self):
        """Exibe submenu para cadastros (usuários e dados da empresa)."""
        # Verificar permissões do usuário
        if self.empresa_logada["tipo_acesso"] not in ["CEO", "Administrador"]:
            messagebox.showerror("Acesso Negado", "Você não tem permissão para acessar esta funcionalidade.")
            return
            
        for widget in self.conteudo_frame.winfo_children():
            widget.destroy()

        submenu_frame = ttk.Frame(self.conteudo_frame, style="Submenu.TFrame")
        submenu_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(submenu_frame, text="Manutenção", style="Titulo.TLabel").pack(pady=10)

        btn_container = ttk.Frame(submenu_frame)
        btn_container.pack(pady=20)

        # Botão para cadastro de usuários
        self.criar_botao_com_imagem(
            container=btn_container,
            caminho_imagem="icons/user.png",
            texto_descricao="Cadastrar Usuários",
            comando=self.tela_manutencao_usuario,
        )

        ttk.Label(btn_container, text="").pack(pady=10)

        # Botão para manutenção dos dados da empresa
        self.criar_botao_com_imagem(
            container=btn_container,
            caminho_imagem="icons/empresa.png",
            texto_descricao="Dados da Empresa",
            comando=self.tela_manutencao_empresa,
        )

    def criar_botao_com_imagem(
        self, container, caminho_imagem, texto_descricao, comando
    ):
        """
        Cria um botão padronizado com imagem e texto.
        :param container: Frame onde o botão será inserido.
        :param caminho_imagem: Caminho para o arquivo da imagem.
        :param texto_descricao: Descrição exibida ao lado do botão.
        :param comando: Função de callback associada ao botão.
        """
        frame = ttk.Frame(container)
        frame.pack(pady=10, fill=tk.X)

        try:
            img = Image.open(caminho_imagem)
            img = img.resize((40, 40), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            btn = ttk.Button(frame, image=img_tk, command=comando)
            btn.image = img_tk  # Mantém referência da imagem
            btn.pack(side=tk.LEFT, padx=10)
            ttk.Label(frame, text=texto_descricao, font=("Arial", 10)).pack(
                side=tk.LEFT, padx=10
            )
        except Exception as e:
            print(f"Erro ao carregar imagem {caminho_imagem}: {e}")
            ttk.Button(
                frame,
                text="⚠️ Botão" if "user" in caminho_imagem else "🏢 Dados da Empresa",
                command=comando,
            ).pack(pady=10)

    def tela_manutencao_usuario(self):
        """Exibe a tela de cadastro de usuário em uma nova janela."""
        # Verificar permissões do usuário
        if self.empresa_logada["tipo_acesso"] not in ["CEO", "Administrador"]:
            messagebox.showerror("Acesso Negado", "Você não tem permissão para cadastrar usuários.")
            return
            
        if hasattr(self, "janela_usuario") and self.janela_usuario.winfo_exists():
            self.janela_usuario.lift()
            return

        self.janela_usuario = tk.Toplevel(self.root)
        self.janela_usuario.title("Cadastro de Usuário")
        self.janela_usuario.geometry("900x600")
        self.janela_usuario.protocol("WM_DELETE_WINDOW", self.fechar_janela_usuario)
        
        # Definir métodos de mensagem específicos para a janela de usuário
        def exibir_mensagem_aviso_usuario(titulo, mensagem):
            messagebox.showwarning(titulo, mensagem, parent=self.janela_usuario)
        
        def exibir_mensagem_erro_usuario(titulo, mensagem):
            messagebox.showerror(titulo, mensagem, parent=self.janela_usuario)
            
        self.exibir_mensagem_aviso_usuario = exibir_mensagem_aviso_usuario
        self.exibir_mensagem_erro_usuario = exibir_mensagem_erro_usuario

        main_container = ttk.Frame(self.janela_usuario)
        main_container.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=5)
        self.criar_header_usuario(header_frame)  # Header específico para usuários

        container = ttk.Frame(main_container)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(container, text="Cadastro de Usuário", style="Titulo.TLabel").pack(
            pady=10
        )

        form_frame = ttk.Frame(container)
        form_frame.pack(pady=10)

        campos = [
            ("Código Empresa:", "entry_cod_empresa"),
            (None, "lbl_nome_empresa"),  # Removido o texto "Nome da Empresa"
            ("Usuário:", "entry_usuario"),
            ("Nome Completo:", "entry_nome"),
            ("Nome Supervisor:", "entry_supervisor"),
            ("Turno:", "entry_turno"),
            ("Email:", "entry_email"),
            ("Senha:", "entry_senha"),
            ("Tipo Acesso:", "entry_tipo"),
        ]

        self.entries = {}
        for idx, (texto, var) in enumerate(campos):
            if texto:
                ttk.Label(form_frame, text=texto).grid(
                    row=idx, column=0, padx=5, pady=5, sticky="e"
                )

            if var == "lbl_nome_empresa":
                lbl = ttk.Label(form_frame, text="", foreground="#3498DB")
                lbl.grid(row=0, column=2, padx=5, pady=2, sticky="w")
                self.entries[var] = lbl
            else:
                entry = ttk.Entry(form_frame, width=30)
                if "Senha" in texto:
                    entry.config(show="*")
                entry.grid(row=idx, column=1, padx=5, pady=5)
                self.entries[var] = entry

        self.entries["entry_turno"] = ttk.Combobox(
            form_frame, values=["Manhã", "Tarde", "Noite"], state="readonly"
        )
        self.entries["entry_turno"].grid(row=5, column=1, padx=5, pady=5)

        # Definir valores disponíveis com base no tipo de acesso do usuário logado
        tipo_valores = []
        if self.empresa_logada["tipo_acesso"] == "CEO":
            tipo_valores = ["Administrador", "Gerente", "Operador"]
        elif self.empresa_logada["tipo_acesso"] == "Administrador":
            tipo_valores = ["Gerente", "Operador"]
        else:
            tipo_valores = ["Operador"]
            
        self.entries["entry_tipo"] = ttk.Combobox(
            form_frame,
            values=tipo_valores,
            state="readonly",
        )
        self.entries["entry_tipo"].grid(row=8, column=1, padx=5, pady=5)

        self.entries["entry_tipo"].configure(state="readonly")
        self.entries["entry_turno"].configure(state="readonly")

        self.entries["entry_tipo"].bind(
            "<<ComboboxSelected>>", self.atualizar_estado_botao_tipo
        )
        self.entries["entry_turno"].bind(
            "<<ComboboxSelected>>", self.atualizar_estado_botao_turno
        )

        def preencher_campos_com_primeiro_usuario():
            try:
                conn = self.obter_conexao_empresa()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM usuarios LIMIT 1")
                usuario = cursor.fetchone()

                if usuario:
                    self.entries["entry_cod_empresa"].insert(0, usuario[1])
                    self.entries["entry_usuario"].insert(0, usuario[3])
                    self.entries["entry_nome"].insert(0, usuario[4])
                    self.entries["entry_supervisor"].insert(0, usuario[5])
                    self.entries["entry_turno"].set(usuario[6])
                    self.entries["entry_email"].insert(0, usuario[7])
                    self.entries["entry_senha"].insert(0, "******")  # Oculta a senha
                    self.entries["entry_tipo"].set(usuario[9])

            except Exception as e:
                self.exibir_mensagem_erro("Erro", f"Erro ao carregar usuário: {str(e)}")
            finally:
                if conn:
                    conn.close()

        preencher_campos_com_primeiro_usuario()

    def atualizar_estado_botao_tipo(self, event):
        """Desabilita o botão relacionado ao tipo de acesso se já estiver selecionado."""
        tipo_selecionado = self.entries["entry_tipo"].get()
        if tipo_selecionado:
            for widget in self.janela_usuario.winfo_children():
                if (
                    isinstance(widget, ttk.Button)
                    and widget.cget("text") == "Tipo Acesso"
                ):
                    widget.state(["disabled"])

    def atualizar_estado_botao_turno(self, event):
        """Desabilita o botão relacionado ao turno se já estiver selecionado."""
        turno_selecionado = self.entries["entry_turno"].get()
        if turno_selecionado:
            for widget in self.janela_usuario.winfo_children():
                if isinstance(widget, ttk.Button) and widget.cget("text") == "Turno":
                    widget.state(["disabled"])

    def fechar_janela_usuario(self):
        """Fecha a janela de cadastro de usuário e remove as referências."""
        if hasattr(self, "janela_usuario") and self.janela_usuario.winfo_exists():
            self.janela_usuario.destroy()
        if hasattr(self, "entries"):
            del self.entries

    def buscar_empresa_por_codigo(self, event):
        """Busca o nome da empresa no banco principal a partir do código informado."""
        codigo = self.entries["entry_cod_empresa"].get()
        if codigo:
            try:
                conn = sqlite3.connect("deposito_principal.db")
                cursor = conn.cursor()
                cursor.execute("SELECT nome FROM empresas WHERE id = ?", (codigo,))
                resultado = cursor.fetchone()
                self.entries["lbl_nome_empresa"].config(
                    text=resultado[0] if resultado else "Empresa não encontrada!"
                )
            except Exception as e:
                self.exibir_mensagem_erro("Erro", f"Erro na consulta: {str(e)}")
            finally:
                conn.close()

    def criar_header_usuario(self, container):
        """Cria a barra de navegação e ações específicas para o cadastro de usuários.
        
        Este método cria dois frames com botões para navegação e operações CRUD específicas para usuários.
        
        Args:
            container: O container onde o header será criado
        """
        nav_frame = ttk.Frame(container, style="Header.TFrame")
        nav_frame.pack(fill=tk.X, pady=2)

        botoes_nav = [
            ("⏮️ Primeiro", self.primeiro_usuario),
            ("◀ Anterior", self.usuario_anterior),
            ("Próximo ▶", self.proximo_usuario),
            ("⏭️ Último", self.ultimo_usuario),
            ("🔍 Pesquisar", self.pesquisar_usuario),
        ]

        for texto, comando in botoes_nav:
            ttk.Button(
                nav_frame, text=texto, style="Header.TButton", command=comando
            ).pack(side=tk.LEFT, padx=2)

        crud_frame = ttk.Frame(container, style="Header.TFrame")
        crud_frame.pack(fill=tk.X, pady=2)

        botoes_crud = [
            ("➕ Novo Usuário", self.novo_usuario),
            ("✏️ Editar", self.editar_usuario),
            ("❌ Excluir", self.excluir_usuario),
            ("💾 Salvar", self.salvar_usuario),
            ("🚫 Cancelar", self.cancelar_edicao_usuario),
            ("📋 Listar Todos", self.listar_todos_usuarios),
        ]

        for texto, comando in botoes_crud:
            ttk.Button(
                crud_frame, text=texto, style="Header.TButton", command=comando
            ).pack(side=tk.LEFT, padx=2)
    
    def primeiro_usuario(self):
        """Navega para o primeiro usuário cadastrado."""
        try:
            conn = self.obter_conexao_empresa()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios ORDER BY id ASC LIMIT 1")
            usuario = cursor.fetchone()
            
            if usuario:
                self.limpar_campos_usuario()
                self.preencher_campos_usuario(usuario)
                self.exibir_mensagem_aviso_usuario("Navegação", "Primeiro usuário selecionado")
            else:
                self.exibir_mensagem_aviso_usuario("Navegação", "Não há usuários cadastrados")
        except Exception as e:
            self.exibir_mensagem_erro_usuario("Erro", f"Erro ao navegar: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def usuario_anterior(self):
        """Navega para o usuário anterior ao atual."""
        try:
            usuario_atual = self.entries["entry_usuario"].get()
            if not usuario_atual:
                self.primeiro_usuario()
                return
                
            conn = self.obter_conexao_empresa()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", (usuario_atual,))
            id_atual = cursor.fetchone()
            
            if id_atual:
                cursor.execute("SELECT * FROM usuarios WHERE id < ? ORDER BY id DESC LIMIT 1", (id_atual[0],))
                usuario = cursor.fetchone()
                
                if usuario:
                    self.limpar_campos_usuario()
                    self.preencher_campos_usuario(usuario)
                    self.exibir_mensagem_aviso_usuario("Navegação", "Usuário anterior selecionado")
                else:
                    self.exibir_mensagem_aviso_usuario("Navegação", "Este já é o primeiro usuário")
            else:
                self.primeiro_usuario()
        except Exception as e:
            self.exibir_mensagem_erro_usuario("Erro", f"Erro ao navegar: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def proximo_usuario(self):
        """Navega para o próximo usuário."""
        try:
            usuario_atual = self.entries["entry_usuario"].get()
            if not usuario_atual:
                self.primeiro_usuario()
                return
                
            conn = self.obter_conexao_empresa()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", (usuario_atual,))
            id_atual = cursor.fetchone()
            
            if id_atual:
                cursor.execute("SELECT * FROM usuarios WHERE id > ? ORDER BY id ASC LIMIT 1", (id_atual[0],))
                usuario = cursor.fetchone()
                
                if usuario:
                    self.limpar_campos_usuario()
                    self.preencher_campos_usuario(usuario)
                    self.exibir_mensagem_aviso("Navegação", "Próximo usuário selecionado")
                else:
                    self.exibir_mensagem_aviso("Navegação", "Este já é o último usuário")
            else:
                self.primeiro_usuario()
        except Exception as e:
            self.exibir_mensagem_erro("Erro", f"Erro ao navegar: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def ultimo_usuario(self):
        """Navega para o último usuário cadastrado."""
        try:
            conn = self.obter_conexao_empresa()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios ORDER BY id DESC LIMIT 1")
            usuario = cursor.fetchone()
            
            if usuario:
                self.limpar_campos_usuario()
                self.preencher_campos_usuario(usuario)
                self.exibir_mensagem_aviso("Navegação", "Último usuário selecionado")
            else:
                self.exibir_mensagem_aviso("Navegação", "Não há usuários cadastrados")
        except Exception as e:
            self.exibir_mensagem_erro("Erro", f"Erro ao navegar: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def pesquisar_usuario(self):
        """Abre uma janela para pesquisar usuários por nome ou código."""
        if not hasattr(self, "janela_pesquisa") or not self.janela_pesquisa.winfo_exists():
            self.janela_pesquisa = tk.Toplevel(self.janela_usuario)
            self.janela_pesquisa.title("Pesquisar Usuário")
            self.janela_pesquisa.geometry("400x200")
            
            ttk.Label(self.janela_pesquisa, text="Pesquisar por:").pack(pady=5)
            
            opcoes_frame = ttk.Frame(self.janela_pesquisa)
            opcoes_frame.pack(pady=5)
            
            self.opcao_pesquisa = tk.StringVar(value="nome")
            ttk.Radiobutton(opcoes_frame, text="Nome", variable=self.opcao_pesquisa, value="nome").pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(opcoes_frame, text="Usuário", variable=self.opcao_pesquisa, value="usuario").pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(opcoes_frame, text="Email", variable=self.opcao_pesquisa, value="email").pack(side=tk.LEFT, padx=5)
            
            ttk.Label(self.janela_pesquisa, text="Termo de pesquisa:").pack(pady=5)
            self.termo_pesquisa = ttk.Entry(self.janela_pesquisa, width=30)
            self.termo_pesquisa.pack(pady=5)
            
            ttk.Button(self.janela_pesquisa, text="Pesquisar", command=self.executar_pesquisa_usuario).pack(pady=10)
    
    def executar_pesquisa_usuario(self):
        """Executa a pesquisa de usuário com base nos critérios selecionados."""
        if not hasattr(self, "termo_pesquisa") or not hasattr(self, "opcao_pesquisa"):
            return
            
        termo = self.termo_pesquisa.get()
        opcao = self.opcao_pesquisa.get()
        
        if not termo:
            self.exibir_mensagem_erro("Erro", "Digite um termo para pesquisar")
            return
            
        try:
            conn = self.obter_conexao_empresa()
            cursor = conn.cursor()
            
            if opcao == "nome":
                cursor.execute("SELECT * FROM usuarios WHERE nome_completo LIKE ? LIMIT 1", (f"%{termo}%",))
            elif opcao == "usuario":
                cursor.execute("SELECT * FROM usuarios WHERE usuario LIKE ? LIMIT 1", (f"%{termo}%",))
            elif opcao == "email":
                cursor.execute("SELECT * FROM usuarios WHERE email LIKE ? LIMIT 1", (f"%{termo}%",))
            
            usuario = cursor.fetchone()
            
            if usuario:
                self.limpar_campos_usuario()
                self.preencher_campos_usuario(usuario)
                if hasattr(self, "janela_pesquisa") and self.janela_pesquisa.winfo_exists():
                    self.janela_pesquisa.destroy()
                self.exibir_mensagem_aviso("Pesquisa", "Usuário encontrado")
            else:
                self.exibir_mensagem_aviso("Pesquisa", "Nenhum usuário encontrado com este critério")
        except Exception as e:
            self.exibir_mensagem_erro("Erro", f"Erro ao pesquisar: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def novo_usuario(self):
        """Limpa os campos para cadastrar um novo usuário."""
        self.limpar_campos_usuario()
        self.entries["entry_cod_empresa"].insert(0, self.empresa_logada.get("id", ""))
        self.entries["lbl_nome_empresa"].config(text=self.empresa_logada.get("nome", ""))
        self.exibir_mensagem_aviso("Novo Usuário", "Preencha os dados para o novo usuário")
    
    def editar_usuario(self):
        """Habilita a edição dos campos do usuário atual."""
        usuario_atual = self.entries["entry_usuario"].get()
        if not usuario_atual:
            self.exibir_mensagem_erro("Erro", "Selecione um usuário para editar")
            return
            
        self.exibir_mensagem_aviso("Edição", "Modo de edição ativado. Faça as alterações necessárias e clique em Salvar.")
    
    def excluir_usuario(self):
        """Exclui o usuário atual do banco de dados."""
        usuario_atual = self.entries["entry_usuario"].get()
        if not usuario_atual:
            self.exibir_mensagem_erro("Erro", "Selecione um usuário para excluir")
            return
            
        if usuario_atual == self.empresa_logada.get("admin_user"):
            self.exibir_mensagem_erro("Erro", "Não é possível excluir o usuário administrador")
            return
            
        confirmacao = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o usuário {usuario_atual}?")
        if not confirmacao:
            return
            
        try:
            conn = self.obter_conexao_empresa()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE usuario = ?", (usuario_atual,))
            conn.commit()
            
            self.limpar_campos_usuario()
            self.exibir_mensagem_aviso("Exclusão", "Usuário excluído com sucesso")
            self.primeiro_usuario()
        except Exception as e:
            self.exibir_mensagem_erro("Erro", f"Erro ao excluir usuário: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def cancelar_edicao_usuario(self):
        """Cancela a edição atual e restaura os dados originais."""
        usuario_atual = self.entries["entry_usuario"].get()
        if usuario_atual:
            try:
                conn = self.obter_conexao_empresa()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario_atual,))
                usuario = cursor.fetchone()
                
                if usuario:
                    self.limpar_campos_usuario()
                    self.preencher_campos_usuario(usuario)
            except Exception as e:
                self.exibir_mensagem_erro("Erro", f"Erro ao cancelar edição: {str(e)}")
            finally:
                if conn:
                    conn.close()
        else:
            self.limpar_campos_usuario()
            
        self.exibir_mensagem_aviso("Edição", "Edição cancelada")
    
    def listar_todos_usuarios(self):
        """Abre uma janela com a lista de todos os usuários cadastrados."""
        if hasattr(self, "janela_lista") and self.janela_lista.winfo_exists():
            self.janela_lista.lift()
            return
            
        self.janela_lista = tk.Toplevel(self.janela_usuario)
        self.janela_lista.title("Lista de Usuários")
        self.janela_lista.geometry("800x400")
        
        # Criar tabela para exibir usuários
        colunas = ("ID", "Usuário", "Nome Completo", "Email", "Tipo Acesso", "Turno")
        self.tabela_usuarios = ttk.Treeview(self.janela_lista, columns=colunas, show="headings")
        
        # Configurar cabeçalhos
        for col in colunas:
            self.tabela_usuarios.heading(col, text=col)
            self.tabela_usuarios.column(col, width=100)
        
        # Adicionar barra de rolagem
        scrollbar = ttk.Scrollbar(self.janela_lista, orient="vertical", command=self.tabela_usuarios.yview)
        self.tabela_usuarios.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tabela_usuarios.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Carregar dados na tabela
        self.carregar_usuarios_na_tabela()
        
        # Adicionar evento de duplo clique para selecionar usuário
        self.tabela_usuarios.bind("<Double-1>", self.selecionar_usuario_da_lista)
    
    def carregar_usuarios_na_tabela(self, event=None):
        """Carrega os usuários do banco de dados na tabela."""
        # Limpar tabela
        for item in self.tabela_usuarios.get_children():
            self.tabela_usuarios.delete(item)
            
        try:
            conn = self.obter_conexao_empresa()
            cursor = conn.cursor()
            cursor.execute("SELECT id, usuario, nome_completo, email, tipo_acesso, turno FROM usuarios ORDER BY nome_completo")
            usuarios = cursor.fetchall()
            
            for usuario in usuarios:
                self.tabela_usuarios.insert("", "end", values=usuario)
        except Exception as e:
            self.exibir_mensagem_erro("Erro", f"Erro ao carregar usuários: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def selecionar_usuario_da_lista(self, event):
        """Seleciona um usuário da lista e preenche os campos do formulário."""
        item_selecionado = self.tabela_usuarios.selection()
        if not item_selecionado:
            return
            
        item = self.tabela_usuarios.item(item_selecionado[0])
        usuario_id = item["values"][0]
        
        try:
            conn = self.obter_conexao_empresa()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
            usuario = cursor.fetchone()
            
            if usuario:
                self.limpar_campos_usuario()
                self.preencher_campos_usuario(usuario)
                self.janela_lista.destroy()
        except Exception as e:
            self.exibir_mensagem_erro("Erro", f"Erro ao selecionar usuário: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def limpar_campos_usuario(self):
        """Limpa todos os campos do formulário de usuário."""
        for key, entry in self.entries.items():
            if key == "lbl_nome_empresa":
                entry.config(text="")
            elif key in ["entry_tipo", "entry_turno"]:
                entry.set("")
            else:
                entry.delete(0, tk.END)
    
    def preencher_campos_usuario(self, usuario):
        """Preenche os campos do formulário com os dados do usuário.
        
        Args:
            usuario: Tupla com os dados do usuário do banco de dados
        """
        # Mapear índices do banco de dados para os campos do formulário
        self.entries["entry_cod_empresa"].insert(0, usuario[1])
        self.entries["lbl_nome_empresa"].config(text=usuario[2])
        self.entries["entry_usuario"].insert(0, usuario[3])
        self.entries["entry_nome"].insert(0, usuario[4])
        self.entries["entry_supervisor"].insert(0, usuario[5])
        self.entries["entry_turno"].set(usuario[6])
        self.entries["entry_email"].insert(0, usuario[7])
        self.entries["entry_senha"].insert(0, "******")  # Oculta a senha real
        self.entries["entry_tipo"].set(usuario[9])
    
    def salvar_usuario(self):
        """Salva o cadastro de usuário no banco de dados da empresa."""
        if (
            not hasattr(self, "janela_usuario")
            or not self.janela_usuario.winfo_exists()
        ):
            return

        dados = {
            "cod_empresa": self.entries["entry_cod_empresa"].get(),
            "empresa_nome": self.entries["lbl_nome_empresa"].cget("text"),
            "usuario": self.entries["entry_usuario"].get(),
            "nome": self.entries["entry_nome"].get(),
            "supervisor": self.entries["entry_supervisor"].get(),
            "turno": self.entries["entry_turno"].get(),
            "email": self.entries["entry_email"].get(),
            "senha": self.entries["entry_senha"].get(),
            "tipo": self.entries["entry_tipo"].get(),
        }

        campos_obrigatorios = [
            "cod_empresa",
            "usuario",
            "nome",
            "supervisor",
            "turno",
            "email",
            "senha",
            "tipo",
        ]
        if not all(dados[field] for field in campos_obrigatorios):
            self.exibir_mensagem_erro("Erro", "Preencha todos os campos obrigatórios!")
            return

        if dados["empresa_nome"] == "Empresa não encontrada!":
            self.exibir_mensagem_erro("Erro", "Código da empresa inválido!")
            return

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", dados["email"]):
            self.exibir_mensagem_erro("Erro", "Formato de email inválido!")
            return

        if len(dados["senha"]) < 6:
            self.exibir_mensagem_erro("Erro", "Senha deve ter pelo menos 6 caracteres!")
            return

        try:
            conn = self.obter_conexao_empresa()
            cursor = conn.cursor()
            
            # Verificar permissões do usuário atual
            cursor.execute("SELECT tipo_acesso FROM usuarios WHERE usuario = ?", (self.empresa_logada['nome'],))
            tipo_atual = cursor.fetchone()
            tipo_atual = tipo_atual[0] if tipo_atual else 'CEO'
            
            # Verificar hierarquia de permissões
            if tipo_atual != 'CEO' and dados['tipo'] in ['CEO', 'Administrador']:
                self.exibir_mensagem_na_tela("erro", "Erro", "Apenas o CEO pode cadastrar administradores!")
                return
            elif tipo_atual not in ['CEO', 'Administrador'] and dados['tipo'] == 'Gerente':
                self.exibir_mensagem_na_tela("erro", "Erro", "Apenas o CEO e administradores podem cadastrar gerentes!")
                return
            
            senha_hash = hashlib.sha256(dados["senha"].encode()).hexdigest()
            cursor.execute(
                """
                INSERT INTO usuarios (
                    codigo_empresa,
                    empresa_nome,
                    usuario,
                    nome_completo,
                    nome_supervisor,
                    turno,
                    email,
                    senha,
                    tipo_acesso,
                    criado_por
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    dados["cod_empresa"],
                    dados["empresa_nome"],
                    dados["usuario"],
                    dados["nome"],
                    dados["supervisor"],
                    dados["turno"],
                    dados["email"],
                    senha_hash,
                    dados["tipo"],
                    self.empresa_logada['nome']
                ),
            )
            conn.commit()
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            self.fechar_janela_usuario()
        except sqlite3.IntegrityError:
            self.exibir_mensagem_na_tela("erro", "Erro", "Email já cadastrado!")
        except sqlite3.OperationalError as e:
            erro = str(e).lower()
            if "no such column" in erro:
                self.exibir_mensagem_na_tela(
                    "erro",
                    "Erro de Banco de Dados",
                    "Banco desatualizado! Exclua o banco da empresa e recadastre-a.",
                )
            else:
                self.exibir_mensagem_na_tela("erro", "Erro", f"Erro no banco: {erro}")
        except Exception as e:
            self.exibir_mensagem_na_tela("erro", "Erro", f"Erro inesperado: {str(e)}")
        finally:
            if "conn" in locals():
                conn.close()

    def exibir_mensagem_na_tela(self, tipo, titulo, mensagem):
        """Exibe mensagens de erro ou aviso na tela de cadastro de usuários sem fechar a janela."""
        if tipo == "erro":
            messagebox.showerror(titulo, mensagem, parent=self.janela_usuario)
        elif tipo == "aviso":
            messagebox.showwarning(titulo, mensagem, parent=self.janela_usuario)
        elif tipo == "info":
            messagebox.showinfo(titulo, mensagem, parent=self.janela_usuario)

    def tela_manutencao_empresa(self):
        """Exibe a tela de manutenção dos dados da empresa."""
        janela = tk.Toplevel(self.root)
        janela.title("Manutenção da Empresa")
        janela.geometry("600x400")

        container = ttk.Frame(janela)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(container, text="Dados da Empresa", style="Titulo.TLabel").pack(
            pady=10
        )

        form_frame = ttk.Frame(container)
        form_frame.pack(pady=10)

        campos = [
            ("Razão Social:", "entry_razao"),
            ("CNPJ:", "entry_cnpj"),
            ("Endereço:", "entry_endereco"),
            ("Telefone:", "entry_telefone"),
        ]

        self.entries_empresa = {}
        for idx, (texto, var) in enumerate(campos):
            ttk.Label(form_frame, text=texto).grid(
                row=idx, column=0, padx=5, pady=5, sticky="e"
            )
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            self.entries_empresa[var] = entry

        self.entries_empresa["entry_razao"].insert(0, self.empresa_logada["nome"])
        self.entries_empresa["entry_cnpj"].insert(0, self.empresa_logada["cnpj"] or "")
        self.entries_empresa["entry_endereco"].insert(
            0, self.empresa_logada["endereco"] or ""
        )
        self.entries_empresa["entry_telefone"].insert(
            0, self.empresa_logada["telefone"] or ""
        )

        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Atualizar", command=self.atualizar_empresa).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Cancelar", command=janela.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def atualizar_empresa(self):
        """Atualiza os dados da empresa no banco de dados principal."""
        dados = {
            "nome": self.entries_empresa["entry_razao"].get(),
            "cnpj": self.entries_empresa["entry_cnpj"].get(),
            "endereco": self.entries_empresa["entry_endereco"].get(),
            "telefone": self.entries_empresa["entry_telefone"].get(),
        }

        if not dados["nome"]:
            self.exibir_mensagem_erro("Erro", "Razão Social é obrigatória!")
            return

        try:
            conn = sqlite3.connect("deposito_principal.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE empresas SET
                    nome = ?,
                    cnpj = ?,
                    endereco = ?,
                    telefone = ?
                WHERE id = ?
            """,
                (
                    dados["nome"],
                    dados["cnpj"],
                    dados["endereco"],
                    dados["telefone"],
                    self.empresa_logada["id"],
                ),
            )
            conn.commit()

            self.empresa_logada["nome"] = dados["nome"]
            self.empresa_logada["cnpj"] = dados["cnpj"]
            self.empresa_logada["endereco"] = dados["endereco"]
            self.empresa_logada["telefone"] = dados["telefone"]

            messagebox.showinfo("Sucesso", "Dados atualizados com sucesso!")
        except Exception as e:
            self.exibir_mensagem_erro("Erro", f"Erro ao atualizar empresa: {str(e)}")
        finally:
            if conn:
                conn.close()

    def tela_consulta_produtos(self):
        pass

    def carregar_produtos_na_treeview(self):
        pass

    def tela_relatorio_estoque(self):
        pass

    def atualizar_treeview(self):
        """Atualiza a Treeview dos produtos."""
        if hasattr(self, "tree"):
            self.carregar_produtos_na_treeview()

    def pesquisar_registro(self):
        """Permite pesquisar um usuário e exibe os dados nos campos correspondentes."""
        termo = self.entries["entry_usuario"].get().strip()

        if not termo:
            self.exibir_mensagem_na_tela(
                "aviso", "Campo Vazio", "Digite um nome de usuário para pesquisar."
            )
            return

        try:
            conn = self.obter_conexao_empresa()
            cursor = conn.cursor()

            # Busca o usuário pelo nome ou parte do nome
            cursor.execute(
                """
                SELECT * FROM usuarios
                WHERE usuario LIKE ? COLLATE NOCASE
                LIMIT 1
                """,
                (f"%{termo}%",),
            )
            usuario = cursor.fetchone()

            if usuario:
                # Preenche os campos com os dados do usuário encontrado
                self.entries["entry_cod_empresa"].delete(0, tk.END)
                self.entries["entry_cod_empresa"].insert(0, usuario[1])

                self.entries["entry_usuario"].delete(0, tk.END)
                self.entries["entry_usuario"].insert(0, usuario[3])

                self.entries["entry_nome"].delete(0, tk.END)
                self.entries["entry_nome"].insert(0, usuario[4])

                self.entries["entry_supervisor"].delete(0, tk.END)
                self.entries["entry_supervisor"].insert(0, usuario[5])

                self.entries["entry_turno"].set(usuario[6])

                self.entries["entry_email"].delete(0, tk.END)
                self.entries["entry_email"].insert(0, usuario[7])

                self.entries["entry_senha"].delete(0, tk.END)
                self.entries["entry_senha"].insert(0, "******")  # Oculta a senha

                self.entries["entry_tipo"].set(usuario[9])
            else:
                self.exibir_mensagem_na_tela(
                    "aviso", "Não Encontrado", "Usuário não encontrado."
                )
        except Exception as e:
            self.exibir_mensagem_na_tela(
                "erro", "Erro", f"Erro ao buscar usuário: {str(e)}"
            )
        finally:
            if conn:
                conn.close()

    def carregar_usuarios_na_tabela(self, event=None):
        """Carrega os usuários do banco da empresa na Treeview da pesquisa."""
        termo = (
            self.entry_pesquisa.get().lower() if hasattr(self, "entry_pesquisa") else ""
        )
        turno = self.combo_turno.get() if hasattr(self, "combo_turno") else ""
        tipo = self.combo_tipo.get() if hasattr(self, "combo_tipo") else ""
        supervisor = (
            self.entry_supervisor.get().strip()
            if hasattr(self, "entry_supervisor")
            else ""
        )

        try:
            self.tree_usuarios.delete(*self.tree_usuarios.get_children())
            conn = self.obter_conexao_empresa()
            cursor = conn.cursor()

            base_query = """
                SELECT id, usuario, nome_completo, email, tipo_acesso, turno, nome_supervisor 
                FROM usuarios
            """
            where_clauses = []
            params = []

            if termo:
                where_clauses.append(
                    """
                    (usuario LIKE ? COLLATE NOCASE OR 
                    nome_completo LIKE ? COLLATE NOCASE OR 
                    email LIKE ? COLLATE NOCASE)
                """
                )
                params.extend([f"%{termo}%", f"%{termo}%", f"%{termo}%"])

            if turno:
                where_clauses.append("turno = ?")
                params.append(turno)

            if tipo:
                where_clauses.append("tipo_acesso = ?")
                params.append(tipo)

            if supervisor:
                where_clauses.append("nome_supervisor LIKE ? COLLATE NOCASE")
                params.append(f"%{supervisor}%")

            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)

            cursor.execute(base_query, params)

            for usuario in cursor.fetchall():
                self.tree_usuarios.insert(
                    "",
                    "end",
                    values=(
                        usuario[0],
                        usuario[1],
                        usuario[2],
                        usuario[3],
                        usuario[4],
                        usuario[5],
                        usuario[6],
                    ),
                )
        except sqlite3.Error as e:
            self.exibir_mensagem_erro(
                "Erro no Banco de Dados", f"Erro ao carregar usuários:\n{str(e)}"
            )
        except Exception as e:
            self.exibir_mensagem_erro("Erro", f"Erro inesperado:\n{str(e)}")
        finally:
            if "conn" in locals():
                conn.close()

    def atualizar_tabela_usuarios(self, event=None):
        """Atualiza a tabela de usuários na tela de pesquisa."""
        self.carregar_usuarios_na_tabela()

    # Métodos de navegação e ações (simulações para demonstração)
    def registro_anterior(self):
        """Volta para o usuário anterior na lista de usuários."""
        try:
            conn = self.obter_conexao_empresa()
            cursor = conn.cursor()

            # Obtém o ID do usuário atual
            usuario_atual = self.entries["entry_usuario"].get()
            cursor.execute(
                "SELECT id FROM usuarios WHERE usuario = ?", (usuario_atual,)
            )
            resultado = cursor.fetchone()

            if resultado:
                id_atual = resultado[0]

                # Busca o usuário anterior com ID menor
                cursor.execute(
                    "SELECT * FROM usuarios WHERE id < ? ORDER BY id DESC LIMIT 1",
                    (id_atual,),
                )
                usuario_anterior = cursor.fetchone()

                if usuario_anterior:
                    # Preenche os campos com os dados do usuário anterior
                    self.entries["entry_cod_empresa"].delete(0, tk.END)
                    self.entries["entry_cod_empresa"].insert(0, usuario_anterior[1])

                    self.entries["entry_usuario"].delete(0, tk.END)
                    self.entries["entry_usuario"].insert(0, usuario_anterior[3])

                    self.entries["entry_nome"].delete(0, tk.END)
                    self.entries["entry_nome"].insert(0, usuario_anterior[4])

                    self.entries["entry_supervisor"].delete(0, tk.END)
                    self.entries["entry_supervisor"].insert(0, usuario_anterior[5])

                    self.entries["entry_turno"].set(usuario_anterior[6])

                    self.entries["entry_email"].delete(0, tk.END)
                    self.entries["entry_email"].insert(0, usuario_anterior[7])

                    self.entries["entry_senha"].delete(0, tk.END)
                    self.entries["entry_senha"].insert(0, "******")  # Oculta a senha

                    self.entries["entry_tipo"].set(usuario_anterior[9])
                else:
                    # Desabilita o botão "Anterior" se não houver usuários anteriores
                    for widget in self.janela_usuario.winfo_children():
                        if (
                            isinstance(widget, ttk.Button)
                            and widget.cget("text") == "◀ Anterior"
                        ):
                            widget.state(["disabled"])
                    return
            else:
                self.exibir_mensagem_na_tela(
                    "erro", "Erro", "Usuário atual não encontrado."
                )
        except Exception as e:
            self.exibir_mensagem_na_tela(
                "erro", "Erro", f"Erro ao executar ação: {str(e)}"
            )
        finally:
            if conn:
                conn.close()

    def primeiro_registro(self):
        """Seleciona o primeiro usuário na lista de usuários."""
        try:
            conn = self.obter_conexao_empresa()
            cursor = conn.cursor()

            # Busca o primeiro usuário
            cursor.execute("SELECT * FROM usuarios ORDER BY id ASC LIMIT 1")
            primeiro_usuario = cursor.fetchone()

            if primeiro_usuario:
                # Preenche os campos com os dados do primeiro usuário
                self.entries["entry_cod_empresa"].delete(0, tk.END)
                self.entries["entry_cod_empresa"].insert(0, primeiro_usuario[1])

                self.entries["entry_usuario"].delete(0, tk.END)
                self.entries["entry_usuario"].insert(0, primeiro_usuario[3])

                self.entries["entry_nome"].delete(0, tk.END)
                self.entries["entry_nome"].insert(0, primeiro_usuario[4])

                self.entries["entry_supervisor"].delete(0, tk.END)
                self.entries["entry_supervisor"].insert(0, primeiro_usuario[5])

                self.entries["entry_turno"].set(primeiro_usuario[6])

                self.entries["entry_email"].delete(0, tk.END)
                self.entries["entry_email"].insert(0, primeiro_usuario[7])

                self.entries["entry_senha"].delete(0, tk.END)
                self.entries["entry_senha"].insert(0, "******")  # Oculta a senha

                self.entries["entry_tipo"].set(primeiro_usuario[9])
            else:
                self.exibir_mensagem_na_tela(
                    "aviso", "Lista Vazia", "Não há usuários cadastrados."
                )
        except Exception as e:
            self.exibir_mensagem_na_tela(
                "erro", "Erro", f"Erro ao executar ação: {str(e)}"
            )
        finally:
            if conn:
                conn.close()

    def proximo_registro(self):
        """Avança para o próximo usuário na lista de usuários."""
        try:
            conn = self.obter_conexao_empresa()
            cursor = conn.cursor()

            # Obtém o ID do usuário atual
            usuario_atual = self.entries["entry_usuario"].get()
            cursor.execute(
                "SELECT id FROM usuarios WHERE usuario = ?", (usuario_atual,)
            )
            resultado = cursor.fetchone()

            if resultado:
                id_atual = resultado[0]

                # Busca o próximo usuário com ID maior
                cursor.execute(
                    "SELECT * FROM usuarios WHERE id > ? ORDER BY id ASC LIMIT 1",
                    (id_atual,),
                )
                proximo_usuario = cursor.fetchone()

                if proximo_usuario:
                    # Preenche os campos com os dados do próximo usuário
                    self.entries["entry_cod_empresa"].delete(0, tk.END)
                    self.entries["entry_cod_empresa"].insert(0, proximo_usuario[1])

                    self.entries["entry_usuario"].delete(0, tk.END)
                    self.entries["entry_usuario"].insert(0, proximo_usuario[3])

                    self.entries["entry_nome"].delete(0, tk.END)
                    self.entries["entry_nome"].insert(0, proximo_usuario[4])

                    self.entries["entry_supervisor"].delete(0, tk.END)
                    self.entries["entry_supervisor"].insert(0, proximo_usuario[5])

                    self.entries["entry_turno"].set(proximo_usuario[6])

                    self.entries["entry_email"].delete(0, tk.END)
                    self.entries["entry_email"].insert(0, proximo_usuario[7])

                    self.entries["entry_senha"].delete(0, tk.END)
                    self.entries["entry_senha"].insert(0, "******")  # Oculta a senha

                    self.entries["entry_tipo"].set(proximo_usuario[9])
                else:
                    self.exibir_mensagem_na_tela(
                        "aviso", "Fim da Lista", "Não há mais usuários na lista."
                    )
            else:
                self.exibir_mensagem_na_tela(
                    "erro", "Erro", "Usuário atual não encontrado."
                )
        except Exception as e:
            self.exibir_mensagem_na_tela(
                "erro", "Erro", f"Erro ao executar ação: {str(e)}"
            )
        finally:
            if conn:
                conn.close()

    def ultimo_registro(self):
        """Seleciona o último usuário na lista de usuários."""
        try:
            conn = self.obter_conexao_empresa()
            cursor = conn.cursor()

            # Busca o último usuário
            cursor.execute("SELECT * FROM usuarios ORDER BY id DESC LIMIT 1")
            ultimo_usuario = cursor.fetchone()

            if ultimo_usuario:
                # Preenche os campos com os dados do último usuário
                self.entries["entry_cod_empresa"].delete(0, tk.END)
                self.entries["entry_cod_empresa"].insert(0, ultimo_usuario[1])

                self.entries["entry_usuario"].delete(0, tk.END)
                self.entries["entry_usuario"].insert(0, ultimo_usuario[3])

                self.entries["entry_nome"].delete(0, tk.END)
                self.entries["entry_nome"].insert(0, ultimo_usuario[4])

                self.entries["entry_supervisor"].delete(0, tk.END)
                self.entries["entry_supervisor"].insert(0, ultimo_usuario[5])

                self.entries["entry_turno"].set(ultimo_usuario[6])

                self.entries["entry_email"].delete(0, tk.END)
                self.entries["entry_email"].insert(0, ultimo_usuario[7])

                self.entries["entry_senha"].delete(0, tk.END)
                self.entries["entry_senha"].insert(0, "******")  # Oculta a senha

                self.entries["entry_tipo"].set(ultimo_usuario[9])
            else:
                self.exibir_mensagem_na_tela(
                    "aviso", "Lista Vazia", "Não há usuários cadastrados."
                )
        except Exception as e:
            self.exibir_mensagem_na_tela(
                "erro", "Erro", f"Erro ao executar ação: {str(e)}"
            )
        finally:
            if conn:
                conn.close()

    def pesquisar_range(self):
        """Exibe a tabela de pesquisa de usuários cadastrados."""
        if hasattr(self, "janela_pesquisa") and self.janela_pesquisa.winfo_exists():
            self.janela_pesquisa.lift()
            return

        self.janela_pesquisa = tk.Toplevel(self.root)
        self.janela_pesquisa.title("Pesquisa de Usuários Cadastrados")
        self.janela_pesquisa.geometry("1200x600")

        main_container = ttk.Frame(self.janela_pesquisa)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Filtros básicos
        filtro_frame = ttk.Frame(main_container)
        filtro_frame.pack(fill=tk.X, pady=5)
        ttk.Label(filtro_frame, text="Pesquisar:").pack(side=tk.LEFT, padx=5)
        self.entry_pesquisa = ttk.Entry(filtro_frame, width=40)
        self.entry_pesquisa.pack(side=tk.LEFT, padx=5)
        self.entry_pesquisa.bind("<KeyRelease>", self.atualizar_tabela_usuarios)

        # Filtros avançados
        filtro_avancado_frame = ttk.Frame(main_container)
        filtro_avancado_frame.pack(fill=tk.X, pady=5)

        ttk.Label(filtro_avancado_frame, text="Turno:").grid(row=0, column=0, padx=5)
        self.combo_turno = ttk.Combobox(
            filtro_avancado_frame,
            values=["", "Manhã", "Tarde", "Noite"],
            state="readonly",
            width=10,
        )
        self.combo_turno.grid(row=0, column=1, padx=5)
        self.combo_turno.bind("<<ComboboxSelected>>", self.atualizar_tabela_usuarios)

        ttk.Label(filtro_avancado_frame, text="Tipo Acesso:").grid(
            row=0, column=2, padx=5
        )
        self.combo_tipo = ttk.Combobox(
            filtro_avancado_frame,
            values=["", "Administrador", "Gerente", "Operador"],
            state="readonly",
            width=15,
        )
        self.combo_tipo.grid(row=0, column=3, padx=5)
        self.combo_tipo.bind("<<ComboboxSelected>>", self.atualizar_tabela_usuarios)

        ttk.Label(filtro_avancado_frame, text="Supervisor:").grid(
            row=0, column=4, padx=5
        )
        self.entry_supervisor = ttk.Entry(filtro_avancado_frame, width=20)
        self.entry_supervisor.grid(row=0, column=5, padx=5)
        self.entry_supervisor.bind("<KeyRelease>", self.atualizar_tabela_usuarios)

        # Tabela de resultados
        tree_frame = ttk.Frame(main_container)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        colunas = (
            "ID",
            "Usuário",
            "Nome Completo",
            "Email",
            "Tipo Acesso",
            "Turno",
            "Supervisor",
        )
        self.tree_usuarios = ttk.Treeview(
            tree_frame, columns=colunas, show="headings", selectmode="extended"
        )

        larguras = [50, 120, 200, 250, 100, 100, 150]
        for col, larg in zip(colunas, larguras):
            self.tree_usuarios.heading(col, text=col)
            self.tree_usuarios.column(col, width=larg, anchor="w")

        scroll = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self.tree_usuarios.yview
        )
        self.tree_usuarios.configure(yscrollcommand=scroll.set)

        self.tree_usuarios.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        self.carregar_usuarios_na_tabela()

    def criar_registro(self):
        try:
            messagebox.showinfo("Ação", "Criar registro")
        except Exception as e:
            self.exibir_mensagem_na_tela(
                "erro", "Erro", f"Erro ao executar ação: {str(e)}"
            )

    def atualizar_registro(self):
        try:
            messagebox.showinfo("Ação", "Atualizar registro")
        except Exception as e:
            self.exibir_mensagem_na_tela(
                "erro", "Erro", f"Erro ao executar ação: {str(e)}"
            )

    def copiar_registro(self):
        try:
            messagebox.showinfo("Ação", "Copiar registro")
        except Exception as e:
            self.exibir_mensagem_na_tela(
                "erro", "Erro", f"Erro ao executar ação: {str(e)}"
            )

    def deletar_registro(self):
        try:
            messagebox.showinfo("Ação", "Deletar registro")
        except Exception as e:
            self.exibir_mensagem_na_tela(
                "erro", "Erro", f"Erro ao executar ação: {str(e)}"
            )

    def salvar_edicao(self):
        try:
            messagebox.showinfo("Ação", "Salvar edição")
        except Exception as e:
            self.exibir_mensagem_na_tela(
                "erro", "Erro", f"Erro ao executar ação: {str(e)}"
            )

    def reset_edicao(self):
        try:
            messagebox.showinfo("Ação", "Resetar edição")
        except Exception as e:
            self.exibir_mensagem_na_tela(
                "erro", "Erro", f"Erro ao executar ação: {str(e)}"
            )

    def cancelar_edicao(self):
        """Cancela a edição sem sair da tela atual."""
        try:
            self.exibir_mensagem_aviso("Ação", "Edição cancelada com sucesso!")
        except Exception as e:
            self.exibir_mensagem_na_tela(
                "erro", "Erro", f"Erro ao executar ação: {str(e)}"
            )

    def iniciar(self):
        """Inicia o loop principal da aplicação."""
        self.root.mainloop()


if __name__ == "__main__":
    app = SistemaGerenciamentoDeposito()
    app.iniciar()

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import hashlib
import os
from PIL import Image, ImageTk

class SistemaGerenciamentoDeposito:
    def __init__(self):
        self.criar_banco_dados()
        self.criar_pasta_imagens()
        
        self.root = tk.Tk()
        self.root.title("Sistema de Gerenciamento de Depósito")
        self.root.geometry("1000x700")
        self.configurar_estilos()
        
        self.empresa_logada = None
        self.tela_login()
        
    def configurar_estilos(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        cores = {
            'fundo': '#F5F6FA',
            'primaria': '#2C3E50',
            'secundaria': '#3498DB',
            'sucesso': '#27AE60',
            'texto': '#2C3E50',
            'alerta': '#E74C3C'
        }
        
        self.style.configure('Cabecalho.TFrame', background=cores['primaria'])
        self.style.configure('Cabecalho.TLabel', 
                    font=('Arial', 16, 'bold'),
                    foreground='white',
                    background=cores['primaria'],
                    padding=(10, 5))
        self.style.configure('TLabel', background=cores['fundo'], foreground=cores['texto'], font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10), padding=8)
        self.style.map('TButton',
            foreground=[('active', 'white'), ('!disabled', 'white')],
            background=[('active', cores['secundaria']), ('!disabled', cores['primaria'])]
        )
        self.style.configure('TEntry', fieldbackground='white', font=('Arial', 10))
        self.style.configure('Titulo.TLabel', font=('Arial', 16, 'bold'), foreground=cores['primaria'])
        self.style.configure('Alerta.TLabel', foreground=cores['alerta'])
        self.style.configure('Header.TFrame', background='#E0E0E0', padding=5)
        self.style.configure('Header.TButton', 
                            font=('Arial', 9),
                            width=12,
                            padding=4,
                            anchor='center')
        self.style.map('Header.TButton',
            foreground=[('active', 'white'), ('!disabled', 'white')],
            background=[('active', '#2980B9'), ('!disabled', '#3498DB')]
        )

    def criar_header_acoes(self, container):
        nav_frame = ttk.Frame(container, style='Header.TFrame')
        nav_frame.pack(fill=tk.X, pady=2)
        
        botoes_nav = [
            ("⏮️ Primeiro", self.primeiro_registro),
            ("◀ Anterior", self.registro_anterior),
            ("Próximo ▶", self.proximo_registro),
            ("⏭️ Último", self.ultimo_registro),
            ("🔍 Pesquisar", self.pesquisar_registro),
            ("📂 Pesquisar Range", self.pesquisar_range)
        ]
        
        for texto, comando in botoes_nav:
            ttk.Button(nav_frame, text=texto, style='Header.TButton', 
                      command=comando).pack(side=tk.LEFT, padx=2)

        crud_frame = ttk.Frame(container, style='Header.TFrame')
        crud_frame.pack(fill=tk.X, pady=2)
        
        botoes_crud = [
            ("➕ Criar", self.criar_registro),
            ("✏️ Atualizar", self.atualizar_registro),
            ("⎘ Copiar", self.copiar_registro),
            ("❌ Deletar", self.deletar_registro),
            ("💾 Salvar", self.salvar_edicao),
            ("↩️ Reset", self.reset_edicao),
            ("🚫 Cancelar", self.cancelar_edicao)
        ]
        
        for texto, comando in botoes_crud:
            ttk.Button(crud_frame, text=texto, style='Header.TButton', 
                      command=comando).pack(side=tk.LEFT, padx=2)

    def criar_pasta_imagens(self):
        if not os.path.exists('logos'):
            os.makedirs('logos')

    def criar_banco_dados(self):
        conn = sqlite3.connect('deposito.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS empresas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                logo_path TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER,
                nome TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                preco REAL NOT NULL,
                FOREIGN KEY(empresa_id) REFERENCES empresas(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def tela_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        container = ttk.Frame(main_frame)
        container.pack(expand=True, padx=50, pady=50)
        
        ttk.Label(container, text="Login - Sistema de Depósito", style='Titulo.TLabel').pack(pady=20)
        
        form_frame = ttk.Frame(container)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Nome da Empresa:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        
        entry_frame = ttk.Frame(form_frame)
        entry_frame.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        
        self.entry_nome = ttk.Entry(entry_frame, width=30)
        self.entry_nome.pack(fill=tk.X)
        
        self.listbox = tk.Listbox(
            entry_frame, 
            height=4, 
            bg='white', 
            fg='#2C3E50', 
            font=('Arial', 10),
            selectbackground='#3498DB'
        )
        self.listbox.pack(fill=tk.X)
        self.listbox.pack_forget()
        
        conn = sqlite3.connect('deposito.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM empresas")
        empresas = cursor.fetchall()
        self.lista_empresas = [empresa[0] for empresa in empresas]
        conn.close()
        
        self.entry_nome.bind('<KeyRelease>', self.atualizar_sugestoes)
        self.listbox.bind('<<ListboxSelect>>', self.selecionar_empresa)
        self.entry_nome.bind('<FocusOut>', lambda e: self.verificar_foco())
        self.listbox.bind('<FocusOut>', lambda e: self.verificar_foco())

        ttk.Label(form_frame, text="Senha:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.entry_senha = ttk.Entry(form_frame, show="*", width=30)
        self.entry_senha.grid(row=1, column=1, padx=10, pady=5)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Login", command=self.fazer_login).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cadastrar Empresa", command=self.tela_cadastro_empresa).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Sair", command=self.root.quit).pack(side=tk.LEFT, padx=10)

    def atualizar_sugestoes(self, event):
        texto = self.entry_nome.get().lower()
        if texto:
            sugestoes = [empresa for empresa in self.lista_empresas if empresa.lower().startswith(texto)]
            self.listbox.delete(0, tk.END)
            for empresa in sugestoes:
                self.listbox.insert(tk.END, empresa)
            self.listbox.pack() if sugestoes else self.listbox.pack_forget()
        else:
            self.listbox.pack_forget()

    def selecionar_empresa(self, event):
        if selecao := self.listbox.curselection():
            empresa_selecionada = self.listbox.get(selecao[0])
            self.entry_nome.delete(0, tk.END)
            self.entry_nome.insert(0, empresa_selecionada)
            self.listbox.pack_forget()
            self.entry_senha.focus()

    def verificar_foco(self):
        if self.root.focus_get() not in (self.entry_nome, self.listbox):
            self.listbox.pack_forget()

    def tela_cadastro_empresa(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        container = ttk.Frame(main_frame)
        container.pack(expand=True, padx=50, pady=50)
        
        ttk.Label(container, text="Cadastro de Empresa", style='Titulo.TLabel').pack(pady=20)
        
        form_frame = ttk.Frame(container)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Nome da Empresa:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.entry_nome_cadastro = ttk.Entry(form_frame, width=30)
        self.entry_nome_cadastro.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Senha:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.entry_senha_cadastro = ttk.Entry(form_frame, show="*", width=30)
        self.entry_senha_cadastro.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Logo da Empresa:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.btn_logo = ttk.Button(form_frame, text="Selecionar Logo", command=self.selecionar_logo)
        self.btn_logo.grid(row=2, column=1, padx=10, pady=5)
        self.logo_path = None
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Cadastrar", command=self.cadastrar_empresa).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Voltar", command=self.tela_login).pack(side=tk.LEFT, padx=10)

    def selecionar_logo(self):
        if filepath := filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg")]):
            self.logo_path = filepath
            self.btn_logo.config(text="Logo Selecionado")

    def cadastrar_empresa(self):
        nome = self.entry_nome_cadastro.get()
        senha = self.entry_senha_cadastro.get()
        
        if not nome or not senha:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        
        try:
            conn = sqlite3.connect('deposito.db')
            cursor = conn.cursor()
            
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            logo_final = None
            
            if self.logo_path:
                nome_arquivo = f"logo_{nome}.{self.logo_path.split('.')[-1]}"
                caminho_final = os.path.join('logos', nome_arquivo)
                os.replace(self.logo_path, caminho_final)
                logo_final = caminho_final
            
            cursor.execute("INSERT INTO empresas (nome, senha, logo_path) VALUES (?, ?, ?)", 
                         (nome, senha_hash, logo_final))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Empresa cadastrada com sucesso!")
            self.tela_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Empresa já cadastrada!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")
        finally:
            conn.close()

    def fazer_login(self):
        nome = self.entry_nome.get()
        senha = self.entry_senha.get()
        
        try:
            conn = sqlite3.connect('deposito.db')
            cursor = conn.cursor()
            
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            cursor.execute("SELECT * FROM empresas WHERE nome = ? AND senha = ?", (nome, senha_hash))
            
            if empresa := cursor.fetchone():
                self.empresa_logada = {
                    'id': empresa[0],
                    'nome': empresa[1],
                    'logo_path': empresa[3]
                }
                self.tela_menu()
            else:
                messagebox.showerror("Erro", "Credenciais inválidas!")
        finally:
            conn.close()

    def tela_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header = ttk.Frame(main_frame, style='Cabecalho.TFrame')
        header.pack(fill=tk.X, padx=10, pady=10)
        
        if self.empresa_logada['logo_path'] and os.path.exists(self.empresa_logada['logo_path']):
            try:
                logo = Image.open(self.empresa_logada['logo_path'])
                logo = logo.resize((80, 80), Image.LANCZOS)
                logo_tk = ImageTk.PhotoImage(logo)
                
                logo_label = ttk.Label(header, image=logo_tk)
                logo_label.image = logo_tk
                logo_label.pack(side=tk.LEFT, padx=10, pady=5)
            except Exception as e:
                print(f"Erro ao carregar logo: {e}")
        
        ttk.Label(header, 
            text=f"Bem-vindo, {self.empresa_logada['nome']}", 
            style='Cabecalho.TLabel').pack(side=tk.LEFT, padx=10)
        
        menu_frame = ttk.Frame(main_frame)
        menu_frame.pack(expand=True, pady=50)
        
        botoes = [
            ("Cadastrar Produto", self.tela_cadastro_produto),
            ("Consultar Produtos", self.tela_consulta_produtos),
            ("Relatório de Estoque", self.tela_relatorio_estoque),
            ("Sair", self.tela_login)
        ]
        
        for texto, comando in botoes:
            btn = ttk.Button(menu_frame, text=texto, command=comando, width=25)
            btn.pack(pady=10, ipady=5)

    def tela_cadastro_produto(self):
        janela = tk.Toplevel(self.root)
        janela.title("Cadastro de Produto")
        janela.geometry("800x500")
        
        container = ttk.Frame(janela)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.criar_header_acoes(container)
        
        ttk.Label(container, text="Cadastro de Produto", style='Titulo.TLabel').pack(pady=10)
        
        form_frame = ttk.Frame(container)
        form_frame.pack(pady=20)
        
        campos = [
            ("Nome do Produto:", 'entry_nome'),
            ("Quantidade:", 'entry_quantidade'),
            ("Preço (R$):", 'entry_preco')
        ]
        
        for idx, (texto, var) in enumerate(campos):
            ttk.Label(form_frame, text=texto).grid(row=idx, column=0, padx=10, pady=5, sticky='e')
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            setattr(self, var, entry)
        
        def salvar_produto():
            self.atualizar_treeview()  # Adicione esta linha
            janela.destroy()
            nome = self.entry_nome.get()
            quantidade = self.entry_quantidade.get()
            preco = self.entry_preco.get()
            
            try:
                quantidade = int(quantidade)
                preco = float(preco)
                
                if not nome or quantidade < 0 or preco <= 0:
                    raise ValueError("Dados inválidos")
                
                conn = sqlite3.connect('deposito.db')
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO produtos (empresa_id, nome, quantidade, preco)
                    VALUES (?, ?, ?, ?)
                """, (self.empresa_logada['id'], nome, quantidade, preco))
                
                conn.commit()
                messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
                janela.destroy()
                
            except ValueError as e:
                messagebox.showerror("Erro", "Valores inválidos:\n- Quantidade deve ser inteiro\n- Preço deve ser positivo")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao cadastrar: {str(e)}")
            finally:
                conn.close() if 'conn' in locals() else None
        
        ttk.Button(container, text="Salvar Produto", command=salvar_produto, style='TButton').pack(pady=20)

    def tela_consulta_produtos(self):
        janela = tk.Toplevel(self.root)
        janela.title("Consulta de Produtos")
        janela.geometry("1000x700")
        
        container = ttk.Frame(janela)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.criar_header_acoes(container)
        
        # Frame principal para Treeview e scrollbar
        main_tree_frame = ttk.Frame(container)
        main_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurar Treeview
        colunas = ('ID', 'Nome', 'Quantidade', 'Preço')
        self.tree = ttk.Treeview(
            main_tree_frame, 
            columns=colunas, 
            show='headings', 
            selectmode='browse'
        )
        
        # Configurar cabeçalhos
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
            
        self.tree.column('Nome', width=250, anchor='w')
        self.tree.column('Preço', width=150, anchor='e')
        
        # Scrollbar
        scroll = ttk.Scrollbar(
            main_tree_frame, 
            orient=tk.VERTICAL, 
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scroll.set)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        scroll.grid(row=0, column=1, sticky='ns')
        
        # Carregar dados
        self.carregar_produtos_na_treeview()
        
        # Configurar expansão
        main_tree_frame.grid_rowconfigure(0, weight=1)
        main_tree_frame.grid_columnconfigure(0, weight=1)

    def carregar_produtos_na_treeview(self):
        try:
            # Limpar dados antigos
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            conn = sqlite3.connect('deposito.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nome, quantidade, preco 
                FROM produtos 
                WHERE empresa_id = ?
            """, (self.empresa_logada['id'],))
            
            for produto in cursor.fetchall():
                self.tree.insert('', 'end', values=(
                    produto[0],
                    produto[1],
                    produto[2],
                    f"R$ {produto[3]:.2f}"
                ))
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar produtos: {str(e)}")
        finally:
            conn.close() if 'conn' in locals() else None

    def tela_relatorio_estoque(self):
        janela = tk.Toplevel(self.root)
        janela.title("Relatório de Estoque")
        janela.geometry("800x600")
        
        container = ttk.Frame(janela)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.criar_header_acoes(container)
        
        conn = sqlite3.connect('deposito.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM produtos WHERE empresa_id = ?", 
                      (self.empresa_logada['id'],))
        total_produtos = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(quantidade * preco) FROM produtos WHERE empresa_id = ?",
                      (self.empresa_logada['id'],))
        valor_total = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT nome, quantidade 
            FROM produtos 
            WHERE empresa_id = ? AND quantidade < 10
            ORDER BY quantidade ASC
        """, (self.empresa_logada['id'],))
        produtos_baixo_estoque = cursor.fetchall()
        
        conn.close()
        
        relatorio_frame = ttk.Frame(container)
        relatorio_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(relatorio_frame, text="Relatório de Estoque", style='Titulo.TLabel').pack(pady=10)
        
        info_text = f"""
        Total de Produtos: {total_produtos}
        Valor Total do Estoque: R$ {valor_total:.2f}
        
        Produtos com Estoque Baixo:
        """
        
        ttk.Label(relatorio_frame, text=info_text, justify=tk.LEFT).pack(pady=10, anchor='w')
        
        for produto in produtos_baixo_estoque:
            cor = '#E74C3C' if produto[1] < 5 else '#F1C40F'
            ttk.Label(relatorio_frame, 
                     text=f"- {produto[0]}: {produto[1]} unidades",
                     style='Alerta.TLabel' if produto[1] < 5 else 'TLabel',
                     foreground=cor).pack(anchor='w')

    # Métodos de navegação
    def primeiro_registro(self): messagebox.showinfo("Ação", "Primeiro registro")
    def registro_anterior(self): messagebox.showinfo("Ação", "Registro anterior")
    def proximo_registro(self): messagebox.showinfo("Ação", "Próximo registro")
    def ultimo_registro(self): messagebox.showinfo("Ação", "Último registro")
    def pesquisar_registro(self): messagebox.showinfo("Ação", "Pesquisar registro")
    def pesquisar_range(self): messagebox.showinfo("Ação", "Pesquisar range")

    # Métodos CRUD
    def criar_registro(self): messagebox.showinfo("Ação", "Criar registro")
    def atualizar_registro(self): messagebox.showinfo("Ação", "Atualizar registro")
    def copiar_registro(self): messagebox.showinfo("Ação", "Copiar registro")
    def deletar_registro(self): messagebox.showinfo("Ação", "Deletar registro")
    def salvar_edicao(self): messagebox.showinfo("Ação", "Salvar edição")
    def reset_edicao(self): messagebox.showinfo("Ação", "Resetar edição")
    def cancelar_edicao(self): messagebox.showinfo("Ação", "Cancelar edição")

    def iniciar(self):
        self.root.mainloop()

    def atualizar_treeview(self):
        if hasattr(self, 'tree'):
            self.carregar_produtos_na_treeview()

if __name__ == "__main__":
    app = SistemaGerenciamentoDeposito()
    app.iniciar()
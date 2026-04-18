import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import os
from utils import aplicar_mascara_data, TEMAS

class MainInterface:
    def __init__(self, app):
        self.app = app
        self.tree = None

    def renderizar(self):
        self.app.limpar_tela()
        cores = TEMAS[self.app.tema_atual]
        self.app.root.config(bg=cores["bg"])
        
        # --- CONFIGURAÇÃO DE ESTILO PARA A TABELA (TREEVIEW) ---
        style = ttk.Style()
        style.theme_use("default") # Base para permitir customização
        
        # Configura as cores da Treeview baseadas no tema atual
        style.configure("Treeview", 
                        background=cores["entry_bg"], 
                        foreground=cores["fg"], 
                        fieldbackground=cores["entry_bg"],
                        borderwidth=0,
                        font=("Arial", 10))
        
        style.configure("Treeview.Heading", 
                        background="#004a8d", 
                        foreground="white", 
                        font=("Arial", 10, "bold"))

        # Cor de quando você seleciona uma linha
        style.map("Treeview", background=[('selected', '#007bff')])

        # --- HEADER ---
        header = tk.Frame(self.app.root, bg="#004a8d", pady=10)
        header.pack(fill="x")
        
        tk.Button(header, text="👤 Perfil", command=self.app.janela_perfil, 
                  bg="#004a8d", fg="white", bd=0, font=("Arial", 9, "underline")).pack(side="right", padx=10)
        
        tk.Label(header, text=f"{self.app.usuario_logado.nome} ({self.app.usuario_logado.cargo})", 
                 fg="white", bg="#004a8d", font=("Arial", 10, "bold")).pack(side="right", padx=10)
        
        tk.Button(header, text="⚙️ Config", command=self.app.janela_configuracoes, 
                  bg="#004a8d", fg="white", bd=0).pack(side="left", padx=10)

# --- GERENCIAR MÁQUINAS ---

# --- GERENCIAR MÁQUINAS ---

        f_cad = tk.LabelFrame(self.app.root, text=" Gerenciar Máquinas ", padx=10, pady=10, 
                              bg=cores["bg"], fg=cores["fg"])
        f_cad.pack(fill="x", padx=20, pady=10)
        
        # Frame interno para alinhar todos horizontalmente
        f_btns_row = tk.Frame(f_cad, bg=cores["bg"])
        f_btns_row.pack(fill="x", pady=5)

        # Configuração comum para todos os botões
        btn_params = {"side": "left", "padx": 5, "expand": True, "fill": "both"}
        largura_padrao = 22 # Define um tamanho fixo para todos

        tk.Button(f_btns_row, text="➕ NOVA MÁQUINA", bg="green", fg="white", font=("Arial", 9, "bold"),
                  command=self.app.janela_cadastro_maquina, width=largura_padrao).pack(**btn_params)

        tk.Button(f_btns_row, text="⚙️ MANUTENÇÃO", bg="#007bff", fg="white", font=("Arial", 9, "bold"),
                  command=self.app.janela_manutencao, width=largura_padrao).pack(**btn_params)
        
        tk.Button(f_btns_row, text="📋 HISTÓRICO", command=self.app.ver_hist, font=("Arial", 9, "bold"),
                  bg=cores["btn_bg"], fg=cores["fg"], width=largura_padrao).pack(**btn_params)

        tk.Button(f_btns_row, text="✏️ EDITAR", bg="#17a2b8", fg="white", font=("Arial", 9, "bold"),
                  command=self.app.janela_editar_maquina, width=largura_padrao).pack(**btn_params)

        tk.Button(f_btns_row, text="🗑️ EXCLUIR", bg="#f39c12", fg="white", font=("Arial", 9, "bold"),
                  command=self.confirmar_exclusao, width=largura_padrao).pack(**btn_params)
        
        # --- TABELA (Treeview) ---
        # Note que agora ela usará o 'style' configurado acima
        self.tree = ttk.Treeview(self.app.root, columns=("N", "U", "P", "S"), show="headings")
        for c, h in zip(("N", "U", "P", "S"), ("Nome", "Última", "Próxima", "Status")):
            self.tree.heading(c, text=h)
            self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20)
        
        # --- BOTÕES DE AÇÃO ---
        f_btn = tk.Frame(self.app.root, pady=10, bg=cores["bg"])
        f_btn.pack()
        
        tk.Button(f_btn, text="🚪 SAIR", command=self.app.deslogar, 
                  bg="#dc3545", fg="white", padx=15).pack(side="right", padx=20)
        
        self.atualizar_lista()

    def atualizar_lista(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        for m in self.app.maquinas:
            s, _ = m.get_status_agendamento()
            self.tree.insert("", "end", values=(m.nome, m.ultima_manutencao, m.agendamento, s))

    def confirmar_exclusao(self):
        if self.app.usuario_logado.cargo != "Supervisor":
            messagebox.showerror("Acesso Negado", "Apenas Supervisores podem excluir máquinas!")
            return
        
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma máquina para excluir.")
            return
            
        m_nome = self.tree.item(sel)['values'][0]
        if messagebox.askyesno("Confirmar", f"Deseja realmente excluir a máquina {m_nome}?"):
            self.app.maquinas = [m for m in self.app.maquinas if m.nome != m_nome]
            self.app.db.salvar(self.app.maquinas, self.app.usuarios)
            self.atualizar_lista()
            messagebox.showinfo("Sucesso", "Máquina removida.")
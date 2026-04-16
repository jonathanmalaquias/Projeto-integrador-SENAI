import tkinter as tk
from tkinter import messagebox, ttk
from utils import TEMAS

class UserManager:
    def __init__(self, app):
        self.app = app

    def alternar_cargo(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um usuário!")
            return
        
        nome_sel = self.tree.item(sel)['values'][0]
        
        for u in self.app.usuarios:
            if u.nome == nome_sel:
                # Lógica de inversão
                u.cargo = "Supervisor" if u.cargo == "Funcionário" else "Funcionário"
                break
        
        self.app.db.salvar(self.app.maquinas, self.app.usuarios)
        self.carregar_usuarios()
        messagebox.showinfo("Sucesso", f"Cargo de {nome_sel} atualizado!")

    def logar_como(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um usuário na lista!")
            return
        
        nome_selecionado = self.tree.item(sel)['values'][0]

        # Procurar o objeto usuario real na lista do app
        usuario_alvo = None
        for u in self.app.usuarios:
            if u.nome == nome_selecionado:
                usuario_alvo = u
                break
        
        if usuario_alvo:
            if messagebox.askyesno("Confirmar", f"Deseja entrar no sistema como '{usuario_alvo.nome}'?"):
                self.app.usuario_logado = usuario_alvo # Troca o login
                self.app.abrir_principal() # Manda para a tela das máquinas
                messagebox.showinfo("Sucesso", f"Logado como {usuario_alvo.nome}")

    def abrir_janela(self):
        # Se o usuário logado for o ADMIN, usamos a root principal em vez de Toplevel
        # para a janela não ficar "flutuando" sobre o nada.
        if self.app.usuario_logado.nome == "ADMINISTRADOR":
            self.win = self.app.root 
            self.app.limpar_tela()
        else:
            self.win = tk.Toplevel(self.app.root)
            self.win.title("Debugger de Contas")
            self.win.geometry("600x450")

        cores = TEMAS[self.app.tema_atual]
        self.win.config(bg=cores["bg"])

        tk.Label(self.win, text="PAINEL DE CONTROLE - ADMIN", font=("Arial", 14, "bold"), 
                 bg="#6f42c1", fg="white", pady=10).pack(fill="x")
        
        # --- TABELA DE USUÁRIOS ---
        # Reutilizando o estilo que já criamos para a Treeview
        self.tree = ttk.Treeview(self.win, columns=("N", "C", "P"), show="headings")
        self.tree.heading("N", text="Nome")
        self.tree.heading("C", text="Contato")
        self.tree.heading("P", text="Cargo")
        
        self.tree.column("N", width=150)
        self.tree.column("C", width=200)
        self.tree.column("P", width=100)
        self.tree.pack(fill="both", expand=True, padx=20)

        f_btn = tk.Frame(self.win, bg=cores["bg"], pady=10)
        f_btn.pack()

        tk.Button(f_btn, text="🗑️ EXCLUIR USUÁRIO", bg="#dc3545", fg="white",
                  command=self.excluir_usuario).pack(side="left", padx=5)
        tk.Button(f_btn, text="🔄 ATUALIZAR", command=self.carregar_usuarios, 
                  bg=cores["btn_bg"], fg=cores["fg"]).pack(side="left", padx=5)
        tk.Button(f_btn, text="🚪 SAIR DO ADMIN", bg="#dc3545", fg="white",
                  command=self.app.deslogar).pack(side="left", padx=5)
        tk.Button(f_btn, text="🔑 LOGAR COMO", bg="#28a745", fg="white",
                  command=self.logar_como).pack(side="left", padx=5)
        tk.Button(f_btn, text="🎭 MUDAR CARGO", bg="#17a2b8", fg="white",
          command=self.alternar_cargo).pack(side="left", padx=5)

        self.carregar_usuarios()

    def carregar_usuarios(self):
        # Limpa e recarrega a lista do app.usuarios
        for r in self.tree.get_children():
            self.tree.delete(r)
        
        for u in self.app.usuarios:
            self.tree.insert("", "end", values=(u.nome, u.contato, u.cargo))

    def excluir_usuario(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione alguém para deletar!")
            return
        
        dados = self.tree.item(sel)['values']
        nome_user = dados[0]

        # Impedir que o usuário logado se delete (auto-exclusão dá erro de sessão)
        if nome_user == self.app.usuario_logado.nome:
            messagebox.showerror("Erro", "Você não pode excluir a sua própria conta logada!")
            return

        if messagebox.askyesno("Confirmar", f"Deletar permanentemente o usuário {nome_user}?"):
            # Filtra a lista removendo o usuário
            self.app.usuarios = [u for u in self.app.usuarios if u.nome != nome_user]
            
            # Salva no banco de dados (JSON)
            self.app.db.salvar(self.app.maquinas, self.app.usuarios)
            
            self.carregar_usuarios()
            messagebox.showinfo("Sucesso", "Usuário removido!")

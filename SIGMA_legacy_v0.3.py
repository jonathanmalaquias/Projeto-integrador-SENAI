import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import json
import os
import csv

# --- CLASSE USUÁRIO ---
class Usuario:
    def __init__(self, nome, contato, cargo, senha):
        self.nome = nome
        self.contato = contato
        self.cargo = cargo # 'Supervisor' ou 'Funcionário'
        self.senha = senha

# --- CLASSE MÁQUINA ---
class Maquina:
    def __init__(self, nome, ultima_manutencao, agendamento=None, insumos_usados=None, procedimentos=None):
        self.nome = nome
        self.ultima_manutencao = ultima_manutencao
        self.agendamento = agendamento
        self.insumos_usados = insumos_usados if insumos_usados else []
        self.procedimentos = procedimentos if procedimentos else []

    def get_status_agendamento(self):
        if not self.agendamento: return "Sem agendamento", "black"
        try:
            data_alvo = datetime.strptime(self.agendamento, "%Y-%m-%d")
            hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            diferenca = (data_alvo - hoje).days
            if diferenca < 0: return f"VENCIDA ({abs(diferenca)} dias)", "red"
            elif diferenca == 0: return "HOJE!", "orange"
            elif diferenca <= 7: return f"ALERTA: {diferenca} dias", "#b8860b"
            else: return f"Ok ({diferenca} d)", "green"
        except: return "Erro data", "black"

# --- SISTEMA PRINCIPAL ---
class SIGMA:
    def __init__(self, root):
        self.root = root
        self.root.title("SIGMA - SENAI Gestão de Manutenção")
        self.root.geometry("1100x700")
        
        # Caminhos de arquivos
        pasta_docs = os.path.join(os.path.expanduser("~"), "Documents")
        self.arq_maquinas = os.path.join(pasta_docs, "sigma_maquinas.json")
        self.arq_usuarios = os.path.join(pasta_docs, "sigma_usuarios.json")
        
        self.usuario_logado = None
        self.maquinas = self.carregar_maquinas()
        self.usuarios = self.carregar_usuarios()
        
        # Iniciar pela tela de Login
        self.tela_login()

    # --- LÓGICA DE DADOS ---
    def carregar_maquinas(self):
        if os.path.exists(self.arq_maquinas):
            with open(self.arq_maquinas, 'r', encoding='utf-8') as f:
                return [Maquina(**m) for m in json.load(f)]
        return []

    def carregar_usuarios(self):
        if os.path.exists(self.arq_usuarios):
            with open(self.arq_usuarios, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                return [Usuario(**u) for u in dados]
        return []

    def salvar_tudo(self):
        dados_m = [m.__dict__ for m in self.maquinas]
        with open(self.arq_maquinas, 'w', encoding='utf-8') as f:
            json.dump(dados_m, f, indent=4, ensure_ascii=False)
        
        dados_u = [u.__dict__ for u in self.usuarios]
        with open(self.arq_usuarios, 'w', encoding='utf-8') as f:
            json.dump(dados_u, f, indent=4, ensure_ascii=False)

    # --- TELAS DE ACESSO ---
    def tela_login(self):
        self.limpar_tela()
        frame = tk.Frame(self.root, pady=50)
        frame.pack()

        tk.Label(frame, text="SIGMA LOGIN", font=("Arial", 18, "bold"), fg="#004a8d").pack(pady=10)
        
        tk.Label(frame, text="Nome de Usuário:").pack()
        ent_user = tk.Entry(frame, width=30)
        ent_user.pack(pady=5)

        tk.Label(frame, text="Senha:").pack()
        ent_senha = tk.Entry(frame, width=30, show="*")
        ent_senha.pack(pady=5)

        def logar():
            u = ent_user.get()
            s = ent_senha.get()
            for user in self.usuarios:
                if user.nome == u and user.senha == s:
                    self.usuario_logado = user
                    self.setup_ui_principal()
                    return
            messagebox.showerror("Erro", "Usuário ou senha inválidos!")

        tk.Button(frame, text="ENTRAR", bg="#004a8d", fg="white", width=25, command=logar).pack(pady=15)
        tk.Button(frame, text="CRIAR CONTA", command=self.tela_registro).pack()

    def tela_registro(self):
        self.limpar_tela()
        frame = tk.Frame(self.root, pady=30)
        frame.pack()

        tk.Label(frame, text="NOVO USUÁRIO", font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(frame, text="Nome Completo:").pack()
        ent_n = tk.Entry(frame, width=35); ent_n.pack()

        tk.Label(frame, text="Contato (E-mail ou WhatsApp):").pack()
        ent_c = tk.Entry(frame, width=35); ent_c.pack()

        tk.Label(frame, text="Senha:").pack()
        ent_s = tk.Entry(frame, width=35, show="*"); ent_s.pack()

        tk.Label(frame, text="Cargo/Nível:").pack(pady=5)
        combo_cargo = ttk.Combobox(frame, values=["Funcionário", "Supervisor"], state="readonly")
        combo_cargo.current(0)
        combo_cargo.pack()

        def registrar():
            if ent_n.get() and ent_s.get():
                novo = Usuario(ent_n.get(), ent_c.get(), combo_cargo.get(), ent_s.get())
                self.usuarios.append(novo)
                self.salvar_tudo()
                messagebox.showinfo("Sucesso", "Usuário cadastrado!")
                self.tela_login()
            else:
                messagebox.showwarning("Aviso", "Preencha os campos obrigatórios!")

        tk.Button(frame, text="REGISTRAR", bg="#28a745", fg="white", width=20, command=registrar).pack(pady=20)
        tk.Button(frame, text="VOLTAR", command=self.tela_login).pack()

    def limpar_tela(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # --- INTERFACE PRINCIPAL ---
    def setup_ui_principal(self):
        self.limpar_tela()
        
        # Header com info do usuário
        header = tk.Frame(self.root, bg="#004a8d", pady=10)
        header.pack(fill="x")
        
        txt_user = f"Usuário: {self.usuario_logado.nome} | Cargo: {self.usuario_logado.cargo}"
        tk.Label(header, text=txt_user, fg="white", bg="#004a8d", font=("Arial", 10)).pack(side="right", padx=20)
        tk.Label(header, text="SIGMA - GESTÃO SENAI", fg="white", bg="#004a8d", font=("Arial", 14, "bold")).pack(side="left", padx=20)

        # Cadastro Maquina
        frame_cad = tk.LabelFrame(self.root, text=" Gerenciar Máquinas ", padx=10, pady=10)
        frame_cad.pack(fill="x", padx=20, pady=10)

        tk.Label(frame_cad, text="Máquina:").grid(row=0, column=0)
        self.ent_nome = tk.Entry(frame_cad, width=30)
        self.ent_nome.grid(row=0, column=1, padx=5)

        tk.Label(frame_cad, text="Data Agenda:").grid(row=0, column=2)
        self.ent_agenda = tk.Entry(frame_cad, width=15)
        self.ent_agenda.grid(row=0, column=3, padx=5)
        self.ent_agenda.bind("<KeyRelease>", lambda e: self.aplicar_mascara(e, self.ent_agenda))

        tk.Button(frame_cad, text="➕ CADASTRAR", bg="#28a745", fg="white", command=self.adicionar_maquina).grid(row=0, column=4, padx=5)
        tk.Button(frame_cad, text="📝 EDITAR NOME", bg="#ffc107", command=self.editar_nome_maquina).grid(row=0, column=5, padx=5)

        # Tabela
        columns = ("Nome", "Ultima", "Proxima", "Status")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.tree.tag_configure("red", foreground="red")
        self.tree.tag_configure("orange", foreground="#ff8c00")

        # Botões de Ação
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=15)

        # Registro e Histórico (Todos podem)
        tk.Button(btn_frame, text="⚙️ REGISTRAR MANUTENÇÃO", bg="#007bff", fg="white", command=self.janela_manutencao).pack(side="left", padx=5)
        tk.Button(btn_frame, text="📋 HISTÓRICO", bg="#6c757d", fg="white", command=self.ver_historico).pack(side="left", padx=5)
        
        # Remover (Só Supervisor)
        self.btn_remover = tk.Button(btn_frame, text="🗑️ REMOVER MÁQUINA", bg="#dc3545", fg="white", command=self.remover_maquina)
        self.btn_remover.pack(side="left", padx=5)
        
        if self.usuario_logado.cargo != "Supervisor":
            self.btn_remover.config(state="disabled", bg="#e9ecef", fg="#6c757d") # Cinza e travado

        tk.Button(btn_frame, text="📊 EXPORTAR CSV", bg="#1d6f42", fg="white", command=self.exportar_csv).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🚪 SAIR", command=self.tela_login).pack(side="right", padx=20)

        self.atualizar_lista()

    # --- FUNÇÕES DE MÁQUINA ---
    def aplicar_mascara(self, event, entry):
        if event.keysym == "BackSpace": return
        texto = "".join(filter(str.isdigit, entry.get()))
        novo = ""
        if len(texto) <= 4: novo = texto
        elif len(texto) <= 6: novo = f"{texto[:4]}-{texto[4:6]}"
        else: novo = f"{texto[:4]}-{texto[4:6]}-{texto[6:8]}"
        entry.delete(0, tk.END); entry.insert(0, novo)

    def atualizar_lista(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        for m in self.maquinas:
            status, _ = m.get_status_agendamento()
            tag = "red" if "VENCIDA" in status else "orange" if "HOJE" in status else ""
            self.tree.insert("", "end", values=(m.nome, m.ultima_manutencao, m.agendamento or "---", status), tags=(tag,))

    def adicionar_maquina(self):
        n, a = self.ent_nome.get(), self.ent_agenda.get()
        if n:
            self.maquinas.append(Maquina(n, "---", a))
            self.salvar_tudo(); self.atualizar_lista()
            self.ent_nome.delete(0, tk.END); self.ent_agenda.delete(0, tk.END)

    def editar_nome_maquina(self):
        sel = self.tree.selection()
        if not sel: return
        nome_antigo = self.tree.item(sel)['values'][0]
        
        # Mini janela para novo nome
        win = tk.Toplevel(self.root); win.title("Editar Nome")
        tk.Label(win, text=f"Novo nome para {nome_antigo}:").pack(padx=20, pady=5)
        ent_novo = tk.Entry(win); ent_novo.pack(padx=20, pady=5)
        ent_novo.insert(0, nome_antigo)
        
        def confirmar():
            for m in self.maquinas:
                if m.nome == nome_antigo:
                    m.nome = ent_novo.get()
                    break
            self.salvar_tudo(); self.atualizar_lista(); win.destroy()
        
        tk.Button(win, text="SALVAR", command=confirmar, bg="blue", fg="white").pack(pady=10)

    def remover_maquina(self):
        # A trava de botão já existe, mas por segurança checamos no código também
        if self.usuario_logado.cargo != "Supervisor":
            messagebox.showerror("Acesso Negado", "Apenas Supervisores podem excluir máquinas.")
            return

        sel = self.tree.selection()
        if not sel: return
        nome = self.tree.item(sel)['values'][0]
        if messagebox.askyesno("Confirmação", f"Excluir '{nome}' definitivamente?"):
            self.maquinas = [m for m in self.maquinas if m.nome != nome]
            self.salvar_tudo(); self.atualizar_lista()

    # --- JANELAS DE REGISTRO E HISTÓRICO (Lógica mantida e ajustada) ---
    def janela_manutencao(self):
        sel = self.tree.selection(); 
        if not sel: return
        m_nome = self.tree.item(sel)['values'][0]
        win = tk.Toplevel(self.root); win.geometry("400x500"); win.title("Registro")
        tk.Label(win, text="Procedimentos:").pack(); t_proc = tk.Text(win, height=5); t_proc.pack()
        tk.Label(win, text="Insumos:").pack(); t_ins = tk.Text(win, height=3); t_ins.pack()
        tk.Label(win, text="Próxima Agenda (AAAA-MM-DD):").pack(); e_data = tk.Entry(win); e_data.pack()
        e_data.bind("<KeyRelease>", lambda e: self.aplicar_mascara(e, e_data))

        def salvar():
            agora = datetime.now().strftime("%d/%m/%Y %H:%M")
            for m in self.maquinas:
                if m.nome == m_nome:
                    m.ultima_manutencao = agora
                    registro = f"[{agora}] Por: {self.usuario_logado.nome}\nPROC: {t_proc.get('1.0', 'end-1c')}\nINS: {t_ins.get('1.0', 'end-1c')}\n"
                    m.insumos_usados.append(registro)
                    if e_data.get(): m.agendamento = e_data.get()
            self.salvar_tudo(); self.atualizar_lista(); win.destroy()
        
        tk.Button(win, text="SALVAR", bg="green", fg="white", command=salvar).pack(pady=20)

    def ver_historico(self):
        sel = self.tree.selection()
        if not sel: return
        m_nome = self.tree.item(sel)['values'][0]
        for m in self.maquinas:
            if m.nome == m_nome:
                win = tk.Toplevel(self.root); win.title(f"Histórico - {m.nome}")
                t = tk.Text(win, padx=10, pady=10); t.pack(fill="both", expand=True)
                t.insert("1.0", "\n".join(m.insumos_usados))
                t.config(state="disabled")

    def exportar_csv(self):
        caminho = filedialog.asksaveasfilename(defaultextension=".csv")
        if caminho:
            with open(caminho, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(['Máquina', 'Histórico'])
                for m in self.maquinas:
                    writer.writerow([m.nome, " | ".join(m.insumos_usados)])
            messagebox.showinfo("Sucesso", "Exportado!")

if __name__ == "__main__":
    root = tk.Tk()
    app = SIGMA(root)
    root.mainloop()

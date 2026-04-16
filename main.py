import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import os
from database import Database
from utils import TEMAS, aplicar_mascara_data
from auth_ui import AuthInterface
from app_ui import MainInterface
from models import Maquina
from user_manager import UserManager


class SIGMA:
    def __init__(self, root):
        self.root = root
        self.root.title("SIGMA - CSN")
        self.root.geometry("1100x700")
        
        self.db = Database()
        self.maquinas = self.db.carregar_maquinas()
        self.usuarios = self.db.carregar_usuarios()
        self.usuario_logado = None
        self.tema_atual = "claro"

        self.auth_ui = AuthInterface(self)
        self.main_ui = MainInterface(self)
        self.user_manager = UserManager(self) # <-- Adicione isso
        self.auth_ui.tela_login()


    def limpar_tela(self):
        for w in self.root.winfo_children(): w.destroy()

    def abrir_principal(self):
        self.main_ui.renderizar()

    def deslogar(self):
        self.usuario_logado = None
        self.auth_ui.tela_login()

    # --- LÓGICA DE MÁQUINAS ---
    def add_maq(self):
        nome = self.main_ui.en_n.get()
        agenda = self.main_ui.en_a.get()
        if nome:
            # Criando conforme sua classe Maquina
            nova = Maquina(nome, "---", agenda)
            self.maquinas.append(nova)
            self.db.salvar(self.maquinas, self.usuarios)
            self.main_ui.atualizar_lista()
            self.main_ui.en_n.delete(0, tk.END)
            self.main_ui.en_a.delete(0, tk.END)
        else:
            messagebox.showwarning("Aviso", "Digite o nome da máquina!")

    def ver_hist(self):
        sel = self.main_ui.tree.selection()
        if not sel: return
        m_nome = self.main_ui.tree.item(sel)['values'][0]
        cores = TEMAS[self.tema_atual]
        
        for m in self.maquinas:
            if m.nome == m_nome:
                win_h = tk.Toplevel(self.root)
                win_h.title(f"Histórico {m.nome}")
                win_h.geometry("500x450")
                win_h.config(bg=cores["bg"])
                
                txt = tk.Text(win_h, padx=10, pady=10, bg=cores["entry_bg"], fg=cores["fg"])
                txt.pack(fill="both", expand=True)
                txt.insert("1.0", "\n".join(m.insumos_usados))
                txt.config(state="disabled")

                if m.fotos:
                    def abrir_img():
                        path = m.fotos[-1]
                        if os.path.exists(path): os.startfile(path)
                        else: messagebox.showerror("Erro", "Imagem não encontrada.")
                    
                    tk.Button(win_h, text="🖼️ VER ÚLTIMA FOTO", bg="orange", 
                              command=abrir_img).pack(pady=5)

    def janela_manutencao(self):
        sel = self.main_ui.tree.selection()
        if not sel: 
            messagebox.showwarning("Aviso", "Selecione uma máquina na lista!")
            return
        
        m_nome = self.main_ui.tree.item(sel)['values'][0]
        cores = TEMAS[self.tema_atual]
        win = tk.Toplevel(self.root)
        win.title(f"Manutenção - {m_nome}")
        win.geometry("450x600")
        win.config(bg=cores["bg"])
        
        tk.Label(win, text="PROCEDIMENTOS:", bg=cores["bg"], fg=cores["fg"]).pack(pady=5)
        txt_proc = tk.Text(win, height=6, bg=cores["entry_bg"], fg=cores["fg"]); txt_proc.pack(padx=10)
        
        tk.Label(win, text="INSUMOS:", bg=cores["bg"], fg=cores["fg"]).pack(pady=5)
        txt_ins = tk.Text(win, height=4, bg=cores["entry_bg"], fg=cores["fg"]); txt_ins.pack(padx=10)
        
        tk.Label(win, text="PRÓXIMA DATA (AAAA-MM-DD):", bg=cores["bg"], fg=cores["fg"]).pack(pady=5)
        ent_data = tk.Entry(win, bg=cores["entry_bg"], fg=cores["fg"]); ent_data.pack()
        ent_data.bind("<KeyRelease>", lambda e: aplicar_mascara_data(e, ent_data))
        
        caminho_foto = tk.StringVar(value="")
        def selecionar_foto():
            arq = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.png *.jpeg")])
            if arq: caminho_foto.set(arq)

        tk.Button(win, text="📸 ANEXAR FOTO", command=selecionar_foto).pack(pady=10)

        def finalizar():
            agora = datetime.now().strftime("%d/%m/%Y %H:%M")
            novo_caminho = self.db.copiar_foto(caminho_foto.get())
            
            for m in self.maquinas:
                if m.nome == m_nome:
                    m.ultima_manutencao = agora
                    registro = f"--- DATA: {agora} por {self.usuario_logado.nome} ---\n"
                    registro += f"PROC: {txt_proc.get('1.0', 'end-1c')}\n"
                    registro += f"INSUMOS: {txt_ins.get('1.0', 'end-1c')}\n"
                    if novo_caminho:
                        m.fotos.append(novo_caminho)
                    m.insumos_usados.append(registro)
                    if ent_data.get(): m.agendamento = ent_data.get()
            
            self.db.salvar(self.maquinas, self.usuarios)
            self.main_ui.atualizar_lista()
            win.destroy()
            messagebox.showinfo("Sucesso", "Manutenção registrada!")

        tk.Button(win, text="FINALIZAR", bg="green", fg="white", command=finalizar).pack(pady=20)

    # --- CONFIGS E PERFIL (Já estavam corretos) ---
    def janela_configuracoes(self):
        win = tk.Toplevel(self.root)
        win.title("Temas")
        win.geometry("250x180")
        cores = TEMAS[self.tema_atual]
        win.config(bg=cores["bg"])
        tk.Label(win, text="Tema do Sistema:", bg=cores["bg"], fg=cores["fg"]).pack(pady=10)
        tk.Button(win, text="Claro ☀️", width=15, command=lambda: self.alternar_tema("claro", win)).pack(pady=5)
        tk.Button(win, text="Escuro 🌙", width=15, command=lambda: self.alternar_tema("escuro", win)).pack(pady=5)

    def alternar_tema(self, novo, win):
        self.tema_atual = novo
        win.destroy()
        if self.usuario_logado: self.abrir_principal()
        else: self.auth_ui.tela_login()

    def janela_perfil(self):
        win = tk.Toplevel(self.root)
        win.title("Meu Perfil")
        win.geometry("300x400")
        cores = TEMAS[self.tema_atual]
        win.config(bg=cores["bg"])
        tk.Label(win, text="Editar Dados", font=("bold", 12), bg=cores["bg"], fg=cores["fg"]).pack(pady=10)
        
        tk.Label(win, text="Nome:", bg=cores["bg"], fg=cores["fg"]).pack()
        en = tk.Entry(win, bg=cores["entry_bg"], fg=cores["fg"])
        en.insert(0, self.usuario_logado.nome); en.pack()

        tk.Label(win, text="Contato:", bg=cores["bg"], fg=cores["fg"]).pack()
        ec = tk.Entry(win, bg=cores["entry_bg"], fg=cores["fg"])
        ec.insert(0, self.usuario_logado.contato); ec.pack()

        tk.Label(win, text="Senha:", bg=cores["bg"], fg=cores["fg"]).pack()
        es = tk.Entry(win, show="*", bg=cores["entry_bg"], fg=cores["fg"])
        es.insert(0, self.usuario_logado.senha); es.pack()

        def salvar():
            self.usuario_logado.nome = en.get()
            self.usuario_logado.contato = ec.get()
            self.usuario_logado.senha = es.get()
            self.db.salvar(self.maquinas, self.usuarios)
            messagebox.showinfo("OK", "Atualizado!")
            win.destroy()
            self.abrir_principal()

        tk.Button(win, text="SALVAR", bg="green", fg="white", command=salvar).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = SIGMA(root)
    root.mainloop()
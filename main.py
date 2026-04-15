import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import csv
import os
from models import Maquina, Usuario
from database import Database
from utils import aplicar_mascara_data
from PIL import Image, ImageTk


class SIGMA:
    def __init__(self, root):
        self.root = root
        self.root.title("SIGMA - Gestão de Manutenção CSN")
        self.root.geometry("1100x700")
        
        self.db = Database()
        self.maquinas = self.db.carregar_maquinas()
        self.usuarios = self.db.carregar_usuarios()
        self.usuario_logado = None
        self.tela_login()

    def limpar_tela(self):
        for widget in self.root.winfo_children(): widget.destroy()

    def tela_login(self):
        self.limpar_tela()
        f = tk.Frame(self.root, pady=50); f.pack()
        tk.Label(f, text="SIGMA LOGIN", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Label(f, text="Usuário:").pack(); e_u = tk.Entry(f); e_u.pack(pady=5)
        tk.Label(f, text="Senha:").pack(); e_s = tk.Entry(f, show="*"); e_s.pack(pady=5)
        
        def logar():
            for u in self.usuarios:
                if u.nome == e_u.get() and u.senha == e_s.get():
                    self.usuario_logado = u; self.setup_ui_principal(); return
            messagebox.showerror("Erro", "Falha no login")
        
        tk.Button(f, text="ENTRAR", bg="#004a8d", fg="white", command=logar, width=20).pack(pady=10)
        tk.Button(f, text="Registrar", command=self.tela_registro).pack()

    def tela_registro(self):
        self.limpar_tela()
        f = tk.Frame(self.root, pady=20); f.pack()
        tk.Label(f, text="Nome:").pack(); en = tk.Entry(f); en.pack()
        tk.Label(f, text="Senha:").pack(); es = tk.Entry(f, show="*"); es.pack()
        c = ttk.Combobox(f, values=["Funcionário", "Supervisor"]); c.current(0); c.pack(pady=10)
        
        def registrar():
            self.usuarios.append(Usuario(en.get(), "", c.get(), es.get()))
            self.db.salvar(self.maquinas, self.usuarios); self.tela_login()
        
        tk.Button(f, text="Salvar", command=registrar).pack()

    def setup_ui_principal(self):
        self.limpar_tela()
        header = tk.Frame(self.root, bg="#004a8d", pady=10); header.pack(fill="x")
        tk.Label(header, text=f"{self.usuario_logado.nome} ({self.usuario_logado.cargo})", fg="white", bg="#004a8d").pack(side="right", padx=20)
        
        f_cad = tk.LabelFrame(self.root, text=" Gerenciar Máquinas ", padx=10, pady=10)
        f_cad.pack(fill="x", padx=20, pady=10)
        tk.Label(f_cad, text="Máquina:").grid(row=0, column=0)
        self.en_n = tk.Entry(f_cad); self.en_n.grid(row=0, column=1)
        tk.Label(f_cad, text="Agenda:").grid(row=0, column=2)
        self.en_a = tk.Entry(f_cad); self.en_a.grid(row=0, column=3)
        self.en_a.bind("<KeyRelease>", lambda e: aplicar_mascara_data(e, self.en_a))
        tk.Button(f_cad, text="CADASTRAR", bg="green", fg="white", command=self.add_maq).grid(row=0, column=4, padx=10)

        self.tree = ttk.Treeview(self.root, columns=("N", "U", "P", "S"), show="headings")
        for c, h in zip(("N", "U", "P", "S"), ("Nome", "Última", "Próxima", "Status")):
            self.tree.heading(c, text=h); self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20)
        
        f_btn = tk.Frame(self.root, pady=10); f_btn.pack()
        tk.Button(f_btn, text="⚙️ REGISTRAR MANUTENÇÃO", bg="#007bff", fg="white", command=self.janela_manutencao).pack(side="left", padx=5)
        tk.Button(f_btn, text="📋 HISTÓRICO", command=self.ver_hist).pack(side="left", padx=5)
        tk.Button(f_btn, text="🚪 SAIR", command=self.tela_login).pack(side="right", padx=20)
        
        self.atualizar_lista()

    def add_maq(self):
        if self.en_n.get():
            self.maquinas.append(Maquina(self.en_n.get(), "---", self.en_a.get()))
            self.db.salvar(self.maquinas, self.usuarios); self.atualizar_lista()

    def atualizar_lista(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        for m in self.maquinas:
            s, _ = m.get_status_agendamento()
            self.tree.insert("", "end", values=(m.nome, m.ultima_manutencao, m.agendamento, s))

    def janela_manutencao(self):
        sel = self.tree.selection()
        if not sel: return
        m_nome = self.tree.item(sel)['values'][0]
        
        win = tk.Toplevel(self.root); win.title(f"Manutenção - {m_nome}"); win.geometry("450x600")
        
        tk.Label(win, text="PROCEDIMENTOS REALIZADOS:", font=("Arial", 9, "bold")).pack(pady=5)
        txt_proc = tk.Text(win, height=6); txt_proc.pack(padx=10)
        
        tk.Label(win, text="INSUMOS / PEÇAS USADAS:", font=("Arial", 9, "bold")).pack(pady=5)
        txt_ins = tk.Text(win, height=4); txt_ins.pack(padx=10)
        
        tk.Label(win, text="PRÓXIMA MANUTENÇÃO (AAAA-MM-DD):").pack(pady=5)
        ent_data = tk.Entry(win); ent_data.pack()
        ent_data.bind("<KeyRelease>", lambda e: aplicar_mascara_data(e, ent_data))
        
        caminho_foto = tk.StringVar(value="")
        def selecionar_foto():
            arq = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.png *.jpeg")])
            if arq: 
                caminho_foto.set(arq)
                lbl_foto.config(text="Foto selecionada!", fg="green")

        tk.Button(win, text="📸 ANEXAR FOTO", command=selecionar_foto).pack(pady=10)
        lbl_foto = tk.Label(win, text="Nenhuma foto", fg="gray"); lbl_foto.pack()

        def finalizar():
            agora = datetime.now().strftime("%d/%m/%Y %H:%M")
            novo_caminho = self.db.copiar_foto(caminho_foto.get())
            
            for m in self.maquinas:
                if m.nome == m_nome:
                    m.ultima_manutencao = agora
                    # Criar registro estruturado no histórico
                    registro = f"--- DATA: {agora} por {self.usuario_logado.nome} ---\n"
                    registro += f"PROC: {txt_proc.get('1.0', 'end-1c')}\n"
                    registro += f"INSUMOS: {txt_ins.get('1.0', 'end-1c')}\n"
                    if novo_caminho:
                        m.fotos.append(novo_caminho)
                        registro += f"FOTO: {os.path.basename(novo_caminho)}\n"
                    
                    m.insumos_usados.append(registro)
                    if ent_data.get(): m.agendamento = ent_data.get()
            
            self.db.salvar(self.maquinas, self.usuarios); self.atualizar_lista(); win.destroy()
            messagebox.showinfo("Sucesso", "Manutenção registrada e foto salva na pasta do projeto!")

        tk.Button(win, text="FINALIZAR E SALVAR", bg="green", fg="white", font=("bold", 10), command=finalizar).pack(pady=20)

    def ver_hist(self):
            sel = self.tree.selection()
            if not sel: return
            m_nome = self.tree.item(sel)['values'][0]
            
            for m in self.maquinas:
                if m.nome == m_nome:
                    win_h = tk.Toplevel(self.root)
                    win_h.title(f"Histórico {m.nome}")
                    win_h.geometry("500x400")
                    
                    txt = tk.Text(win_h, padx=10, pady=10)
                    txt.pack(fill="both", expand=True)
                    txt.insert("1.0", "\n".join(m.insumos_usados))
                    txt.config(state="disabled")

                    # Se houver fotos, mostrar botão para abrir a última
                    if m.fotos:
                        def abrir_img():
                            # Verifica se a lista de fotos NÃO está vazia
                            if m.fotos: 
                                path = m.fotos[-1] # Pega a última
                                if os.path.exists(path):
                                    os.startfile(path) 
                                else:
                                    messagebox.showerror("Erro", "Arquivo de imagem não encontrado na pasta.")
                            else:
                                # Avisa o usuário que não tem foto em vez de dar erro no console
                                messagebox.showinfo("Aviso", "Esta máquina ainda não possui fotos registradas.")

                        tk.Button(win_h, text="🖼️ VER ÚLTIMA FOTO", bg="orange", 
                                command=abrir_img).pack(pady=5)
if __name__ == "__main__":
    root = tk.Tk()
    app = SIGMA(root)
    root.mainloop()
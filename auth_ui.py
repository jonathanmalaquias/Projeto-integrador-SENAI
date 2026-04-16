import tkinter as tk
from tkinter import messagebox, ttk
import os
from PIL import Image, ImageTk
from utils import TEMAS
from models import Usuario

class AuthInterface:
    def __init__(self, app):
        self.app = app

    def tela_login(self):
        self.app.limpar_tela()
        cores = TEMAS[self.app.tema_atual]
        self.app.root.config(bg=cores["bg"])
        
        f = tk.Frame(self.app.root, pady=50, bg=cores["bg"])
        f.pack()

        # --- LOGOS E QR CODE ---
        try:
            dir_at = os.path.dirname(os.path.abspath(__file__))
            img = Image.open(os.path.join(dir_at, "logo.png")).resize((150, 180), Image.LANCZOS)
            self.img_tk = ImageTk.PhotoImage(img)
            tk.Label(f, image=self.img_tk, bg=cores["bg"]).pack(pady=10)

            img_qr = Image.open(os.path.join(dir_at, "qrcode.png")).resize((100, 100), Image.LANCZOS)
            self.qr_tk = ImageTk.PhotoImage(img_qr)
            f_qr = tk.Frame(self.app.root, bg=cores["bg"])
            f_qr.place(relx=0.02, rely=0.98, anchor="sw")
            tk.Label(f_qr, text="GitHub Portfolio:", font=("Arial", 8, "bold"), bg=cores["bg"], fg=cores["fg"]).pack()
            tk.Label(f_qr, image=self.qr_tk, bg=cores["bg"]).pack()
        except:
            tk.Label(f, text="SIGMA LOGIN", font=("Arial", 18, "bold"), bg=cores["bg"], fg=cores["fg"]).pack(pady=10)

        # --- CAMPOS DE ENTRADA ---
        tk.Label(f, text="Usuário:", bg=cores["bg"], fg=cores["fg"]).pack()
        e_u = tk.Entry(f, bg=cores["entry_bg"], fg=cores["fg"], width=30)
        e_u.pack(pady=5)
        
        tk.Label(f, text="Senha:", bg=cores["bg"], fg=cores["fg"]).pack()
        e_s = tk.Entry(f, show="*", bg=cores["entry_bg"], fg=cores["fg"], width=30)
        e_s.pack(pady=5)

        def logar():
            u_digitado = e_u.get().strip()
            s_digitada = e_s.get()

            if u_digitado == "AdmUser" and s_digitada == "admuser123":
                self.app.usuario_logado = Usuario("ADMINISTRADOR", "N/A", "Supervisor", "admuser123")
                self.app.user_manager.abrir_janela()
                return

            for u in self.app.usuarios:
                if u.nome == u_digitado and u.senha == s_digitada:
                    self.app.usuario_logado = u
                    self.app.abrir_principal()
                    return
            
            messagebox.showerror("Erro", "Login Inválido")

        tk.Button(f, text="ENTRAR", bg="#004a8d", fg="white", font=("Arial", 10, "bold"),
                  command=logar, width=25).pack(pady=10)
        
        tk.Button(f, text="Registrar-se", command=self.tela_registro, 
                  bg=cores["btn_bg"], fg=cores["fg"], bd=0).pack()
        
        btn_c = tk.Button(self.app.root, text="⚙️", command=self.app.janela_configuracoes)
        btn_c.place(relx=0.98, rely=0.02, anchor="ne")

    def tela_registro(self):
        self.app.limpar_tela()
        cores = TEMAS[self.app.tema_atual]
        self.app.root.config(bg=cores["bg"])
        
        f = tk.Frame(self.app.root, pady=20, bg=cores["bg"])
        f.pack()
        
        tk.Label(f, text="Nome de Usuário:", bg=cores["bg"], fg=cores["fg"]).pack()
        en = tk.Entry(f, width=30, bg=cores["entry_bg"], fg=cores["fg"]); en.pack(pady=5)
        
        tk.Label(f, text="Contato (E-mail/Zap):", bg=cores["bg"], fg=cores["fg"]).pack()
        ec = tk.Entry(f, width=30, bg=cores["entry_bg"], fg=cores["fg"]); ec.pack(pady=5)
        
        tk.Label(f, text="Senha:", bg=cores["bg"], fg=cores["fg"]).pack()
        es = tk.Entry(f, show="*", width=30, bg=cores["entry_bg"], fg=cores["fg"]); es.pack(pady=5)
        
        def salvar():
            nome_digitado = en.get().strip()
            senha_digitada = es.get()
            
            if not nome_digitado or not senha_digitada:
                messagebox.showwarning("Erro", "Nome e Senha são obrigatórios!")
                return
            
            for usuario in self.app.usuarios:
                if usuario.nome.lower() == nome_digitado.lower():
                    messagebox.showerror("Erro", f"O usuário '{nome_digitado}' já está cadastrado!")
                    return
            
            # MUDANÇA AQUI: Cargo fixo como "Funcionário"
            novo_user = Usuario(nome_digitado, ec.get(), "Funcionário", senha_digitada)
            self.app.usuarios.append(novo_user)
            self.app.db.salvar(self.app.maquinas, self.app.usuarios)
            
            messagebox.showinfo("Sucesso", "Usuário cadastrado como Funcionário!")
            self.tela_login()
        
        tk.Button(f, text="Salvar", bg="green", fg="white", command=salvar, width=20).pack(pady=10)
        tk.Button(f, text="Voltar", command=self.tela_login, bg=cores["btn_bg"], fg=cores["fg"]).pack()
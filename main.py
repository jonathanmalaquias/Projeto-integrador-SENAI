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
        self.tema_atual = "escuro"

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
    def janela_cadastro_maquina(self):
        cores = TEMAS[self.tema_atual]
        win = tk.Toplevel(self.root)
        win.title("Cadastrar Ativo")
        win.geometry("400x450")
        win.config(bg=cores["bg"])

        tk.Label(win, text="NOME DA MÁQUINA/VEÍCULO:", bg=cores["bg"], fg=cores["fg"]).pack(pady=5)
        en_nome = tk.Entry(win, width=35, bg=cores["entry_bg"], fg=cores["fg"]); en_nome.pack()

        tk.Label(win, text="PRÓXIMA MANUTENÇÃO (Opcional):", bg=cores["bg"], fg=cores["fg"]).pack(pady=5)
        en_data = tk.Entry(win, width=35, bg=cores["entry_bg"], fg=cores["fg"]); en_data.pack()
        en_data.bind("<KeyRelease>", lambda e: aplicar_mascara_data(e, en_data))

        caminho_manual = tk.StringVar(value="")
        lbl_manual = tk.Label(win, text="Nenhum manual anexado", font=("Arial", 8), bg=cores["bg"], fg="gray")

        def selecionar_manual():
            # Aceita PDF, Texto ou todos os arquivos
            arq = filedialog.askopenfilename(filetypes=[("Documentos", "*.pdf *.txt *.docx"), ("Todos", "*.*")])
            if arq:
                caminho_manual.set(arq)
                lbl_manual.config(text=f"📄 {os.path.basename(arq)}", fg="blue")

        tk.Button(win, text="📂 ANEXAR MANUAL (PDF/TXT)", command=selecionar_manual).pack(pady=10)
        lbl_manual.pack()

        def salvar_nova():
            nome = en_nome.get().strip()
            if not nome:
                messagebox.showwarning("Erro", "O nome é obrigatório!")
                return
            
            # Copia o manual para a pasta do sistema
            manual_final = self.db.copiar_manual(caminho_manual.get())
            
            nova = Maquina(nome, "---", en_data.get(), manual=manual_final)
            self.maquinas.append(nova)
            self.db.salvar(self.maquinas, self.usuarios)
            self.main_ui.atualizar_lista()
            win.destroy()
            messagebox.showinfo("Sucesso", f"{nome} cadastrado!")

        tk.Button(win, text="SALVAR MÁQUINA", bg="green", fg="white", font=("bold"),
                  command=salvar_nova, height=2).pack(pady=30)
        
    def ver_hist(self):
        sel = self.main_ui.tree.selection()
        if not sel: return
        m_nome = self.main_ui.tree.item(sel)['values'][0]
        cores = TEMAS[self.tema_atual]
        
        # Busca o objeto da máquina
        maquina_obj = next((m for m in self.maquinas if m.nome == m_nome), None)
        if not maquina_obj: return

        win_h = tk.Toplevel(self.root)
        win_h.title(f"Histórico - {maquina_obj.nome}")
        win_h.geometry("600x600")
        win_h.config(bg=cores["bg"])

        # --- HEADER FIXO (Nome + Manual) ---
        header_top = tk.Frame(win_h, bg=cores["bg"], pady=10, padx=15)
        header_top.pack(fill="x")

        tk.Label(header_top, text=f"HISTÓRICO: {maquina_obj.nome}", 
                 font=("Arial", 11, "bold"), bg=cores["bg"], fg="#007bff").pack(side="left")

        def abrir_manual():
            if maquina_obj.manual and os.path.exists(maquina_obj.manual):
                os.startfile(maquina_obj.manual)
            else:
                messagebox.showinfo("Aviso", "Manual não disponível para esta máquina.")

        tk.Button(header_top, text="📖 MANUAL TÉCNICO", font=("Arial", 8, "bold"),
                  bg="#6c757d", fg="white", command=abrir_manual).pack(side="right")

        # --- ÁREA DE SCROLL ---
        canvas = tk.Canvas(win_h, bg=cores["bg"], highlightthickness=0)
        scroll = tk.Scrollbar(win_h, orient="vertical", command=canvas.yview)
        frame_lista = tk.Frame(canvas, bg=cores["bg"])

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.create_window((0, 0), window=frame_lista, anchor="nw", width=560)
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Inverter a lista para mostrar a manutenção mais recente primeiro
        for entrada in reversed(maquina_obj.insumos_usados):
            if "--- DATA:" in entrada:
                d_h, mec, proc, ins = "Antigo", "N/A", entrada.replace("\n", " "), "Ver log"
            else:
                try:
                    partes = entrada.split(" | ")
                    d_h = partes[0] if len(partes) > 0 else "N/A"
                    mec = partes[1] if len(partes) > 1 else "N/A"
                    proc = partes[2] if len(partes) > 2 else "N/A"
                    ins = partes[3] if len(partes) > 3 else "N/A"
                except:
                    d_h, mec, proc, ins = "Erro", "Erro", "Formato inválido", "N/A"

            card = tk.Frame(frame_lista, bg=cores["entry_bg"], bd=1, relief="solid")
            card.pack(fill="x", padx=10, pady=10)

            header_card = tk.Frame(card, bg="#007bff")
            header_card.pack(fill="x")
            
            tk.Label(header_card, text=f"📅 {d_h}    👤 Mecânico: {mec}", font=("Arial", 9, "bold"),
                     bg="#007bff", fg="white", anchor="w", padx=10).pack(fill="x")

            body = tk.Frame(card, bg=cores["entry_bg"], padx=10, pady=5)
            body.pack(fill="x")

            tk.Label(body, text="PROCEDIMENTOS:", font=("Arial", 8, "bold"),
                     bg=cores["entry_bg"], fg="#007bff", anchor="w").pack(fill="x")
            tk.Label(body, text=proc, bg=cores["entry_bg"], fg=cores["fg"], 
                     anchor="w", wraplength=500, justify="left").pack(fill="x", pady=(0, 5))

            tk.Label(body, text="INSUMOS:", font=("Arial", 8, "bold"),
                     bg=cores["entry_bg"], fg="#28a745", anchor="w").pack(fill="x")
            tk.Label(body, text=ins, bg=cores["entry_bg"], fg=cores["fg"], 
                     anchor="w", wraplength=500, justify="left").pack(fill="x")

        frame_lista.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Botão de Fotos no rodapé (Fixo)
        if maquina_obj.fotos:
            tk.Button(win_h, text="🖼️ VER ÚLTIMA FOTO ANEXADA", bg="orange", font=("Arial", 10, "bold"),
                      command=lambda: os.startfile(maquina_obj.fotos[-1]) if os.path.exists(maquina_obj.fotos[-1]) else None).pack(fill="x", padx=20, pady=10)
            

#Janela de Realizar manutenção

    def janela_manutencao(self):
        sel = self.main_ui.tree.selection()
        if not sel: 
            messagebox.showwarning("Aviso", "Selecione uma máquina na lista!")
            return
        
        m_nome = self.main_ui.tree.item(sel)['values'][0]
        cores = TEMAS[self.tema_atual]
        
        # Busca o objeto da máquina selecionada para pegar o caminho do manual
        maquina_obj = next((m for m in self.maquinas if m.nome == m_nome), None)
        
        win = tk.Toplevel(self.root)
        win.title(f"Manutenção - {m_nome}")
        win.geometry("450x650")
        win.config(bg=cores["bg"])
        
        # --- HEADER DA JANELA (Nome + Botão Manual) ---
        header_manut = tk.Frame(win, bg=cores["bg"])
        header_manut.pack(fill="x", pady=10, padx=15)

        tk.Label(header_manut, text=f"MÁQUINA: {m_nome}", 
                 font=("Arial", 10, "bold"), bg=cores["bg"], fg="#007bff").pack(side="left")

        def abrir_manual():
            if maquina_obj and maquina_obj.manual:
                if os.path.exists(maquina_obj.manual):
                    os.startfile(maquina_obj.manual)
                else:
                    messagebox.showerror("Erro", "Arquivo do manual não encontrado!")
            else:
                messagebox.showinfo("Aviso", "Esta máquina não possui manual cadastrado.")

        # Botão do Manual (só aparece se quiser, ou fica cinza se não tiver)
        btn_manual = tk.Button(header_manut, text="📖 VER MANUAL", font=("Arial", 8, "bold"),
                               bg="#6c757d", fg="white", command=abrir_manual, padx=5)
        btn_manual.pack(side="right")

        # --- CAMPOS DE TEXTO ---
        tk.Label(win, text="PROCEDIMENTOS REALIZADOS:", bg=cores["bg"], fg=cores["fg"]).pack(pady=5)
        txt_proc = tk.Text(win, height=6, bg=cores["entry_bg"], fg=cores["fg"], font=("Arial", 9)); txt_proc.pack(padx=15, fill="x")
        
        tk.Label(win, text="INSUMOS UTILIZADOS:", bg=cores["bg"], fg=cores["fg"]).pack(pady=5)
        txt_ins = tk.Text(win, height=4, bg=cores["entry_bg"], fg=cores["fg"], font=("Arial", 9)); txt_ins.pack(padx=15, fill="x")
        
        tk.Label(win, text="PRÓXIMA DATA (AAAA-MM-DD):", bg=cores["bg"], fg=cores["fg"]).pack(pady=5)
        ent_data = tk.Entry(win, bg=cores["entry_bg"], fg=cores["fg"], justify="center"); ent_data.pack()
        ent_data.bind("<KeyRelease>", lambda e: aplicar_mascara_data(e, ent_data))
        
        caminho_foto = tk.StringVar(value="")
        lbl_foto = tk.Label(win, text="Nenhuma foto anexada", font=("Arial", 8), bg=cores["bg"], fg="gray")
        
        def selecionar_foto():
            arq = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.png *.jpeg")])
            if arq: 
                caminho_foto.set(arq)
                lbl_foto.config(text="📸 Foto pronta!", fg="#28a745")

        tk.Button(win, text="📸 ANEXAR FOTO", command=selecionar_foto, bg=cores["btn_bg"], fg=cores["fg"]).pack(pady=10)
        lbl_foto.pack()

        def finalizar():
            proc_val = txt_proc.get('1.0', 'end-1c').strip().replace("\n", ", ")
            ins_val = txt_ins.get('1.0', 'end-1c').strip().replace("\n", ", ")

            if not proc_val or not ins_val:
                messagebox.showwarning("Aviso", "Preencha os procedimentos e insumos!")
                return

            agora = datetime.now().strftime("%d/%m/%Y %H:%M")
            novo_caminho = self.db.copiar_foto(caminho_foto.get())
            
            registro_formatado = f"{agora} | {self.usuario_logado.nome} | {proc_val} | {ins_val}"
            
            if maquina_obj:
                maquina_obj.ultima_manutencao = agora
                if novo_caminho:
                    maquina_obj.fotos.append(novo_caminho)
                maquina_obj.insumos_usados.append(registro_formatado)
                if ent_data.get(): 
                    maquina_obj.agendamento = ent_data.get()
            
            self.db.salvar(self.maquinas, self.usuarios)
            self.main_ui.atualizar_lista()
            win.destroy()
            messagebox.showinfo("Sucesso", "Manutenção registrada!")

        tk.Button(win, text="💾 FINALIZAR MANUTENÇÃO", bg="#28a745", fg="white", 
                  font=("Arial", 10, "bold"), command=finalizar, height=2, width=30).pack(pady=20)
        

    # --- CONFIGS E PERFIL ---
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
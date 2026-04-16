import tkinter as tk

def aplicar_mascara_data(event, entry):
    if event.keysym == "BackSpace": return
    texto = "".join(filter(str.isdigit, entry.get()))
    novo = ""
    if len(texto) <= 4: novo = texto
    elif len(texto) <= 6: novo = f"{texto[:4]}-{texto[4:6]}"
    else: novo = f"{texto[:4]}-{texto[4:6]}-{texto[6:8]}"
    entry.delete(0, tk.END)
    entry.insert(0, novo)

# ESSA PARTE ABAIXO PRECISA ESTAR AQUI:
TEMAS = {
    "claro": {
        "bg": "#f0f0f0",
        "fg": "#000000",
        "btn_bg": "#e0e0e0",
        "entry_bg": "#ffffff"
    },
    "escuro": {
        "bg": "#1e1e1e",
        "fg": "#ffffff",
        "btn_bg": "#333333",
        "entry_bg": "#2d2d2d"
    }
}
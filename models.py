from datetime import datetime

class Usuario:
    def __init__(self, nome, contato, cargo, senha):
        self.nome = nome
        self.contato = contato
        self.cargo = cargo
        self.senha = senha

class Maquina:
    def __init__(self, nome, ultima_manutencao, agendamento=None, insumos_usados=None, procedimentos=None, fotos=None, manual=None):
        self.nome = nome
        self.ultima_manutencao = ultima_manutencao
        self.agendamento = agendamento
        self.insumos_usados = insumos_usados if insumos_usados else []
        self.procedimentos = procedimentos if procedimentos else []
        self.fotos = fotos if fotos else [] # Lista de caminhos das imagens
        self.manual = manual if manual else []
        
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
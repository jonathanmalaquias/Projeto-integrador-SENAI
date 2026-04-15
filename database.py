import json
import os
import shutil
from models import Maquina, Usuario

class Database:
    def __init__(self):
        # Pasta base do projeto
        self.diretorio_base = os.path.dirname(os.path.abspath(__file__))
        self.pasta_fotos = os.path.join(self.diretorio_base, "armazenamento_fotos")
        
        # Criar pasta de fotos se não existir
        try:
            if not os.path.exists(self.pasta_fotos):
                os.makedirs(self.pasta_fotos)
        except Exception as e:
            print(f"Erro ao criar pasta de fotos: {e}")

        # Arquivos de dados nos Documentos do Windows
        pasta_docs = os.path.join(os.path.expanduser("~"), "Documents")
        self.arq_maquinas = os.path.join(pasta_docs, "sigma_maquinas.json")
        self.arq_usuarios = os.path.join(pasta_docs, "sigma_usuarios.json")

    def copiar_foto(self, caminho_original):
        """Copia a foto original para a pasta do projeto para não perdê-la"""
        if not caminho_original: return None
        try:
            nome_arquivo = os.path.basename(caminho_original)
            # Adiciona timestamp para não sobrescrever fotos com mesmo nome
            novo_nome = f"{int(os.path.getmtime(caminho_original))}_{nome_arquivo}"
            destino = os.path.join(self.pasta_fotos, novo_nome)
            shutil.copy2(caminho_original, destino)
            return destino # Retorna o novo caminho
        except Exception as e:
            print(f"Erro ao copiar foto: {e}")
            return None

    def carregar_maquinas(self):
        if os.path.exists(self.arq_maquinas):
            with open(self.arq_maquinas, 'r', encoding='utf-8') as f:
                return [Maquina(**m) for m in json.load(f)]
        return []

    def carregar_usuarios(self):
        if os.path.exists(self.arq_usuarios):
            with open(self.arq_usuarios, 'r', encoding='utf-8') as f:
                return [Usuario(**u) for u in json.load(f)]
        return []

    def salvar(self, maquinas, usuarios):
        dados_m = [m.__dict__ for m in maquinas]
        with open(self.arq_maquinas, 'w', encoding='utf-8') as f:
            json.dump(dados_m, f, indent=4, ensure_ascii=False)
        
        dados_u = [u.__dict__ for u in usuarios]
        with open(self.arq_usuarios, 'w', encoding='utf-8') as f:
            json.dump(dados_u, f, indent=4, ensure_ascii=False)
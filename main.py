import os
import time
# Importação da classe do Agente Reativo Simples que está no arquivo agente_simples.py
from agente_simples import AgenteReativoSimples


class Labirinto:
    def __init__(self, caminho_arquivo):
        self.caminho_arquivo = caminho_arquivo
        self.matriz = []
        self.linhas = 0
        self.colunas = 0
        self.inicio = None
        self.fim = None
        self.carregar_labirinto()

    def carregar_labirinto(self):
        try:
            with open(self.caminho_arquivo, 'r') as f:
                for linha in f:
                    partes = linha.strip().split()
                    if partes:
                        linha_int = [int(x) for x in partes]
                        self.matriz.append(linha_int)

            if not self.matriz:
                 raise ValueError("Labirinto vazio ou ilegível.")

            self.linhas = len(self.matriz)
            self.colunas = len(self.matriz[0])
            self.detectar_inicio_fim()

        except Exception as e:
            print(f"Erro ao ler arquivo {self.caminho_arquivo}: {e}")

    def detectar_inicio_fim(self):
        # 1. Procura por valores 2 (Entrada) e 3 (Saída) (p. ex., labirinto expiral.txt)
        temp_inicio = None
        temp_fim = None
        for y in range(self.linhas):
            for x in range(self.colunas):
                if self.matriz[y][x] == 2:
                    temp_inicio = (y, x)
                elif self.matriz[y][x] == 3:
                    temp_fim = (y, x)
        
        if temp_inicio and temp_fim:
            self.inicio = temp_inicio
            self.fim = temp_fim
            return
            
        # 2. Se não encontrou 2 e 3, procura aberturas nas bordas
        aberturas = []
        for y in range(self.linhas):
            for x in range(self.colunas):
                if self.matriz[y][x] != 1: # Não é parede (célula livre)
                    # É na borda
                    if y == 0 or y == self.linhas - 1 or x == 0 or x == self.colunas - 1:
                        aberturas.append((y, x))
        
        if len(aberturas) >= 2:
            # Assume a primeira abertura como início e a última como fim
            self.inicio = aberturas[0]
            self.fim = aberturas[-1]
        elif len(aberturas) == 1:
            self.inicio = aberturas[0]
            self.fim = self.encontrar_celula_livre_fundo()
        else:
            # Caso de erro ou labirinto totalmente fechado
            self.inicio = self.encontrar_celula_livre_topo()
            self.fim = self.encontrar_celula_livre_fundo()

    def encontrar_celula_livre_topo(self):
        for y in range(self.linhas):
            for x in range(self.colunas):
                if self.matriz[y][x] != 1: return (y, x)
        return None

    def encontrar_celula_livre_fundo(self):
        for y in range(self.linhas - 1, -1, -1):
            for x in range(self.colunas - 1, -1, -1):
                if self.matriz[y][x] != 1:
                    # Garante que não é o mesmo que o início
                    if (y, x) != self.inicio: return (y, x)
        return None

    def obter_percepcao(self, y, x):
        percepcoes = {}
        
        # Mapeamento: N(-1, 0), S(1, 0), L(0, 1), O(0, -1)
        direcoes = {
            'N': (-1, 0), 'S': (1, 0), 'L': (0, 1), 'O': (0, -1)
        }
        
        for dir_key, (dy, dx) in direcoes.items():
            ny, nx = y + dy, x + dx
            if 0 <= ny < self.linhas and 0 <= nx < self.colunas:
                percepcoes[dir_key] = self.matriz[ny][nx]
            else:
                percepcoes[dir_key] = 1 # Trata fora do limite como parede
                
        return percepcoes


def main():
    # Lista de arquivos (Assume que estão na mesma pasta do main.py)
    arquivos = [
        "labirinto expiral.txt",
        "labiritno aleatorio1.txt",
        "labirinto aleatorio 2.txt",
        "labirinto estrela.txt",
        "labirinto onda.txt",
        "labirinto comeia.txt"
    ]

    # Instancia o agente
    agente = AgenteReativoSimples()

    print("=== RELATÓRIO DE EXECUÇÃO: AGENTE REATIVO SIMPLES (MODULARIZADO) ===\n")

    for nome_arquivo in arquivos:
        print(f"--- Processando: {nome_arquivo} ---")

        if not os.path.exists(nome_arquivo):
            print(f"ERRO: Arquivo '{nome_arquivo}' não encontrado. Certifique-se de que está na mesma pasta.\n")
            continue

        lab = Labirinto(nome_arquivo)

        if not lab.inicio or not lab.fim:
            print(f"ERRO CRÍTICO: Não foi possível definir Inicio/Fim.\n")
            continue

        print(f"Entrada: {lab.inicio} -> Saída: {lab.fim}")

        posicao_atual = lab.inicio
        passos = 0
        
        # Limite máximo de passos (Aumentado para 10000)
        max_passos = 10000 
        
        sucesso = False

        start_time = time.time()

        while passos < max_passos:
            if posicao_atual == lab.fim:
                sucesso = True
                break

            y, x = posicao_atual
            percepcoes = lab.obter_percepcao(y, x)
            
            # O agente decide (retorna o delta de movimento (dy, dx))
            movimento = agente.decidir(percepcoes) 

            if movimento:
                posicao_atual = (y + movimento[0], x + movimento[1])
                passos += 1
            else:
                print("Agente retornou movimento nulo ou inválido.")
                break

        duracao = time.time() - start_time

        if sucesso:
            print(f"RESULTADO: SUCESSO! (Passos: {passos} | Tempo: {duracao:.4f}s)")
        else:
            print(f"RESULTADO: FALHA (Loop/Limite de {max_passos} passos atingido).")

        print("-" * 30 + "\n")


if __name__ == "__main__":
    main()

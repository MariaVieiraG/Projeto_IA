import os
import time
import sys

# Adiciona a pasta raiz do projeto ao path para resolver os imports relativos
# Isso é útil ao rodar em ambientes como PyCharm ou Colab.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 1. IMPORTS DOS AGENTES
# Ajuste conforme a estrutura de pastas
from AgenteReativoSimples.agente_simples import AgenteReativoSimples
from AgenteReativoBaseadoEmModelo.agente_modelo import AgenteReativoBaseadoEmModelo
from AgenteReativoBaseadoEmObjetivo.agente_baseado_obj import AgenteReativoBaseadoEmObjetivo

# A classe Labirinto permanece inalterada, pois é perfeita
class Labirinto:
    # ... (Seu código da classe Labirinto é mantido aqui) ...
    def __init__(self, caminho_arquivo):
        self.caminho_arquivo = caminho_arquivo
        self.matriz = []
        self.linhas = 0
        self.colunas = 0
        self.inicio = None
        self.fim = None
        self.carregar_labirinto()
        
    def carregar_labirinto(self):
        # ... (Mantido)
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
        # ... (Mantido)
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
            
        aberturas = []
        for y in range(self.linhas):
            for x in range(self.colunas):
                if self.matriz[y][x] != 1: 
                    if y == 0 or y == self.linhas - 1 or x == 0 or x == self.colunas - 1:
                        aberturas.append((y, x))
        
        if len(aberturas) >= 2:
            self.inicio = aberturas[0]
            self.fim = aberturas[-1]
        elif len(aberturas) == 1:
            self.inicio = aberturas[0]
            self.fim = self.encontrar_celula_livre_fundo()
        else:
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
                    if (y, x) != self.inicio: return (y, x)
        return None

    def obter_percepcao(self, y, x):
        percepcoes = {}
        direcoes = {
            'N': (-1, 0), 'S': (1, 0), 'L': (0, 1), 'O': (0, -1)
        }
        
        for dir_key, (dy, dx) in direcoes.items():
            ny, nx = y + dy, x + dx
            if 0 <= ny < self.linhas and 0 <= nx < self.colunas:
                percepcoes[dir_key] = self.matriz[ny][nx]
            else:
                percepcoes[dir_key] = 1 # Parede
                
        return percepcoes


# 2. FUNÇÃO MODULAR PARA TESTAR QUALQUER AGENTE
def executar_agente(AgenteClass, nome_arquivo, lab, max_passos, nome_agente):
    """Executa e testa um agente em um labirinto específico."""

    print(f"--- Processando [{nome_agente}]: {nome_arquivo} ---")
    
    if nome_agente == "Agente Reativo Simples":
        # Agente Simples: não precisa de inicialização especial
        agente = AgenteClass()
        posicao_atual = lab.inicio
        
    elif nome_agente == "Agente Reativo Baseado em Modelo":
        # Agente Modelo: precisa do labirinto e da posição inicial para iniciar a MEMÓRIA
        agente = AgenteClass(lab.matriz, lab.inicio)
        posicao_atual = lab.inicio # A posição atual será mantida dentro do agente
        
    elif nome_agente == "Agente Reativo Baseado em Objetivo (BFS)":
        # Agente Baseado em Objetivo com BFS
        agente = AgenteClass(lab.matriz, lab.inicio, lab.fim, modo_busca="bfs")
        posicao_atual = lab.inicio
        
    elif nome_agente == "Agente Reativo Baseado em Objetivo (DFS)":
        # Agente Baseado em Objetivo com DFS
        agente = AgenteClass(lab.matriz, lab.inicio, lab.fim, modo_busca="dfs")
        posicao_atual = lab.inicio
        
    else:
        # Outros agentes futuros
        agente = AgenteClass(lab.matriz, lab.inicio)
        posicao_atual = lab.inicio


    if not lab.inicio or not lab.fim:
        print(f"ERRO CRÍTICO: Não foi possível definir Inicio/Fim.\n")
        return

    print(f"Entrada: {lab.inicio} -> Saída: {lab.fim}")

    passos = 0
    sucesso = False
    start_time = time.time()

    while passos < max_passos:
        if posicao_atual == lab.fim:
            sucesso = True
            break

        y, x = posicao_atual
        percepcoes = lab.obter_percepcao(y, x)
        
        # O agente decide. A função decidir varia conforme o agente.
        if nome_agente == "Agente Reativo Baseado em Modelo":
            # Passa a matriz do labirinto para a decisão do Agente Modelo, que a consulta
            movimento = agente.decidir(percepcoes, lab.matriz) 
        else:
            # Agente Simples e Agente Baseado em Objetivo (apenas percepções)
            movimento = agente.decidir(percepcoes)

        if movimento:
            # Agentes que mantém posição interna (Modelo e Baseado em Objetivo)
            if nome_agente in ["Agente Reativo Baseado em Modelo", "Agente Reativo Baseado em Objetivo (BFS)", "Agente Reativo Baseado em Objetivo (DFS)"]:
                agente.mover(movimento)
                posicao_atual = agente.posicao_atual
            else:
                # Agente Simples: a posição é atualizada no loop principal
                posicao_atual = (y + movimento[0], x + movimento[1])
            
            passos += 1
        else:
            # Beco sem saída não resolvido, ou agente preso
            # Nota: O agente modelo deve retornar 'movimento' mesmo em backtracking.
            print("Agente retornou movimento nulo ou inválido.")
            break

    duracao = time.time() - start_time

    if sucesso:
        print(f"RESULTADO: SUCESSO! (Passos: {passos} | Tempo: {duracao:.4f}s)")
    else:
        print(f"RESULTADO: FALHA (Loop/Limite de {max_passos} passos atingido).")

    print("-" * 30 + "\n")


# 3. FUNÇÃO PRINCIPAL
def main():
    # Caminho base para a pasta dos labirintos
    caminho_labirintos = "Labirintos" 
    
    # Mapeamento dos nomes dos arquivos para serem testados
    arquivos = [
        "labirinto expiral.txt",
        "labiritno aleatorio1.txt",
        "labirinto aleatorio 2.txt",
        "labirinto estrela.txt",
        "labirinto onda.txt",
        "labirinto comeia.txt"
    ]
    max_passos = 10000

    
    # ------------------------------------------------------------------
    # TESTE 1: AGENTE REATIVO SIMPLES
    # ------------------------------------------------------------------
    print("=== RELATÓRIO DE EXECUÇÃO: AGENTE REATIVO SIMPLES ===\n")
    for nome_arquivo in arquivos:
        caminho_completo = os.path.join(caminho_labirintos, nome_arquivo)
        
        if not os.path.exists(caminho_completo):
            print(f"ERRO: Arquivo '{caminho_completo}' não encontrado. Pule.\n")
            continue
            
        lab = Labirinto(caminho_completo)
        
        # Chama a função modularizada para execução
        executar_agente(AgenteReativoSimples, nome_arquivo, lab, max_passos, "Agente Reativo Simples")

    
    # ------------------------------------------------------------------
    # TESTE 2: AGENTE REATIVO BASEADO EM MODELO (Sua Parte)
    # ------------------------------------------------------------------
    print("\n" + "="*50)
    print("=== RELATÓRIO DE EXECUÇÃO: AGENTE REATIVO BASEADO EM MODELO ===\n")
    for nome_arquivo in arquivos:
        caminho_completo = os.path.join(caminho_labirintos, nome_arquivo)
        
        if not os.path.exists(caminho_completo):
            continue # Já deu erro antes
            
        lab = Labirinto(caminho_completo)
        
        # Chama a função modularizada para execução
        executar_agente(AgenteReativoBaseadoEmModelo, nome_arquivo, lab, max_passos, "Agente Reativo Baseado em Modelo")

    # ------------------------------------------------------------------
    # TESTE 3: AGENTE REATIVO BASEADO EM OBJETIVO - BFS
    # ------------------------------------------------------------------

    print("\n" + "="*50)
    print("=== RELATÓRIO DE EXECUÇÃO: AGENTE REATIVO BASEADO EM OBJETIVO (BFS) ===\n")
    for nome_arquivo in arquivos:
        caminho_completo = os.path.join(caminho_labirintos, nome_arquivo)
        
        if not os.path.exists(caminho_completo):
            continue
            
        lab = Labirinto(caminho_completo)
        executar_agente(AgenteReativoBaseadoEmObjetivo, nome_arquivo, lab, max_passos, "Agente Reativo Baseado em Objetivo (BFS)")

    # ------------------------------------------------------------------
    # TESTE 4: AGENTE REATIVO BASEADO EM OBJETIVO - DFS
    # ------------------------------------------------------------------

    print("\n" + "="*50)
    print("=== RELATÓRIO DE EXECUÇÃO: AGENTE REATIVO BASEADO EM OBJETIVO (DFS) ===\n")
    for nome_arquivo in arquivos:
        caminho_completo = os.path.join(caminho_labirintos, nome_arquivo)
        
        if not os.path.exists(caminho_completo):
            continue
            
        lab = Labirinto(caminho_completo)
        executar_agente(AgenteReativoBaseadoEmObjetivo, nome_arquivo, lab, max_passos, "Agente Reativo Baseado em Objetivo (DFS)")
          

if __name__ == "__main__":
    main()
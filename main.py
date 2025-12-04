import os
import time
import sys

# Adiciona a pasta raiz do projeto ao path para resolver os imports relativos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 1. IMPORTS DOS AGENTES
# Ajuste conforme a estrutura de pastas
try:
    from AgenteReativoSimples.agente_simples import AgenteReativoSimples
except ImportError:
    class AgenteReativoSimples: # Mock
        def decidir(self, percepcoes): return None
        def __init__(self): pass

from AgenteReativoBaseadoEmModelo.agente_modelo import AgenteReativoBaseadoEmModelo

try:
    # Agente Baseado em Objetivo (Critério 3: BFS/DFS)
    from AgenteReativoBaseadoEmObjetivo.agente_baseado_obj import AgenteReativoBaseadoEmObjetivo
except ImportError:
    class AgenteReativoBaseadoEmObjetivo: pass # Mock para BFS/DFS

try:
    # Agente Baseado em Utilidade (Critério 4: A*)
    from AgenteBaseadoEmUtilidade.agente_estrela import AgenteBaseadoEmUtilidade
except ImportError:
    class AgenteBaseadoEmUtilidade: pass # Mock para A*


# A classe Labirinto permanece inalterada
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
        # Lógica de detecção de 2 e 3 (Início/Fim)
        temp_inicio = None
        temp_fim = None
        for y in range(self.linhas):
            for x in range(self.colunas):
                if self.matriz[y][x] == 2: temp_inicio = (y, x)
                elif self.matriz[y][x] == 3: temp_fim = (y, x)
        
        if temp_inicio and temp_fim:
            self.inicio = temp_inicio
            self.fim = temp_fim
            return
            
        # Lógica de fallback (para labirintos sem 2/3)
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


# 2. FUNÇÃO MODULAR PARA TESTAR AGENTES REATIVOS/OBJETIVO (PASSO A PASSO)
def executar_agente(AgenteClass, nome_arquivo, lab, max_passos, nome_agente):
    """Executa Agentes Reativos (Simples/Modelo) e Baseados em Objetivo (BFS/DFS) em loop passo a passo."""

    print(f"--- Processando [{nome_agente}]: {nome_arquivo} ---")
    
    # --- Inicialização ---
    if nome_agente == "Agente Reativo Simples":
        agente = AgenteClass()
    elif nome_agente == "Agente Reativo Baseado em Modelo":
        agente = AgenteClass(lab.matriz, lab.inicio)
    elif "Agente Reativo Baseado em Objetivo" in nome_agente:
        modo = "bfs" if "BFS" in nome_agente else "dfs"
        agente = AgenteClass(lab.matriz, lab.inicio, lab.fim, modo_busca=modo)
    else:
        return

    posicao_atual = lab.inicio
    if not lab.inicio or not lab.fim:
        print("ERRO CRÍTICO: Não foi possível definir Inicio/Fim.\n")
        return

    print(f"Entrada: {lab.inicio} -> Saída: {lab.fim}")

    passos = 0
    sucesso = False
    start_time = time.time()

    # --- Loop de Execução ---
    while passos < max_passos:
        if posicao_atual == lab.fim:
            sucesso = True
            break

        y, x = posicao_atual
        percepcoes = lab.obter_percepcao(y, x)
        
        # Agente Baseado em Modelo (usa apenas percepções, mas atualiza memória)
        if nome_agente == "Agente Reativo Baseado em Modelo":
            movimento = agente.decidir(percepcoes) 
        else:
            # Agente Simples e Agente Baseado em Objetivo (apenas percepções)
            movimento = agente.decidir(percepcoes)

        if movimento:
            dy, dx = movimento
            
            # Agentes com lógica de movimento e estado interno
            if nome_agente in ["Agente Reativo Baseado em Modelo", "Agente Reativo Baseado em Objetivo (BFS)", "Agente Reativo Baseado em Objetivo (DFS)"]:
                agente.mover(movimento)
                posicao_atual = agente.posicao_atual
            # Agente Simples (só reage, posição atualizada externamente)
            else:
                posicao_atual = (y + dy, x + dx)
            
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


# 3. FUNÇÃO DEDICADA PARA AGENTE BASEADO EM UTILIDADE (A*)
def executar_agente_astar(AgenteClass, nome_arquivo, lab, nome_agente):
    """Executa o Agente A* (Critério 4), que calcula o caminho completo (offline)."""
    print(f"--- Processando [{nome_agente}]: {nome_arquivo} ---")
    
    if not lab.inicio or not lab.fim:
        print("ERRO CRÍTICO: Não foi possível definir Inicio/Fim.\n")
        return

    print(f"Entrada: {lab.inicio} -> Saída: {lab.fim}")

    # Inicializa o Agente A*
    agente = AgenteClass(lab.matriz, lab.inicio, lab.fim)
    
    print("\nResultados por Heurística:")
    
    # Itera sobre as 3 heurísticas
    for heuristic_name in agente.heuristics_map.keys():
        start_time = time.time()
        # Chama o solve_astar: retorna path, custo_g, passos e nós expandidos
        path, custo_g, passos, nos_expandidos = agente.solve_astar(heuristic_name)
        duracao = time.time() - start_time
        
        if path:
            print(f"  [{heuristic_name}]: SUCESSO! (Passos: {passos} | Custo: {custo_g} | Tempo: {duracao:.6f}s | Expandidos: {nos_expandidos})")
        else:
            print(f"  [{heuristic_name}]: FALHA (Caminho não encontrado).")

    print("-" * 30 + "\n")


# 4. FUNÇÃO PRINCIPAL
def main():
    caminho_labirintos = "Labirintos" 
    
    arquivos = [
        "labirinto expiral.txt",
        "labiritno aleatorio1.txt",
        "labirinto aleatorio 2.txt",
        "labirinto estrela.txt",
        "labirinto onda.txt",
        "labirinto comeia.txt"
    ]
    max_passos = 10000

    # --- TESTE 1: AGENTE REATIVO SIMPLES ---
    print("="*50 + "\n=== RELATÓRIO DE EXECUÇÃO: AGENTE REATIVO SIMPLES ===\n")
    for nome_arquivo in arquivos:
        caminho_completo = os.path.join(caminho_labirintos, nome_arquivo)
        if os.path.exists(caminho_completo):
            lab = Labirinto(caminho_completo)
            executar_agente(AgenteReativoSimples, nome_arquivo, lab, max_passos, "Agente Reativo Simples")

    
    # --- TESTE 2: AGENTE REATIVO BASEADO EM MODELO ---
    print("="*50 + "\n=== RELATÓRIO DE EXECUÇÃO: AGENTE REATIVO BASEADO EM MODELO ===\n")
    for nome_arquivo in arquivos:
        caminho_completo = os.path.join(caminho_labirintos, nome_arquivo)
        if os.path.exists(caminho_completo):
            lab = Labirinto(caminho_completo)
            executar_agente(AgenteReativoBaseadoEmModelo, nome_arquivo, lab, max_passos, "Agente Reativo Baseado em Modelo")

    # --- TESTE 3: AGENTE BASEADO EM OBJETIVO (BFS/DFS) ---
    print("="*50 + "\n=== RELATÓRIO DE EXECUÇÃO: AGENTE BASEADO EM OBJETIVO (BFS) ===\n")
    for nome_arquivo in arquivos:
        caminho_completo = os.path.join(caminho_labirintos, nome_arquivo)
        if os.path.exists(caminho_completo):
            lab = Labirinto(caminho_completo)
            executar_agente(AgenteReativoBaseadoEmObjetivo, nome_arquivo, lab, max_passos, "Agente Reativo Baseado em Objetivo (BFS)")

    print("="*50 + "\n=== RELATÓRIO DE EXECUÇÃO: AGENTE BASEADO EM OBJETIVO (DFS) ===\n")
    for nome_arquivo in arquivos:
        caminho_completo = os.path.join(caminho_labirintos, nome_arquivo)
        if os.path.exists(caminho_completo):
            lab = Labirinto(caminho_completo)
            executar_agente(AgenteReativoBaseadoEmObjetivo, nome_arquivo, lab, max_passos, "Agente Reativo Baseado em Objetivo (DFS)")

    # --- TESTE 4: AGENTE BASEADO EM UTILIDADE (A*) ---
    print("="*50 + "\n=== RELATÓRIO DE EXECUÇÃO: AGENTE BASEADO EM UTILIDADE (A*) ===\n")
    for nome_arquivo in arquivos:
        caminho_completo = os.path.join(caminho_labirintos, nome_arquivo)
        if os.path.exists(caminho_completo):
            lab = Labirinto(caminho_completo)
            executar_agente_astar(AgenteBaseadoEmUtilidade, nome_arquivo, lab, "Agente Baseado em Utilidade (A*)")


if __name__ == "__main__":
    main()
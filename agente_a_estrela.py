import heapq
import math

class Node:
    """Representa um nó no caminho da busca A*."""
    def __init__(self, pos, g, h, parent=None):
        self.pos = pos
        self.g = g
        self.h = h
        self.parent = parent

        self.f = g + h

    def __lt__(self, other):
        # Comparação primária pelo custo f, desempate pelo custo g
        if self.f !=other.f:
            return self.f < other.f
        return self.g < other.g

    def __hash__(self):
        return hash(self.pos)

    def __eq__(self, other):
        return self.pos == other.pos
    
class Labirinto:
    """Carrega o labirinto e gerencia as posições de início/fim e a percepção do ambiente."""
    # Mantenha esta classe aqui, pois ela define o ambiente de teste
    
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

            if not self.matriz: raise ValueError("Labirinto vazio ou ilegível.")

            self.linhas = len(self.matriz)
            self.colunas = len(self.matriz[0])
            self.detectar_inicio_fim()

        except Exception as e:
            print(f"Erro ao ler arquivo {self.caminho_arquivo}: {e}")

    def detectar_inicio_fim(self):
        # Lógica de detecção (2 e 3, ou aberturas)
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
        
        # Simplificação: Encontra a primeira e última célula livre
        if not temp_inicio:
            for y in range(self.linhas):
                for x in range(self.colunas):
                    if self.matriz[y][x] != 1:
                        self.inicio = (y, x)
                        break
                if self.inicio: break

        if not temp_fim:
            for y in range(self.linhas - 1, -1, -1):
                for x in range(self.colunas - 1, -1, -1):
                    if self.matriz[y][x] != 1 and (y, x) != self.inicio:
                        self.fim = (y, x)
                        break
                if self.fim: break
    
    def obter_percepcao(self, y, x):
        # Lógica de percepção (N, S, L, O) para a matriz
        percepcoes = {}
        direcoes = {'N': (-1, 0), 'S': (1, 0), 'L': (0, 1), 'O': (0, -1)}
        
        for dir_key, (dy, dx) in direcoes.items():
            ny, nx = y + dy, x + dx
            if 0 <= ny < self.linhas and 0 <= nx < self.colunas:
                percepcoes[dir_key] = self.matriz[ny][nx]
            else:
                percepcoes[dir_key] = 1
                
        return percepcoes
        

class AgenteAStar:
    def __init__(self, labirinto):
        self.lab = labirinto
        self.inicio = labirinto.inicio
        self.fim = labirinto.fim
        self.heuristics_map = {
            "Manhattan": self.heuristic_manhattan,
            "Manhattan Ponderada": self.heuristic_weighted_manhattan,
            "Obstáculos": self.heuristic_obstacle_distance
        }    

    def heuristic_manhattan(self, pos):
        """Heurística 1: Distância de Manhattan (Admissível)."""
        y, x = pos
        y_fim, x_fim = self.fim
        return abs(y - y_fim) + abs(x - x_fim)

    def heuristic_weighted_manhattan(self, pos, weight=1.5):
        """Heurística 2: Distância e Manhattan Ponderada (Não-Admissível)."""    
        return weight * self.heuristic_manhattan(pos)
    
    def heuristic_obstacle_distance(self, pos, obstacle_cost=10):
        """Heurística 3: Baseada em Distância (Manhattan) e Proximidade a Obstáculos."""
        h_manhattan = self.heuristic_manhattan(pos)
        penalty = 0

        percepcoes = self.lab.obter_percepcao(pos[0], pos[1])

        for dir_val in percepcoes.values():
            if dir_val == 1:
                penalty += obstacle_cost
        return h_manhattan + penalty
    
    # --- Algoritmo A* (Função Central de Utilidade) ---

    def solve_astar(self, heuristic_name):
        """Executa o algoritmo A* usando a heurística especificada."""
        heuristic_func = self.heuristics_map.get(heuristic_name)
        if not heuristic_func: 
            raise ValueError(f"Heurística '{heuristic_name}' desconhecida.")
        
        open_list = []
        g_costs = {self.inicio: 0}
        start_node = Node(self.inicio, 0, heuristic_func(self.inicio))
        heapq.heappush(open_list, start_node)
        closed_set = set()

        while open_list:
            current_node = heapq.heappop(open_list)

            if current_node.pos in closed_set: continue
            closed_set.add(current_node.pos)

            if current_node.pos == self.fim:
                path = []
                temp = current_node
                while temp:
                    path.append(temp.pos)
                    temp = temp.parent
                return path [:: -1], current_node.g    
            
            y, x = current_node.pos
            direcoes = [(-1,0), (1, 0), (0, 1), (0, -1)]

            for dy, dx in direcoes:
                ny, nx = y + dy, x + dx
                neighbor_pos = (ny, nx)

                if 0 <= ny < self.lab.linhas and 0 <= nx < self.lab.colunas and self.lab.matriz[ny][nx] != 1:

                    new_g_cost = current_node.g + 1

                    if new_g_cost < g_costs.get(neighbor_pos, math.inf):

                        g_costs[neighbor_pos] = new_g_cost
                        h_cost = heuristic_func(neighbor_pos)
                        neighbor_node = Node(neighbor_pos, new_g_cost, h_cost, current_node)

                        heapq.heappush(open_list, neighbor_node)
    
        return None, 0 # Caminho não encontrado                    
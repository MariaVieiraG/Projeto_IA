import heapq
import math

class Node:
    """Representa um nó (célula) no caminho da busca A*."""
    def __init__(self, pos, g, h, parent=None):
        self.pos = pos # Posição (y, x)
        self.g = g     # Custo do caminho da origem até este nó
        self.h = h     # Custo heurístico (estimativa) deste nó até o objetivo
        self.parent = parent # Nó pai para reconstrução do caminho

        self.f = g + h # Custo total estimado

    def __lt__(self, other):
        """Compara nós para o heapq (min-heap). Prioriza menor f, depois menor g."""
        if self.f != other.f:
            return self.f < other.f
        return self.g < other.g

    def __hash__(self):
        """Permite que o nó seja usado em conjuntos (sets) ou dicionários (dicts)."""
        return hash(self.pos)

    def __eq__(self, other):
        """Verifica igualdade com base na posição."""
        return self.pos == other.pos
    
class AgenteBaseadoEmUtilidade:
    """
    Agente que usa o algoritmo A* (Baseado em Utilidade) para encontrar o 
    caminho mais eficiente, utilizando diferentes heurísticas.
    """
    def __init__(self, matriz_labirinto, inicio, fim):
        # Modelo Interno: O agente A* conhece o mapa completo desde o início.
        self.matriz = matriz_labirinto
        self.linhas = len(matriz_labirinto)
        self.colunas = len(matriz_labirinto[0])
        self.inicio = inicio
        self.fim = fim
        
        # 3 Heurísticas conforme o Critério 4 do Trabalho Prático
        self.heuristics_map = {
            "Manhattan": self.heuristic_manhattan,
            "Manhattan Ponderada (w=1.5)": lambda pos: self.heuristic_weighted_manhattan(pos, weight=1.5),
            "Obstáculos (C=10)": self.heuristic_obstacle_distance
        }    

    # ----------------------------------
    # Funções Heurísticas (h(n))
    # ----------------------------------

    def heuristic_manhattan(self, pos):
        """Heurística 1: Distância de Manhattan (Admissível)."""
        y, x = pos
        y_fim, x_fim = self.fim
        return abs(y - y_fim) + abs(x - x_fim)

    def heuristic_weighted_manhattan(self, pos, weight):
        """Heurística 2: Distância de Manhattan Ponderada (Não-Admissível)."""    
        # Usada para otimizar o tempo de busca sacrificando a garantia da rota ótima.
        return weight * self.heuristic_manhattan(pos)
    
    def heuristic_obstacle_distance(self, pos, obstacle_cost=10):
        """Heurística 3: Baseada em Distância (Manhattan) e Proximidade a Obstáculos."""
        h_manhattan = self.heuristic_manhattan(pos)
        penalty = 0

        # Verifica vizinhos para aplicar a penalidade de proximidade a paredes (1)
        direcoes = [(-1,0), (1, 0), (0, 1), (0, -1)]
        for dy, dx in direcoes:
            ny, nx = pos[0] + dy, pos[1] + dx
            if 0 <= ny < self.linhas and 0 <= nx < self.colunas and self.matriz[ny][nx] == 1:
                penalty += obstacle_cost
                
        return h_manhattan + penalty
    
    # ----------------------------------
    # Algoritmo A* (Função de Utilidade Central)
    # ----------------------------------

    def solve_astar(self, heuristic_name):
        """Executa o algoritmo A* usando a heurística especificada."""
        heuristic_func = self.heuristics_map.get(heuristic_name)
        if not heuristic_func: 
            # path, custo, passos, expandidos
            return None, 0, 0, 0 
        
        open_list = [] # Fila de prioridade (heap)
        g_costs = {self.inicio: 0} # Armazena o menor custo g encontrado até o momento
        start_node = Node(self.inicio, 0, heuristic_func(self.inicio))
        heapq.heappush(open_list, start_node)
        closed_set = set() # Nós já processados (garante que não haja ciclos)
        
        nodes_expanded = 0 # Métrica para análise

        while open_list:
            current_node = heapq.heappop(open_list)

            if current_node.pos in closed_set: continue
            closed_set.add(current_node.pos)
            nodes_expanded += 1

            # 1. Chegou ao Objetivo
            if current_node.pos == self.fim:
                path = []
                temp = current_node
                while temp:
                    path.append(temp.pos)
                    temp = temp.parent
                
                # Retorna o caminho, o custo total (g), número de passos e nós expandidos
                return path [:: -1], current_node.g, len(path) - 1, nodes_expanded    
            
            y, x = current_node.pos
            direcoes = [(-1,0), (1, 0), (0, 1), (0, -1)] # N, S, L, O

            # 2. Explora Vizinhos
            for dy, dx in direcoes:
                ny, nx = y + dy, x + dx
                neighbor_pos = (ny, nx)

                # Verifica limites e se não é parede (1)
                if 0 <= ny < self.linhas and 0 <= nx < self.colunas and self.matriz[ny][nx] != 1:

                    new_g_cost = current_node.g + 1 # Custo de mover-se para um vizinho

                    # Atualiza ou adiciona o nó se o novo caminho for melhor
                    if new_g_cost < g_costs.get(neighbor_pos, math.inf):

                        g_costs[neighbor_pos] = new_g_cost
                        h_cost = heuristic_func(neighbor_pos)
                        neighbor_node = Node(neighbor_pos, new_g_cost, h_cost, current_node)

                        heapq.heappush(open_list, neighbor_node)
    
        # 3. Caminho não encontrado
        return None, 0, 0, nodes_expanded
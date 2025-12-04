from collections import deque


class AgenteReativoBaseadoEmObjetivo:
    def __init__(self, labirinto, posicao_inicial, objetivo=None, modo_busca="dfs"):
        
        self.grafo = labirinto
        self.posicao_inicial = posicao_inicial
        self.posicao_atual = posicao_inicial
        self.objetivo = objetivo
        self.modo_busca = modo_busca.lower()
        
        
        if not self.objetivo:
            for y in range(len(labirinto)):
                for x in range(len(labirinto[0])):
                    if labirinto[y][x] == 3:
                        self.objetivo = (y, x)
                        break
                if self.objetivo:
                    break
        
        
        self.caminho_planejado = []
        self.indice_caminho = 0
        self.caminho_calculado = False

    def vizinhos_livres(self, pos):
       
        y, x = pos
        moves = [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
        validos = []
        for ny, nx in moves:
            if 0 <= ny < len(self.grafo) and 0 <= nx < len(self.grafo[0]):
                if self.grafo[ny][nx] != 1:  
                    validos.append((ny, nx))
        return validos

    def busca_dfs(self):
        
        pilha = [(self.posicao_inicial, [self.posicao_inicial])]
        visitados = set()

        while pilha:
            atual, caminho = pilha.pop()

            if atual == self.objetivo:
                return caminho

            if atual in visitados:
                continue

            visitados.add(atual)

            for viz in self.vizinhos_livres(atual):
                if viz not in visitados:
                    pilha.append((viz, caminho + [viz]))

        return []  

    def busca_bfs(self):
        
        fila = deque([(self.posicao_inicial, [self.posicao_inicial])])
        visitados = set([self.posicao_inicial])

        while fila:
            atual, caminho = fila.popleft()

            if atual == self.objetivo:
                return caminho

            for viz in self.vizinhos_livres(atual):
                if viz not in visitados:
                    visitados.add(viz)
                    fila.append((viz, caminho + [viz]))

        return [] 

    def calcular_caminho(self):
        
        if self.modo_busca == "dfs":
            return self.busca_dfs()
        elif self.modo_busca == "bfs":
            return self.busca_bfs()
        else:
            raise ValueError(f"Modo de busca inválido: {self.modo_busca}. Use 'dfs' ou 'bfs'.")

    def decidir(self, percepcoes):
        
        if not self.caminho_calculado:
            self.caminho_planejado = self.calcular_caminho()
            self.caminho_calculado = True
            self.indice_caminho = 0
            
            if not self.caminho_planejado:
                return None  
        
        
        if self.posicao_atual == self.objetivo:
            return None
        
      
        if self.indice_caminho < len(self.caminho_planejado) - 1:
            self.indice_caminho += 1
            proxima_posicao = self.caminho_planejado[self.indice_caminho]
            
            
            y, x = self.posicao_atual
            movimento = (proxima_posicao[0] - y, proxima_posicao[1] - x)
            return movimento
        
        return None
    
    def mover(self, movimento):
        
        if movimento:
            y, x = self.posicao_atual
            dy, dx = movimento
            self.posicao_atual = (y + dy, x + dx)
        return self.posicao_atual



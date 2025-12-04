class AgenteReativoBaseadoEmModelo:
    def __init__(self, labirinto_matriz_referencia, posicao_inicial):
        # Mapeamento de vetores de movimento (dy, dx)
        # N, L, S, O
        self.deltas = [(-1, 0), (0, 1), (1, 0), (0, -1)] 
        
        # --- MODELO INTERNO & VARIÁVEIS DE ESTADO ---
        self.posicao_atual = posicao_inicial
        
        linhas = len(labirinto_matriz_referencia)
        colunas = len(labirinto_matriz_referencia[0])
        
        # Cache de dimensões e direções para evitar recomputações
        self.linhas = linhas
        self.colunas = colunas
        self.direcoes = {'N': (-1, 0), 'S': (1, 0), 'L': (0, 1), 'O': (0, -1)}
        
        # 1. Modelo de Visitas (Contagem de quantas vezes cada célula foi visitada)
        # 0 = não visitado
        self.memoria_visitados = [[0] * colunas for _ in range(linhas)]
        
        # 2. Modelo do Labirinto Construído (Memória do que ele viu)
        # 0=Caminho Livre, 1=Parede, 2=Início, 3=Fim, -1=Desconhecido/Não Visto
        self.modelo_labirinto = [[-1] * colunas for _ in range(linhas)]
        
        # Marca a posição inicial como visitada e registra seu conteúdo (2)
        r, c = posicao_inicial
        self.memoria_visitados[r][c] = 1 
        # O agente sabe onde começou. Usa o valor real (que deve ser 2)
        self.modelo_labirinto[r][c] = labirinto_matriz_referencia[r][c]

    def atualizar_modelo(self, percepcoes):
        """Atualiza o modelo_labirinto (mapa conhecido) com base nas percepções imediatas."""
        r, c = self.posicao_atual
        
        for dir_key, (dy, dx) in self.direcoes.items():
            ny, nx = r + dy, c + dx
            
            # Verifica se a posição percebida está dentro dos limites da matriz
            if 0 <= ny < self.linhas and 0 <= nx < self.colunas:
                # A percepção é o valor (0, 1, 2, ou 3) da célula vizinha
                valor_percebido = percepcoes[dir_key]
                
                # Se for uma célula 'nova' (Desconhecida = -1) no modelo, ou se for o objetivo (3),
                # ou uma parede (1) que ainda não foi registrada, ele a registra.
                if self.modelo_labirinto[ny][nx] == -1 or valor_percebido != self.modelo_labirinto[ny][nx]:
                    self.modelo_labirinto[ny][nx] = valor_percebido

    def mover(self, movimento):
        """Atualiza a posição do agente e a contagem de visitas na memória."""
        y, x = self.posicao_atual
        
        if movimento:
            dy, dx = movimento
            ny, nx = y + dy, x + dx
            
            # Checagem defensiva: limites e não-parede segundo o modelo
            if 0 <= ny < self.linhas and 0 <= nx < self.colunas and self.modelo_labirinto[ny][nx] != 1:
                self.posicao_atual = (ny, nx)
                self.memoria_visitados[ny][nx] += 1
                return self.posicao_atual
            else:
                return self.posicao_atual
        
        return self.posicao_atual

    def decidir(self, percepcoes):
        """
        Lógica Baseada em Modelo Apropriada.
        Usa a memória (modelo_labirinto e memoria_visitados) para decidir.
        """
        
        # PASSO 1: Atualiza o Modelo Interno (Memória) com o que foi percebido
        self.atualizar_modelo(percepcoes) 
        
        r, c = self.posicao_atual
        vizinhos_info = []
        
        # 1. Definir Vizinhos e Obter Dados da MEMÓRIA
        for direcao_abs, (dy, dx) in enumerate(self.deltas):
            vr, vc = r + dy, c + dx
            
            # Checa se o vizinho está nos limites da MEMÓRIA
            if 0 <= vr < self.linhas and 0 <= vc < self.colunas:
                
                # Usa o modelo do labirinto (Memória) para ver o conteúdo
                conteudo_do_modelo = self.modelo_labirinto[vr][vc]
                
                # O agente SÓ pode se mover para células que ele conhece como não-parede (0, 2, 3 ou -1)
                # O valor -1 significa 'desconhecido', mas como o modelo foi atualizado com a percepção, 
                # se a percepção indicou 'parede' (1), o modelo já tem 1. 
                # Se a percepção indicou 'caminho' (0/3), o modelo tem 0/3.
                if conteudo_do_modelo != 1: 
                    vizinhos_info.append({
                        'posicao': (vr, vc),
                        'conteudo': conteudo_do_modelo,
                        'contagem_visitas': self.memoria_visitados[vr][vc],
                        'direcao_abs': direcao_abs
                    })
        
        # 2. Aplicar Regras de Decisão (em ordem de prioridade)

        # Regra A: Encontrou o Objetivo (3)
        for info in vizinhos_info:
            if info['conteudo'] == 3:
                return (info['posicao'][0] - r, info['posicao'][1] - c)

        # Regra B: Priorizar Células NUNCA visitadas (Contagem = 0)
        nao_visitados = [info for info in vizinhos_info if info['contagem_visitas'] == 0]
        
        if nao_visitados:
            # Quebra de empate: Prioridade de exploração N, L, S, O
            prioridade_exploracao = [0, 1, 2, 3] 
            
            for direcao_abs in prioridade_exploracao:
                for info in nao_visitados:
                    if info['direcao_abs'] == direcao_abs:
                        posicao = info['posicao']
                        return (posicao[0] - r, posicao[1] - c)

        # Regra C: Backtracking Inteligente (Escolher o MENOS visitado)
        if vizinhos_info:
            melhor_movimento = min(vizinhos_info, key=lambda m: m['contagem_visitas'])
            posicao = melhor_movimento['posicao']
            return (posicao[0] - r, posicao[1] - c)

        # Se não há para onde ir
        return None
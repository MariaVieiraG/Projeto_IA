# Arquivo: AgenteReativoBaseadoEmModelo/agente_modelo.py

class AgenteReativoBaseadoEmModelo:
    def __init__(self, labirinto, posicao_inicial):
        # Mapeamento de vetores de movimento (dy, dx)
        self.deltas = [(-1, 0), (0, 1), (1, 0), (0, -1)] 
        self.mapa_abs_dir = {'N': 0, 'L': 1, 'S': 2, 'O': 3}
        self.dir_atual = 1 # Estado Interno: Direção atual (mantido do agente simples)
        
        # --- NOVO: MODELO INTERNO (MEMÓRIA DE VISITAS) ---
        self.posicao_atual = posicao_inicial
        
        linhas = len(labirinto)
        colunas = len(labirinto[0])
        
        # Cria a matriz para rastrear a contagem de visitas (0 = não visitado)
        self.memoria_visitados = [[0] * colunas for _ in range(linhas)]
        
        # Marca a posição inicial como visitada
        r, c = posicao_inicial
        self.memoria_visitados[r][c] = 1 
        
    def get_percepcao_por_indice(self, percepcoes, indice_abs):
        """Traduz o índice absoluto para a chave de percepção e retorna o valor."""
        for chave, indice in self.mapa_abs_dir.items():
            if indice == indice_abs:
                return percepcoes.get(chave, 1) 
        return 1 

    def mover(self, movimento):
        """
        Move o agente, atualiza a posição e o MODELO INTERNO.
        Retorna a nova posição (y, x).
        """
        y, x = self.posicao_atual
        
        if movimento:
            dy, dx = movimento
            nova_posicao = (y + dy, x + dx)
            
            # --- ATUALIZAÇÃO DO MODELO ---
            self.posicao_atual = nova_posicao
            r, c = nova_posicao
            self.memoria_visitados[r][c] += 1 # Incrementa o contador de visitas
            
            return nova_posicao
            
        return self.posicao_atual # Retorna a mesma posição se o movimento for nulo

    def decidir(self, percepcoes, labirinto):
        """
        Lógica Baseada em Modelo: Exploração por Menor Visita.
        Prioriza: Objetivo > Nunca Visitado (0) > Menos Visitado
        """
        r, c = self.posicao_atual
        
        # 1. Definir Vizinhos e Obter Percepções/Dados da Memória
        vizinhos_info = []
        for direcao_abs, (dy, dx) in enumerate(self.deltas):
            vr, vc = r + dy, c + dx
            
            # Garante que a coordenada está dentro dos limites e não é parede (valor 1)
            if 0 <= vr < len(labirinto) and 0 <= vc < len(labirinto[0]) and labirinto[vr][vc] != 1:
                
                # Coleta as informações cruciais para a decisão:
                vizinhos_info.append({
                    'posicao': (vr, vc),
                    'conteudo': labirinto[vr][vc], # 0, 2 (Entrada), ou 3 (Saída)
                    'contagem_visitas': self.memoria_visitados[vr][vc], # Modelo Interno
                    'direcao_abs': direcao_abs
                })
        
        # 2. Aplicar Regras de Decisão (em ordem de prioridade)

        # Regra A: Encontrou o Objetivo (3)
        for info in vizinhos_info:
            if info['conteudo'] == 3:
                # O agente não precisa mudar a direção interna (dir_atual) se for só ir para o objetivo
                return (info['posicao'][0] - r, info['posicao'][1] - c)

        # Regra B: Priorizar Células NUNCA visitadas (Contagem = 0)
        nao_visitados = [info for info in vizinhos_info if info['contagem_visitas'] == 0]
        if nao_visitados:
            # Escolhe o primeiro movimento não visitado (Exploração)
            posicao = nao_visitados[0]['posicao']
            return (posicao[0] - r, posicao[1] - c)

        # Regra C: Backtracking Inteligente (Escolher o MENOS visitado)
        if vizinhos_info:
            # Encontra o vizinho com o menor contador de visitas (Backtracking)
            melhor_movimento = min(vizinhos_info, key=lambda m: m['contagem_visitas'])
            posicao = melhor_movimento['posicao']
            return (posicao[0] - r, posicao[1] - c)

        # Caso de erro ou beco sem saída absoluto
        return None


        
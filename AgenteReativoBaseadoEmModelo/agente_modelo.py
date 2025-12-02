# Arquivo: AgenteReativoBaseadoEmModelo/agente_modelo.py

class AgenteReativoBaseadoEmModelo:
    def __init__(self, labirinto, posicao_inicial):
        # Mapeamento de vetores de movimento (dy, dx)
        self.deltas = [(-1, 0), (0, 1), (1, 0), (0, -1)] # 0:N, 1:L, 2:S, 3:O
        self.mapa_abs_dir = {'N': 0, 'L': 1, 'S': 2, 'O': 3}
        self.dir_atual = 1 # Mantido por consistência, embora a decisão seja absoluta
        
        # --- MODELO INTERNO & VARIÁVEIS DE ESTADO ---
        self.posicao_atual = posicao_inicial
        
        linhas = len(labirinto)
        colunas = len(labirinto[0])
        
        # Matriz para rastrear a contagem de visitas (0 = não visitado)
        self.memoria_visitados = [[0] * colunas for _ in range(linhas)]
        
        # Marca a posição inicial como visitada
        r, c = posicao_inicial
        self.memoria_visitados[r][c] = 1 
        
    def get_percepcao_por_indice(self, percepcoes, indice_abs):
        # ... (Mantido)
        for chave, indice in self.mapa_abs_dir.items():
            if indice == indice_abs:
                return percepcoes.get(chave, 1) 
        return 1 

    def mover(self, movimento):
        # ... (Mantido)
        y, x = self.posicao_atual
        
        if movimento:
            dy, dx = movimento
            nova_posicao = (y + dy, x + dx)
            
            self.posicao_atual = nova_posicao
            r, c = nova_posicao
            self.memoria_visitados[r][c] += 1
            
            # O Agente Simples usava self.dir_atual. Mantemos a atualização aqui para consistência.
            # Lógica para atualizar self.dir_atual baseada no delta do movimento:
            try:
                self.dir_atual = self.deltas.index(movimento)
            except ValueError:
                pass # Caso o delta não esteja na lista (não deve acontecer)
            
            return nova_posicao
            
        return self.posicao_atual

    def decidir(self, percepcoes, labirinto):
        """
        Lógica Baseada em Modelo MELHORADA (Puramente Reativa).
        Prioriza: Objetivo > Explorar Não Visitado (Prioridade Direcional) > Backtrack (Menos Visitado)
        """
        r, c = self.posicao_atual
        vizinhos_info = []
        
        # 1. Definir Vizinhos e Obter Percepções/Dados da Memória
        for direcao_abs, (dy, dx) in enumerate(self.deltas):
            vr, vc = r + dy, c + dx
            
            if 0 <= vr < len(labirinto) and 0 <= vc < len(labirinto[0]) and labirinto[vr][vc] != 1:
                
                vizinhos_info.append({
                    'posicao': (vr, vc),
                    'conteudo': labirinto[vr][vc],
                    'contagem_visitas': self.memoria_visitados[vr][vc],
                    'direcao_abs': direcao_abs
                })
        
        # 2. Aplicar Regras de Decisão (em ordem de prioridade)

        # Regra A: Encontrou o Objetivo (3)
        for info in vizinhos_info:
            if info['conteudo'] == 3:
                return (info['posicao'][0] - r, info['posicao'][1] - c)

        # Regra B: Priorizar Células NUNCA visitadas (Contagem = 0) - CORREÇÃO DE DESEMPENHO
        nao_visitados = [info for info in vizinhos_info if info['contagem_visitas'] == 0]
        
        if nao_visitados:
            # CORREÇÃO: Usar a ordem direcional para quebrar o empate e evitar a exploração cega.
            # Ordem: 1: Leste (Frente/Direita Comum), 2: Sul, 0: Norte, 3: Oeste (Voltar)
            prioridade_exploracao = [1, 2, 0, 3] 
            
            movimento_escolhido = None
            
            for direcao_abs in prioridade_exploracao:
                for info in nao_visitados:
                    if info['direcao_abs'] == direcao_abs:
                        movimento_escolhido = info
                        break
                if movimento_escolhido:
                    break
            
            posicao = movimento_escolhido['posicao']
            return (posicao[0] - r, posicao[1] - c)

        # Regra C: Backtracking Inteligente (Escolher o MENOS visitado)
        if vizinhos_info:
            # Se todos já foram visitados, escolhemos o com o menor contador de visitas.
            melhor_movimento = min(vizinhos_info, key=lambda m: m['contagem_visitas'])
            posicao = melhor_movimento['posicao']
            return (posicao[0] - r, posicao[1] - c)

        return None
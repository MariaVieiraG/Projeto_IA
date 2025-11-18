class AgenteReativoSimples:
    def __init__(self):
        # Mapeamento de vetores de movimento (dy, dx)
        # 0: Norte (-1, 0), 1: Leste (0, 1), 2: Sul (1, 0), 3: Oeste (0, -1)
        self.deltas = [(-1, 0), (0, 1), (1, 0), (0, -1)] 
        
        # Mapeamento para ligar as percepções absolutas ('N', 'S', 'L', 'O') aos índices do delta (0, 1, 2, 3)
        self.mapa_abs_dir = {'N': 0, 'L': 1, 'S': 2, 'O': 3}
        
        # Estado Interno: Direção atual que o agente está virado (inicialmente Leste)
        self.dir_atual = 1 

    def get_percepcao_por_indice(self, percepcoes, indice_abs):
        """Traduz o índice absoluto para a chave de percepção ('N', 'L', 'S', 'O') e retorna o valor (1=parede, 0=livre, etc)."""
        for chave, indice in self.mapa_abs_dir.items():
            if indice == indice_abs:
                # Usa .get para evitar erros, assume 1 (parede) se a chave faltar
                return percepcoes.get(chave, 1) 
        return 1 

    def decidir(self, percepcoes):
        """
        Lógica Reativa: Regra da Mão Direita.
        Prioridade: Direita > Frente > Esquerda > 180º
        """
        idx_frente = self.dir_atual
        idx_direita = (self.dir_atual + 1) % 4
        idx_esquerda = (self.dir_atual - 1) % 4
        idx_atras = (self.dir_atual + 2) % 4

        # Checa se o caminho nessas direções está livre (valor != 1)
        direita_livre = self.get_percepcao_por_indice(percepcoes, idx_direita) != 1
        frente_livre = self.get_percepcao_por_indice(percepcoes, idx_frente) != 1
        esquerda_livre = self.get_percepcao_por_indice(percepcoes, idx_esquerda) != 1

        # 1. Tenta virar à direita
        if direita_livre:
            self.dir_atual = idx_direita
            return self.deltas[self.dir_atual]
        # 2. Tenta ir em frente
        elif frente_livre:
            return self.deltas[self.dir_atual]
        # 3. Tenta virar à esquerda
        elif esquerda_livre:
            self.dir_atual = idx_esquerda
            return self.deltas[self.dir_atual]
        # 4. Beco sem saída: vira 180 graus (retorna na direção de trás)
        else:
            self.dir_atual = idx_atras
            return self.deltas[self.dir_atual]

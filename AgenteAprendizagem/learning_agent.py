# learning_agent.py

import random
from collections import defaultdict, deque
import time
import math # Para math.fsum, que substitui np.sum para média


class QLearningAgent:
    """
    Agente de Aprendizagem usando Q-Learning Melhorado.
    (Adaptado para rodar sem a biblioteca NumPy)
    """

    def __init__(
            self,
            alpha: float = 0.3,  # Taxa de aprendizado
            gamma: float = 0.99,  # Fator de desconto
            epsilon: float = 1.0,  # Taxa de exploração inicial
            epsilon_min: float = 0.05,  # Taxa mínima de exploração
            epsilon_decay: float = 0.998,  # Decaimento
            lambda_trace: float = 0.9  # Fator de elegibilidade para Q(λ)
    ):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.lambda_trace = lambda_trace

        self.q_table = defaultdict(lambda: defaultdict(float))
        self.e_traces = defaultdict(lambda: defaultdict(float))
        self.actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.action_names = ['CIMA', 'BAIXO', 'ESQUERDA', 'DIREITA']

        self.metrics = {
            'episodes': [],
            'steps_per_episode': [],
            'rewards_per_episode': [],
            'epsilon_history': [],
            'success_history': []
        }

        self.distance_cache = None
        self.goal = None

    def compute_distance_map(self, maze: list, goal: tuple):
        """
        Pré-computa distâncias de todas as células até o objetivo usando BFS.
        Adaptado para usar listas puras de Python.
        """
        if self.goal == goal and self.distance_cache is not None:
            return

        self.goal = goal
        self.distance_cache = {}

        rows, cols = len(maze), len(maze[0])
        queue = deque([goal])
        self.distance_cache[goal] = 0

        while queue:
            current = queue.popleft()
            current_dist = self.distance_cache[current]

            for dr, dc in self.actions:
                nr, nc = current[0] + dr, current[1] + dc
                next_pos = (nr, nc)

                # Verifica limites e parede usando lista de listas (maze[nr][nc])
                if (0 <= nr < rows and 0 <= nc < cols and
                        maze[nr][nc] != 1 and next_pos not in self.distance_cache):
                    self.distance_cache[next_pos] = current_dist + 1
                    queue.append(next_pos)

    def get_valid_actions(self, maze: list, state: tuple) -> list:
        """Retorna ações válidas (que não colidem com paredes)."""
        valid = []
        row, col = state
        rows, cols = len(maze), len(maze[0])

        for i, (dr, dc) in enumerate(self.actions):
            new_row, new_col = row + dr, col + dc
            # Indexação da matriz usando lista pura (maze[new_row][new_col])
            if (0 <= new_row < rows and
                    0 <= new_col < cols and
                    maze[new_row][new_col] != 1):
                valid.append(i)

        return valid

    def choose_action(self, maze: list, state: tuple, visited_count: dict = None) -> int:
        """
        Escolhe ação usando política ε-greedy com bonus de exploração.
        """
        valid_actions = self.get_valid_actions(maze, state)

        if not valid_actions:
            return None

        # Exploração
        if random.random() < self.epsilon:
            # Exploração inteligente: prefere estados menos visitados
            if visited_count:
                action_scores = []
                for a in valid_actions:
                    dr, dc = self.actions[a]
                    next_state = (state[0] + dr, state[1] + dc)
                    visit_penalty = visited_count.get(next_state, 0)
                    action_scores.append((a, -visit_penalty + random.random() * 0.1))
                action_scores.sort(key=lambda x: x[1], reverse=True)
                return action_scores[0][0]
            return random.choice(valid_actions)

        # Explotação: escolhe a melhor ação válida
        q_values = [self.q_table[state][a] for a in valid_actions]
        
        # Substitui np.max por max() nativo
        if not q_values: 
             return random.choice(valid_actions) # Fallback se houver bug de lógica
        max_q = max(q_values)

        # Se houver empate, escolhe aleatoriamente entre as melhores
        best_actions = [a for a, q in zip(valid_actions, q_values) if q == max_q]
        return random.choice(best_actions)

    def get_reward(self, maze: list, state: tuple, next_state: tuple,
                   goal: tuple, hit_wall: bool) -> float:
        """
        Sistema de recompensas melhorado com reward shaping.
        """
        if next_state == goal:
            return 1000.0

        if hit_wall:
            return -5.0

        reward = -1.0

        if self.distance_cache:
            old_dist = self.distance_cache.get(state, float('inf'))
            new_dist = self.distance_cache.get(next_state, float('inf'))

            if new_dist < old_dist:
                reward += 5.0
            elif new_dist > old_dist:
                reward -= 2.0

        return reward

    def reset_eligibility_traces(self):
        """Reseta as eligibility traces."""
        self.e_traces = defaultdict(lambda: defaultdict(float))

    def update_q_value_with_traces(self, state: tuple, action: int, reward: float,
                                   next_state: tuple, next_action: int, done: bool):
        """
        Atualiza o valor Q usando Q(λ) com eligibility traces.
        """
        current_q = self.q_table[state][action]

        if done:
            td_error = reward - current_q
        else:
            next_q = self.q_table[next_state][next_action] if next_action is not None else 0
            td_error = reward + self.gamma * next_q - current_q

        self.e_traces[state][action] += 1.0

        for s in list(self.e_traces.keys()):
            for a in list(self.e_traces[s].keys()):
                self.q_table[s][a] += self.alpha * td_error * self.e_traces[s][a]
                self.e_traces[s][a] *= self.gamma * self.lambda_trace

                if self.e_traces[s][a] < 0.001:
                    del self.e_traces[s][a]
            if not self.e_traces[s]:
                del self.e_traces[s]

    def decay_epsilon(self, success_rate: float = 0.0):
        """
        Reduz a taxa de exploração de forma adaptativa.
        """
        if success_rate < 0.1:
            # Substitui np.power(self.epsilon_decay, 0.5) por math.pow() ou **
            decay = math.pow(self.epsilon_decay, 0.5)
        else:
            decay = self.epsilon_decay

        self.epsilon = max(self.epsilon_min, self.epsilon * decay)

    def train(
            self,
            maze: list,
            start: tuple,
            goal: tuple,
            episodes: int = 2000,
            max_steps: int = 5000,
            verbose: bool = True
    ) -> dict:
        """
        Treina o agente no labirinto com Q(λ).
        """
        start_time = time.time()

        # Pré-computa mapa de distâncias para reward shaping
        self.compute_distance_map(maze, goal)
        
        # Substitui maze.shape[0] e maze.shape[1] por len()
        rows, cols = len(maze), len(maze[0])
        
        # Verifica se o objetivo é alcançável
        if start not in self.distance_cache:
            print("AVISO: Posição inicial não conectada ao objetivo!")
            return {
                'training_time': 0,
                'total_episodes': 0,
                'final_epsilon': self.epsilon,
                'metrics': self.metrics
            }

        successes = 0
        recent_successes = deque(maxlen=100)
        
        # Variável para acumular passos e recompensas para o log de média
        log_steps = []
        log_rewards = []

        for episode in range(episodes):
            state = start
            total_reward = 0
            steps = 0
            visited_count = defaultdict(int)

            self.reset_eligibility_traces()

            action = self.choose_action(maze, state, visited_count)

            success = False

            for step in range(max_steps):
                if action is None:
                    break

                visited_count[state] += 1

                # Executa ação
                dr, dc = self.actions[action]
                new_row, new_col = state[0] + dr, state[1] + dc

                hit_wall = False
                # Substitui maze.shape[0/1] por rows/cols e indexação maze[new_row][new_col]
                if (0 <= new_row < rows and
                        0 <= new_col < cols and
                        maze[new_row][new_col] != 1):
                    next_state = (new_row, new_col)
                else:
                    next_state = state
                    hit_wall = True

                # Calcula recompensa
                done = next_state == goal
                reward = self.get_reward(maze, state, next_state, goal, hit_wall)
                total_reward += reward

                next_action = self.choose_action(maze, next_state, visited_count) if not done else None

                self.update_q_value_with_traces(state, action, reward, next_state, next_action, done)

                state = next_state
                action = next_action
                steps += 1

                if done:
                    success = True
                    successes += 1
                    break

            recent_successes.append(1 if success else 0)
            # Substitui sum(recent_successes) por math.fsum
            success_rate = math.fsum(recent_successes) / len(recent_successes)

            self.decay_epsilon(success_rate)

            # Registra métricas
            self.metrics['episodes'].append(episode)
            self.metrics['steps_per_episode'].append(steps)
            self.metrics['rewards_per_episode'].append(total_reward)
            self.metrics['epsilon_history'].append(self.epsilon)
            self.metrics['success_history'].append(success)
            
            # Log de progresso
            if verbose and (episode + 1) % 100 == 0:
                # Usa média de lista pura (substituindo np.mean)
                avg_steps = math.fsum(self.metrics['steps_per_episode'][-100:]) / 100
                avg_reward = math.fsum(self.metrics['rewards_per_episode'][-100:]) / 100
                print(f"Episódio {episode + 1}/{episodes} | "
                    f"Passos médios: {avg_steps:.1f} | "
                    f"Recompensa média: {avg_reward:.1f} | "
                    f"ε: {self.epsilon:.3f} | "
                    f"Taxa sucesso: {success_rate:.1%}")

            if success_rate > 0.95 and episode > 500:
                if verbose:
                    print(f"Convergência atingida no episódio {episode + 1}!")
                break

        training_time = time.time() - start_time

        return {
            'training_time': training_time,
            'total_episodes': episode + 1,
            'final_epsilon': self.epsilon,
            'total_successes': successes,
            'metrics': self.metrics
        }

    def get_optimal_path(self, maze: list, start: tuple, goal: tuple, max_steps: int = 5000) -> list:
        """
        Retorna o caminho ótimo aprendido (sem exploração).
        """
        path = [start]
        state = start
        visited = set([start])

        for _ in range(max_steps):
            if state == goal:
                break

            valid_actions = self.get_valid_actions(maze, state)
            if not valid_actions:
                break

            q_values = [(a, self.q_table[state][a]) for a in valid_actions]
            
            # Escolhe a melhor ação (greedy) - max() nativo
            best_action = max(q_values, key=lambda x: x[1])[0]

            dr, dc = self.actions[best_action]
            next_state = (state[0] + dr, state[1] + dc)

            # Evita loops
            if next_state in visited:
                # Tenta outra ação
                alternatives = [(a, q) for a, q in q_values if
                                (state[0] + self.actions[a][0],
                                state[1] + self.actions[a][1]) not in visited]
                if alternatives:
                    best_action = max(alternatives, key=lambda x: x[1])[0]
                    dr, dc = self.actions[best_action]
                    next_state = (state[0] + dr, state[1] + dc)
                else:
                    break

            visited.add(next_state)
            path.append(next_state)
            state = next_state

        return path

    def solve(self, maze: list, start: tuple, goal: tuple) -> dict:
        """
        Interface padrão para resolver o labirinto.
        Treina se necessário e retorna o caminho.
        """
        # Treina o agente
        training_results = self.train(maze, start, goal)

        # Obtém caminho ótimo
        path = self.get_optimal_path(maze, start, goal)

        return {
            'path': path,
            'path_length': len(path),
            'training_time': training_results['training_time'],
            'episodes': training_results['total_episodes'],
            'success': path[-1] == goal if path else False,
            'metrics': training_results['metrics']
        }
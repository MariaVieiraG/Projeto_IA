# test_learning_agent.py

from learning_agent import QLearningAgent
from maze_loader import load_maze
import matplotlib.pyplot as plt


def plot_metrics(metrics: dict, maze_name: str):
    """Plota métricas de aprendizado."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # Passos por episódio
    axes[0, 0].plot(metrics['steps_per_episode'])
    axes[0, 0].set_title('Passos por Episódio')
    axes[0, 0].set_xlabel('Episódio')
    axes[0, 0].set_ylabel('Passos')

    # Média móvel dos passos
    window = 50
    if len(metrics['steps_per_episode']) >= window:
        moving_avg = np.convolve(
            metrics['steps_per_episode'],
            np.ones(window) / window,
            mode='valid'
        )
        axes[0, 1].plot(moving_avg)
        axes[0, 1].set_title(f'Média Móvel de Passos (janela={window})')

    # Recompensa por episódio
    axes[1, 0].plot(metrics['rewards_per_episode'])
    axes[1, 0].set_title('Recompensa por Episódio')

    # Epsilon
    axes[1, 1].plot(metrics['epsilon_history'])
    axes[1, 1].set_title('Decaimento do Epsilon')

    plt.suptitle(f'Métricas de Aprendizado - {maze_name}')
    plt.tight_layout()
    plt.savefig(f'metrics_{maze_name}.png')
    plt.show()


if __name__ == "__main__":
    # Testa com um labirinto
    maze, start, goal = load_maze('labirinto_espiral.txt')

    print(f"Labirinto: {maze.shape}")
    print(f"Início: {start}")
    print(f"Objetivo: {goal}")

    agent = QLearningAgent(
        alpha=0.2,
        gamma=0.95,
        epsilon=1.0,
        epsilon_decay=0.995
    )

    result = agent.solve(maze, start, goal)

    print(f"\nResultados:")
    print(f"Sucesso: {result['success']}")
    print(f"Tamanho do caminho: {result['path_length']}")
    print(f"Tempo de treinamento: {result['training_time']:.2f}s")

    plot_metrics(result['metrics'], 'espiral')
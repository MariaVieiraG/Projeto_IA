# maze_loader.py

import numpy as np


def load_maze(filepath: str) -> tuple:
    """
    Carrega labirinto de arquivo .txt

    Returns:
        (maze, start, goal)
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()

    maze = []
    start = None
    goal = None

    for i, line in enumerate(lines):
        row = [int(x) for x in line.strip().split()]
        maze.append(row)

        for j, cell in enumerate(row):
            if cell == 2:
                start = (i, j)
            elif cell == 3:
                goal = (i, j)

    maze = np.array(maze)

    # Se não tiver marcadores explícitos, usa primeira/última célula livre
    if start is None:
        for i in range(maze.shape[0]):
            for j in range(maze.shape[1]):
                if maze[i, j] == 0:
                    start = (i, j)
                    break
            if start:
                break

    if goal is None:
        for i in range(maze.shape[0] - 1, -1, -1):
            for j in range(maze.shape[1] - 1, -1, -1):
                if maze[i, j] == 0:
                    goal = (i, j)
                    break
            if goal:
                break

    return maze, start, goal
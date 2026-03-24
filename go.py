import pygame
import sys
import math
import random

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer  # Используем локальный симулятор
# Qiskit Runtime (оставляем для возможности переключения)
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Session

# ========== 1) НАСТРОЙКА: ЛОКАЛЬНЫЙ СИМУЛЯТОР ==========
backend = Aer.get_backend("qasm_simulator")
print("Используем локальный симулятор:", backend.name)

# ========== ГЛОБАЛЫЕ ПЕРЕМЕННЫЕ ДЛЯ КВАНТОВОЙ СЛУЧАЙНОСТИ ==========
global_qr_cache = []
global_qr_index = 0


def _simulate_shots(prob_dict, shots, max_val):
    items = list(prob_dict.items())
    clipped = []
    for s, p in items:
        if p < 0:
            p = 0.0
        clipped.append((s, p))
    total_prob = sum(p for _, p in clipped)
    if total_prob == 0:
        clipped = [(0, 1.0)]
        total_prob = 1.0
    distribution = []
    csum = 0.0
    for st, p in clipped:
        if p <= 0:
            continue
        start = csum
        end = start + p
        distribution.append((st, start, end))
        csum = end
    results = []
    for _ in range(shots):
        r = random.random() * total_prob
        for st, st_start, st_end in distribution:
            if st_start <= r < st_end:
                results.append(st % max_val)
                break
    return results


def get_universal_quantum_random_numbers(count=1000, nbits=16):
    qc = QuantumCircuit(nbits)
    for i in range(nbits):
        qc.h(i)
    qc.measure_all()
    qc = transpile(qc, backend=backend, basis_gates=backend.configuration().basis_gates)
    job = backend.run(qc, shots=count)
    result = job.result()
    counts = result.get_counts(qc)
    total = sum(counts.values())
    prob_dict = {int(k, 2): v / total for k, v in counts.items()}
    return _simulate_shots(prob_dict, count, 2 ** nbits)


def universal_quantum_randint(max_val, shots=1000, nbits=16):
    if max_val <= 0:
        return 0
    global global_qr_cache, global_qr_index
    if len(global_qr_cache) - global_qr_index < 10:
        global_qr_cache = get_universal_quantum_random_numbers(count=shots, nbits=nbits)
        global_qr_index = 0
    val = global_qr_cache[global_qr_index]
    global_qr_index += 1
    return val % max_val


def clear_qr_cache():
    global global_qr_cache, global_qr_index
    global_qr_cache = []
    global_qr_index = 0


# ========== 2) ГЕНЕРАЦИЯ ЛАБИРИНТА (Recursive Backtracking) ==========
def generate_maze(rows, cols):
    # Сбрасываем кэш квантовых чисел, чтобы каждый новый лабиринт генерировался с новыми данными
    clear_qr_cache()

    # Итоговая ASCII карта будет размером (2*rows+1)x(2*cols+1)
    H = 2 * rows + 1
    W = 2 * cols + 1
    maze = [['#' for _ in range(W)] for _ in range(H)]

    def cell_to_ascii(r, c):
        return (2 * r + 1, 2 * c + 1)

    visited = [[False] * cols for _ in range(rows)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def neighbors(r, c):
        nbrs = []
        for dr, dc in directions:
            nr = r + dr
            nc = c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                nbrs.append((nr, nc))
        return nbrs

    start_r = universal_quantum_randint(rows)
    start_c = universal_quantum_randint(cols)
    visited[start_r][start_c] = True
    sr_ascii, sc_ascii = cell_to_ascii(start_r, start_c)
    maze[sr_ascii][sc_ascii] = ' '

    stack = [(start_r, start_c)]

    while stack:
        cr, cc = stack[-1]
        nbrs = neighbors(cr, cc)
        if nbrs:
            idx = universal_quantum_randint(len(nbrs))
            nr, nc = nbrs[idx]
            visited[nr][nc] = True
            r1, c1 = cell_to_ascii(cr, cc)
            r2, c2 = cell_to_ascii(nr, nc)
            maze[r2][c2] = ' '
            wall_r = (r1 + r2) // 2
            wall_c = (c1 + c2) // 2
            maze[wall_r][wall_c] = ' '
            stack.append((nr, nc))
        else:
            stack.pop()

    # ========== Расставляем телепорты (A..E) ==========
    pass_cells = [(r, c) for r in range(H) for c in range(W) if maze[r][c] == ' ']
    tele_letters = ['A', 'B', 'C', 'D', 'E']
    if len(pass_cells) >= 10:
        for letter in tele_letters:
            idx1 = universal_quantum_randint(len(pass_cells))
            r1, c1 = pass_cells[idx1]
            pass_cells[idx1], pass_cells[-1] = pass_cells[-1], pass_cells[idx1]
            pass_cells.pop()

            idx2 = universal_quantum_randint(len(pass_cells))
            r2, c2 = pass_cells[idx2]
            pass_cells[idx2], pass_cells[-1] = pass_cells[-1], pass_cells[idx2]
            pass_cells.pop()

            maze[r1][c1] = letter
            maze[r2][c2] = letter

    # ========== Добавляем деревья 'T' ==========
    total_cells = H * W
    tree_count = total_cells // 25
    for _ in range(tree_count):
        rr = universal_quantum_randint(H)
        cc = universal_quantum_randint(W)
        if maze[rr][cc] == ' ':
            maze[rr][cc] = 'T'

    # ========== Размещаем портал выхода 'X' ==========
    if pass_cells:
        idx = universal_quantum_randint(len(pass_cells))
        xr, xc = pass_cells[idx]
        maze[xr][xc] = 'X'
    return maze


# ========== 3) Функции для поиска телепортов и портала ==========
def find_teleports(maze):
    teleports = {}
    for letter in ['A', 'B', 'C', 'D', 'E']:
        teleports[letter] = []
    R = len(maze)
    C = len(maze[0])
    for r in range(R):
        for c in range(C):
            if maze[r][c] in teleports:
                teleports[maze[r][c]].append((r, c))
    return teleports


def find_portal(maze):
    R = len(maze)
    C = len(maze[0])
    for r in range(R):
        for c in range(C):
            if maze[r][c] == 'X':
                return (r, c)
    return None


# ========== 4) ОТОБРАЖЕНИЕ ASCII в PYGAME ==========
CELL_SIZE = 16


def render_ascii_surface(font, maze):
    R = len(maze)
    C = len(maze[0])
    surf_w = C * CELL_SIZE
    surf_h = R * CELL_SIZE
    surface = pygame.Surface((surf_w, surf_h))

    green = (0, 180, 0)  # Стена
    dark_grey = (50, 50, 50)  # Фон
    brown = (139, 69, 19)  # Дерево
    orange = (255, 128, 64)  # Срубленное дерево
    white = (200, 200, 200)  # Проход
    tele_colors = {
        'A': (255, 255, 0),
        'B': (0, 255, 255),
        'C': (255, 128, 0),
        'D': (128, 255, 128),
        'E': (255, 0, 255)
    }
    red = (255, 0, 0)  # Портал выхода

    for r in range(R):
        for c in range(C):
            ch = maze[r][c]
            if ch == '#':
                color = green
            elif ch == 'T':
                color = brown
            elif ch == 't':
                color = orange
            elif ch in tele_colors:
                color = tele_colors[ch]
            elif ch == 'X':
                color = red
            else:
                color = white
            rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, dark_grey, rect)
            text_surf = font.render(ch, True, color)
            surface.blit(text_surf, (c * CELL_SIZE, r * CELL_SIZE))
    return surface


# ========== 5) Геймплей: энергия, портал выхода, деревья и телепорты ==========
def main():
    pygame.init()
    pygame.key.set_repeat(200, 50)

    # Логические размеры лабиринта (используем генерацию через recursive backtracking)
    rows, cols = 10, 20
    H = 2 * rows + 1
    W = 2 * cols + 1

    screen = pygame.display.set_mode((W * CELL_SIZE, H * CELL_SIZE + 32))
    pygame.display.set_caption("Quantum Maze (Energy, Portal, Trees, Teleports)")
    font = pygame.font.SysFont("Courier New", CELL_SIZE)

    maze = generate_maze(rows, cols)
    teleports = find_teleports(maze)
    portal = find_portal(maze)
    maze_surf = render_ascii_surface(font, maze)

    # Игрок: стартуем из клетки (1,1), если это проход, иначе устанавливаем в ближайшую
    player_r, player_c = 1, 1
    if maze[player_r][player_c] == '#':
        maze[player_r][player_c] = ' '

    energy = 100  # Начальная энергия
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                nr, nc = player_r, player_c
                if event.key == pygame.K_w:
                    nr -= 1
                elif event.key == pygame.K_s:
                    nr += 1
                elif event.key == pygame.K_a:
                    nc -= 1
                elif event.key == pygame.K_d:
                    nc += 1

                if 0 <= nr < H and 0 <= nc < W and maze[nr][nc] != '#':
                    player_r, player_c = nr, nc
                    energy -= 1
                    if energy < 0:
                        print("Вы проиграли: закончилась энергия!")
                        running = False
                        break

                    ch = maze[player_r][player_c]

                    # Если на клетке дерево T, получаем энергию, дерево превращается в срубленное (t)
                    if ch == 'T':
                        bonus = universal_quantum_randint(11) + 5  # 5..15 энергии
                        energy += bonus
                        maze[player_r][player_c] = 't'
                        maze_surf = render_ascii_surface(font, maze)
                        print(f"Срублено дерево: +{bonus} энергии")

                    # Если телепорт (A..E), перемещаем игрока и случайно изменяем энергию (-10..+10)
                    elif ch in teleports and len(teleports[ch]) == 2:
                        coords = teleports[ch]
                        if (player_r, player_c) == coords[0]:
                            player_r, player_c = coords[1]
                        else:
                            player_r, player_c = coords[0]
                        delta = universal_quantum_randint(21) - 10
                        energy += delta
                        print(f"Телепорт {ch}: изменение энергии {delta}")
                        if energy < 0:
                            print("Вы проиграли: энергия упала ниже 0 из-за телепорта!")
                            running = False
                            break

                    # Если портал выхода X, проверяем энергию – если энергия > 0, победа
                    elif ch == 'X':
                        if energy > 0:
                            print("Поздравляем! Вы победили, достигнув портала с положительной энергией.")
                        else:
                            print("Вы достигли портала, но у вас 0 энергии. Проигрыш!")
                        running = False
                        break

        screen.fill((0, 0, 0))
        screen.blit(maze_surf, (0, 32))

        # Рисуем игрока '@'
        player_surf = font.render('@', True, (255, 0, 0))
        screen.blit(player_surf, (player_c * CELL_SIZE, player_r * CELL_SIZE + 32))

        # Отображаем энергию
        energy_surf = font.render(f"Energy: {energy}", True, (255, 255, 255))
        screen.blit(energy_surf, (10, 5))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

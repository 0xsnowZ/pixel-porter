#!/usr/bin/env python3
import collections
import random
import sys

def parse_sokoban(text):
    lines = [line.rstrip('\r\n') for line in text.strip().split('\n') if line.strip() and not line.startswith(';')]
    height = len(lines)
    width = max(len(l) for l in lines)
    walls = set()
    goals = set()
    crates = set()
    player = None

    for y, line in enumerate(lines):
        for x, ch in enumerate(line):
            pos = (x, y)
            if ch == '#':
                walls.add(pos)
            elif ch == '.':
                goals.add(pos)
            elif ch == '$':
                crates.add(pos)
            elif ch == '*':
                crates.add(pos)
                goals.add(pos)
            elif ch == '@':
                player = pos
            elif ch == '+':
                player = pos
                goals.add(pos)
    return width, height, walls, goals, crates, player

def format_sokoban(width, height, walls, goals, crates, player):
    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            pos = (x, y)
            if pos in walls:
                row.append('#')
            elif pos in crates and pos in goals:
                row.append('*')
            elif pos in crates:
                row.append('$')
            elif pos == player and pos in goals:
                row.append('+')
            elif pos == player:
                row.append('@')
            elif pos in goals:
                row.append('.')
            else:
                row.append(' ')
        grid.append(''.join(row))
    return '\n'.join(grid)

def solve_sokoban(width, height, walls, goals, crates, player, max_states=40000):
    if crates == goals:
        return True, 0, 0, ""

    # BFS: state is (player_pos, tuple of sorted crate positions)
    dirs = [
        ((0, -1), 'u'),
        ((0, 1), 'd'),
        ((-1, 0), 'l'),
        ((1, 0), 'r')
    ]

    start_crates = tuple(sorted(crates))
    start_state = (player, start_crates)
    queue = collections.deque([(player, start_crates, "", 0)])
    visited = {start_state}

    def is_corner_deadlock(pos, c_set):
        if pos in goals:
            return False
        w_u = (pos[0], pos[1]-1) in walls
        w_d = (pos[0], pos[1]+1) in walls
        w_l = (pos[0]-1, pos[1]) in walls
        w_r = (pos[0]+1, pos[1]) in walls
        if (w_u and w_l) or (w_u and w_r) or (w_d and w_l) or (w_d and w_r):
            return True
        return False

    states_count = 0
    while queue:
        states_count += 1
        if states_count > max_states:
            return False, 0, 0, "TIMEOUT"

        p, c_tuple, moves_str, pushes_count = queue.popleft()
        c_set = set(c_tuple)

        for (dx, dy), m_char in dirs:
            np = (p[0] + dx, p[1] + dy)
            if np in walls or np[0] < 0 or np[0] >= width or np[1] < 0 or np[1] >= height:
                continue

            if np in c_set:
                # Pushing crate
                behind = (np[0] + dx, np[1] + dy)
                if behind in walls or behind in c_set or behind[0] < 0 or behind[0] >= width or behind[1] < 0 or behind[1] >= height:
                    continue
                if is_corner_deadlock(behind, c_set):
                    continue

                new_crates = tuple(sorted((c_set - {np}) | {behind}))
                if set(new_crates) == goals:
                    return True, len(moves_str) + 1, pushes_count + 1, moves_str + m_char

                new_state = (np, new_crates)
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((np, new_crates, moves_str + m_char, pushes_count + 1))
            else:
                # Normal move
                new_state = (np, c_tuple)
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((np, c_tuple, moves_str + m_char, pushes_count))

    return False, 0, 0, "UNSOLVABLE"

if __name__ == '__main__':
    # Test on level 1
    with open("levels/level_01.sok") as f:
        w, h, walls, goals, crates, player = parse_sokoban(f.read())
    solvable, moves, pushes, sol = solve_sokoban(w, h, walls, goals, crates, player)
    print(f"Level 1: Solvable={solvable}, Moves={moves}, Pushes={pushes}, Sol={sol}")

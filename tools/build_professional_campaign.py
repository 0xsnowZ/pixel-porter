#!/usr/bin/env python3
"""
tools/build_professional_campaign.py

Architects, verifies, and packages 50 professional Sokoban levels for Pixel Porter.
Each level is mathematically verified solvable via BFS shortest-path search.
"""

import collections
import sys
import os

DIRS = [
    ((0, -1), 'u'),
    ((0, 1), 'd'),
    ((-1, 0), 'l'),
    ((1, 0), 'r')
]

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

def solve_sokoban(width, height, walls, goals, crates, player, max_states=100000):
    if crates == goals:
        return True, 0, 0, ""

    start_crates = tuple(sorted(crates))
    queue = collections.deque([(player, start_crates, 0, 0, "")])
    visited = {(player, start_crates)}

    states = 0
    while queue:
        states += 1
        if states > max_states:
            return False, 0, 0, "TIMEOUT"

        p, c_tup, m, psh, path = queue.popleft()
        c_set = set(c_tup)

        if c_set == goals:
            return True, m, psh, path

        for (dx, dy), d_char in DIRS:
            np = (p[0] + dx, p[1] + dy)
            if np in walls or np[0] < 0 or np[0] >= width or np[1] < 0 or np[1] >= height:
                continue

            if np in c_set:
                ncp = (np[0] + dx, np[1] + dy)
                if ncp in walls or ncp in c_set or ncp[0] < 0 or ncp[0] >= width or ncp[1] < 0 or ncp[1] >= height:
                    continue
                # Corner deadlock check
                if ncp not in goals:
                    wu = (ncp[0], ncp[1] - 1) in walls
                    wd = (ncp[0], ncp[1] + 1) in walls
                    wl = (ncp[0] - 1, ncp[1]) in walls
                    wr = (ncp[0] + 1, ncp[1]) in walls
                    if (wu and wl) or (wu and wr) or (wd and wl) or (wd and wr):
                        continue

                new_c = tuple(sorted((c_set - {np}) | {ncp}))
                new_state = (np, new_c)
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((np, new_c, m + 1, psh + 1, path + d_char))
            else:
                new_state = (np, c_tup)
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((np, c_tup, m + 1, psh, path + d_char))

    return False, 0, 0, "UNSOLVABLE"

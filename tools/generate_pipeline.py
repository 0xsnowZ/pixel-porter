#!/usr/bin/env python3
import collections
import random
import sys
import os

from benchmark_solver import solve_sokoban, format_sokoban

DIRS = [
    (0, -1), # UP
    (0, 1),  # DOWN
    (-1, 0), # LEFT
    (1, 0)   # RIGHT
]

def generate_room(w, h, num_obstacles=3):
    walls = set()
    for x in range(w):
        walls.add((x, 0))
        walls.add((x, h - 1))
    for y in range(h):
        walls.add((0, y))
        walls.add((w - 1, y))

    interior_cells = [(x, y) for x in range(1, w - 1) for y in range(1, h - 1)]

    # Add some internal pillars / obstacles
    obstacles_added = 0
    random.shuffle(interior_cells)
    for pos in interior_cells:
        if obstacles_added >= num_obstacles:
            break
        # Don't place obstacle right in corners
        if (pos[0] in (1, w-2)) and (pos[1] in (1, h-2)):
            continue
        walls.add(pos)
        # Check flood-fill connectivity of all remaining interior cells
        if not is_connected(w, h, walls):
            walls.remove(pos)
        else:
            obstacles_added += 1

    return walls

def is_connected(w, h, walls):
    interior = [(x, y) for x in range(1, w - 1) for y in range(1, h - 1) if (x, y) not in walls]
    if not interior:
        return False
    start = interior[0]
    visited = {start}
    q = collections.deque([start])
    while q:
        cur = q.popleft()
        for dx, dy in DIRS:
            nbr = (cur[0] + dx, cur[1] + dy)
            if 0 < nbr[0] < w - 1 and 0 < nbr[1] < h - 1 and nbr not in walls and nbr not in visited:
                visited.add(nbr)
                q.append(nbr)
    return len(visited) == len(interior)

def is_corner(pos, walls):
    w_u = (pos[0], pos[1]-1) in walls
    w_d = (pos[0], pos[1]+1) in walls
    w_l = (pos[0]-1, pos[1]) in walls
    w_r = (pos[0]+1, pos[1]) in walls
    return (w_u and w_l) or (w_u and w_r) or (w_d and w_l) or (w_d and w_r)

def generate_candidate(w, h, num_crates, num_obstacles, min_moves=8, max_attempts=150):
    for attempt in range(max_attempts):
        walls = generate_room(w, h, num_obstacles)
        empty_cells = [(x, y) for x in range(1, w - 1) for y in range(1, h - 1) if (x, y) not in walls]

        # Valid goal candidates: preferably not in dead-end corners
        valid_goal_cells = [c for c in empty_cells if not is_corner(c, walls)]
        if len(valid_goal_cells) < num_crates:
            continue

        goals = set(random.sample(valid_goal_cells, num_crates))
        crates = set(goals)

        # Place player adjacent to at least one crate
        candidates_p = []
        for c in crates:
            for dx, dy in DIRS:
                nbr = (c[0] + dx, c[1] + dy)
                if nbr in empty_cells and nbr not in crates:
                    candidates_p.append(nbr)
        if not candidates_p:
            continue

        player = random.choice(candidates_p)

        # Reverse pull walk (PRD Section 7: "pulling crates away from goals")
        reverse_steps = random.randint(40, 100)
        for _ in range(reverse_steps):
            # Try a random move or pull
            # Options:
            # 1. Normal reverse walk: player moves to adjacent empty cell
            # 2. Reverse pull: player is at P, crate at C (C = P + D).
            #    Player moves to P' = P - D, and crate moves to P.
            action_type = random.random()
            if action_type < 0.6: # Pull
                # Find crates adjacent to player
                adj_crates = []
                for c in crates:
                    dx, dy = c[0] - player[0], c[1] - player[1]
                    if abs(dx) + abs(dy) == 1:
                        adj_crates.append((c, (dx, dy)))
                if adj_crates:
                    c, (dx, dy) = random.choice(adj_crates)
                    # New player pos is P - D
                    new_player = (player[0] - dx, player[1] - dy)
                    if new_player in empty_cells and new_player not in crates:
                        # Pull crate from c to player pos
                        crates.remove(c)
                        crates.add(player)
                        player = new_player
            else: # Walk
                dx, dy = random.choice(DIRS)
                new_p = (player[0] + dx, player[1] + dy)
                if new_p in empty_cells and new_p not in crates:
                    player = new_p

        # Ensure not already solved
        if crates == goals:
            continue

        # Solve and measure difficulty
        solvable, moves, pushes, sol = solve_sokoban(w, h, walls, goals, crates, player, max_states=35000)
        if solvable and moves >= min_moves and pushes >= num_crates:
            return {
                "width": w,
                "height": h,
                "walls": walls,
                "goals": goals,
                "crates": crates,
                "player": player,
                "moves": moves,
                "pushes": pushes,
                "solution": sol,
                "text": format_sokoban(w, h, walls, goals, crates, player)
            }
    return None

if __name__ == '__main__':
    print("Testing candidate generator...")
    cand = generate_candidate(7, 7, 2, 2, min_moves=8)
    if cand:
        print(f"Generated candidate: {cand['moves']} moves, {cand['pushes']} pushes")
        print(cand['text'])
    else:
        print("Failed to generate candidate")

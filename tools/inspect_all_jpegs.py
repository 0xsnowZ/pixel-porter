from PIL import Image
import numpy as np
import sys
from collections import deque

def get_player_component(player, walls, crates):
    # Flood-fill to find all reachable tiles for the player without pushing crates
    reachable = set([player])
    q = deque([player])
    crate_set = set(crates)
    while q:
        r, c = q.popleft()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if (nr, nc) not in walls and (nr, nc) not in crate_set and (nr, nc) not in reachable:
                reachable.add((nr, nc))
                q.append((nr, nc))
    # Return canonical min tile of component
    return min(reachable), reachable

def solve_grid(lines):
    walls = set()
    goals = set()
    crates = []
    player = None
    for r, line in enumerate(lines):
        for c, ch in enumerate(line):
            if ch == '#': walls.add((r, c))
            elif ch == '.': goals.add((r, c))
            elif ch == '$': crates.append((r, c))
            elif ch == '@': player = (r, c)
            elif ch == '*': crates.append((r, c)); goals.add((r, c))
            elif ch == '+': player = (r, c); goals.add((r, c))
    
    crates = tuple(sorted(crates))
    goals = frozenset(goals)
    if not player:
        return None, 'No player'
    if len(crates) != len(goals) or len(crates) == 0:
        return None, f'Mismatch: {len(crates)} crates vs {len(goals)} goals'

    # Canonical initial state
    canonical_p, reachable = get_player_component(player, walls, crates)
    visited = set([(canonical_p, crates)])
    # Queue stores: (player_pos, crates, moves, pushes, path)
    q = deque([(player, crates, 0, 0, '')])
    
    states = 0
    while q:
        states += 1
        if states > 200000:
            return None, f'State limit ({states})'
            
        p, cr, moves, pushes, path = q.popleft()
        if set(cr) == goals:
            return (moves, pushes, path), f'Solved ({moves}m, {pushes}p, {states} states)'
            
        pr, pc = p
        for dr, dc, name in [(-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')]:
            nr, nc = pr + dr, pc + dc
            if (nr, nc) in walls:
                continue
            if (nr, nc) in cr:
                nnr, nnc = nr + dr, nc + dc
                if (nnr, nnc) in walls or (nnr, nnc) in cr:
                    continue
                new_cr = list(cr)
                new_cr.remove((nr, nc))
                new_cr.append((nnr, nnc))
                new_cr = tuple(sorted(new_cr))
                can_p, _ = get_player_component((nr, nc), walls, new_cr)
                if (can_p, new_cr) not in visited:
                    visited.add((can_p, new_cr))
                    q.append(((nr, nc), new_cr, moves + 1, pushes + 1, path + name))
            else:
                can_p, _ = get_player_component((nr, nc), walls, cr)
                if (can_p, cr) not in visited:
                    visited.add((can_p, cr))
                    q.append(((nr, nc), cr, moves + 1, pushes, path + name.lower()))
                    
    return None, f'Unsolvable ({states} states)'

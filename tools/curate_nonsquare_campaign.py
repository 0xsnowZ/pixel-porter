from collections import deque
import json
import time

def solve_level(level_lines, max_states=100000):
    walls = set()
    goals = set()
    crates = []
    player = None
    for r, line in enumerate(level_lines):
        for c, ch in enumerate(line):
            if ch == '#': walls.add((r, c))
            elif ch == '.': goals.add((r, c))
            elif ch == '$': crates.append((r, c))
            elif ch == '@': player = (r, c)
            elif ch == '*': crates.append((r, c)); goals.add((r, c))
            elif ch == '+': player = (r, c); goals.add((r, c))
            
    crates = tuple(sorted(crates))
    goals = frozenset(goals)
    if not player or len(crates) != len(goals) or len(crates) == 0:
        return None
        
    visited = set([(player, crates)])
    q = deque([(player, crates, 0, 0, '')])
    states = 0
    start = time.time()
    
    while q:
        states += 1
        if states > max_states:
            return None
            
        p, cr, moves, pushes, path = q.popleft()
        if set(cr) == goals:
            return {
                'solvable': True,
                'moves': moves,
                'pushes': pushes,
                'path': path,
                'states': states,
                'time_s': time.time() - start,
                'crates': len(crates)
            }
            
        pr, pc = p
        for dr, dc, name in [(-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')]:
            nr, nc = pr + dr, pc + dc
            if (nr, nc) in walls: continue
            if (nr, nc) in cr:
                nnr, nnc = nr + dr, nc + dc
                if (nnr, nnc) in walls or (nnr, nnc) in cr: continue
                # Deadlock check: 2 perpendicular walls
                # Corner deadlock pruning
                is_deadlock = False
                if (nnr, nnc) not in goals:
                    w_up = (nnr-1, nnc) in walls
                    w_dn = (nnr+1, nnc) in walls
                    w_lt = (nnr, nnc-1) in walls
                    w_rt = (nnr, nnc+1) in walls
                    if (w_up and w_lt) or (w_up and w_rt) or (w_dn and w_lt) or (w_dn and w_rt):
                        is_deadlock = True
                if is_deadlock:
                    continue
                    
                new_cr = list(cr)
                new_cr.remove((nr, nc))
                new_cr.append((nnr, nnc))
                new_cr = tuple(sorted(new_cr))
                if ((nr, nc), new_cr) not in visited:
                    visited.add(((nr, nc), new_cr))
                    q.append(((nr, nc), new_cr, moves + 1, pushes + 1, path + name))
            else:
                if ((nr, nc), cr) not in visited:
                    visited.add(((nr, nc), cr))
                    q.append(((nr, nc), cr, moves + 1, pushes, path + name.lower()))
    return None

print('Solver loaded successfully.')


from collections import deque
import random
import sys
import time

def generate_from_template(template_str, num_crates, target_min_moves=15, target_max_moves=60, max_pull_steps=200):
    """
    Takes a non-square room template where:
    '#' = wall
    ' ' = floor
    '.' = possible goal location
    '_' or leading space = void
    Generates a solvable puzzle by picking goal locations and pulling crates backward.
    """
    lines = [l.rstrip() for l in template_str.strip('\n').split('\n')]
    height = len(lines)
    width = max(len(l) for l in lines)
    
    walls = set()
    floor = set()
    possible_goals = []
    
    for r in range(height):
        line = lines[r]
        for c in range(len(line)):
            ch = line[c]
            if ch == '#':
                walls.add((r, c))
            elif ch == ' ':
                floor.add((r, c))
            elif ch == '.':
                floor.add((r, c))
                possible_goals.append((r, c))
                
    if len(possible_goals) < num_crates:
        possible_goals = list(floor)
        
    # Run multiple random reverse walks
    best_puzzle = None
    best_moves = 0
    
    # Try 50 random reverse walks
    for attempt in range(80):
        # Pick random distinct goals
        goals = tuple(sorted(random.sample(possible_goals, num_crates)))
        # Pick player adjacent to one of the crates on goals
        crates = list(goals)
        player_candidates = []
        for cr in crates:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                p = (cr[0] + dr, cr[1] + dc)
                if p in floor and p not in crates:
                    player_candidates.append(p)
        if not player_candidates:
            continue
        player = random.choice(player_candidates)
        
        # Reverse walk: player moves or pulls a crate
        # In reverse: player at P, moves to P' (empty). Or player at P, pulls crate from C adjacent to P into P, player moves to P'
        # Reverse pull rule:
        # Crate is at C. Player is at P (adjacent to C). Player steps back to P' (behind P in direction away from C).
        # Crate moves from C to P. Player ends at P'.
        cur_p = player
        cur_crates = list(crates)
        
        steps = 0
        while steps < max_pull_steps:
            steps += 1
            # Choose either simple move or pull
            # Possible reverse moves:
            # 1. Walk without pull: step to any adjacent empty floor
            # 2. Pull: if crate is adjacent to cur_p at C = cur_p - dir, and cur_p + dir is empty floor:
            #    player moves to cur_p + dir, crate moves to cur_p.
            pulls = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                # crate would be at (cur_p[0] - dr, cur_p[1] - dc)
                c_pos = (cur_p[0] - dr, cur_p[1] - dc)
                # player steps to (cur_p[0] + dr, cur_p[1] + dc)
                p_next = (cur_p[0] + dr, cur_p[1] + dc)
                if c_pos in cur_crates and p_next in floor and p_next not in cur_crates:
                    pulls.append((c_pos, p_next, dr, dc))
                    
            walks = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                p_next = (cur_p[0] + dr, cur_p[1] + dc)
                if p_next in floor and p_next not in cur_crates:
                    walks.append(p_next)
                    
            if pulls and random.random() < 0.65:
                # do pull
                c_pos, p_next, dr, dc = random.choice(pulls)
                cur_crates.remove(c_pos)
                cur_crates.append(cur_p)
                cur_p = p_next
            elif walks:
                cur_p = random.choice(walks)
            else:
                break
                
        # Check if crates are not all on goals
        if set(cur_crates) == set(goals):
            continue
            
        # Verify and solve forward with BFS
        res = solve_forward(walls, floor, goals, cur_p, cur_crates, max_states=40000)
        if res and res['solvable']:
            m = res['moves']
            if m > best_moves:
                best_moves = m
                best_puzzle = {
                    'walls': walls,
                    'floor': floor,
                    'goals': goals,
                    'player': cur_p,
                    'crates': cur_crates,
                    'moves': m,
                    'pushes': res['pushes'],
                    'states': res['states'],
                    'path': res['path'],
                    'lines': format_puzzle(lines, walls, goals, cur_p, cur_crates)
                }
            if target_min_moves <= m <= target_max_moves:
                return best_puzzle
                
    return best_puzzle

def solve_forward(walls, floor, goals, player, crates, max_states=40000):
    crates = tuple(sorted(crates))
    goals = frozenset(goals)
    visited = set([(player, crates)])
    q = deque([(player, crates, 0, 0, '')])
    states = 0
    while q:
        states += 1
        if states > max_states:
            return None
        p, cr, moves, pushes, path = q.popleft()
        if set(cr) == goals:
            return {'solvable': True, 'moves': moves, 'pushes': pushes, 'states': states, 'path': path}
        pr, pc = p
        for dr, dc, name in [(-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')]:
            nr, nc = pr + dr, pc + dc
            if (nr, nc) in walls: continue
            if (nr, nc) in cr:
                nnr, nnc = nr + dr, nc + dc
                if (nnr, nnc) in walls or (nnr, nnc) in cr: continue
                # Corner deadlock pruning
                if (nnr, nnc) not in goals:
                    w_up = (nnr-1, nnc) in walls
                    w_dn = (nnr+1, nnc) in walls
                    w_lt = (nnr, nnc-1) in walls
                    w_rt = (nnr, nnc+1) in walls
                    if (w_up and w_lt) or (w_up and w_rt) or (w_dn and w_lt) or (w_dn and w_rt):
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

def format_puzzle(template_lines, walls, goals, player, crates):
    height = len(template_lines)
    width = max(len(l) for l in template_lines)
    grid = []
    crate_set = set(crates)
    for r in range(height):
        row = []
        for c in range(width):
            pos = (r, c)
            if pos in walls:
                row.append('#')
            elif pos == player and pos in goals:
                row.append('+')
            elif pos == player:
                row.append('@')
            elif pos in crate_set and pos in goals:
                row.append('*')
            elif pos in crate_set:
                row.append('$')
            elif pos in goals:
                row.append('.')
            elif (r < len(template_lines) and c < len(template_lines[r]) and template_lines[r][c] == ' ') or pos in walls:
                row.append(' ')
            else:
                row.append(' ')
        grid.append(''.join(row).rstrip())
    return grid

# Test template: Stepped L-Shape
template_l = '''
  #####
  #   #
###   #
#     #
#   ###
#   #
#...#
#####
'''
puz = generate_from_template(template_l, 3, target_min_moves=15, target_max_moves=40)
if puz:
    print(f"Generated L-Shape: Moves={puz['moves']}, Pushes={puz['pushes']}, States={puz['states']}")
    for l in puz['lines']:
        print(repr(l))
else:
    print("Failed to generate L-shape")


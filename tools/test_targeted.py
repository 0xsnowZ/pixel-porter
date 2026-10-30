import sys
import random
import time
from collections import deque
import json
import os

random.seed(1337)

def solve_forward(walls, floor, goals, player, crates, max_states=45000):
    crates = tuple(sorted(crates))
    goals = frozenset(goals)
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
                'states': states,
                'path': path,
                'time_s': time.time() - start
            }
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

def format_grid(template_lines, walls, goals, player, crates):
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

def generate_targeted_puzzles(template_str, name, num_crates, target_moves_min, target_moves_max, count=2, max_attempts=250):
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
            if ch == '#': walls.add((r, c))
            elif ch == ' ': floor.add((r, c))
            elif ch == '.':
                floor.add((r, c))
                possible_goals.append((r, c))
                
    if len(possible_goals) < num_crates:
        possible_goals = list(floor)
        
    found = []
    attempts = 0
    while len(found) < count and attempts < max_attempts:
        attempts += 1
        # Pick goals: prefer dead-ends or alcoves if available
        goals = tuple(sorted(random.sample(possible_goals, num_crates)))
        crates = list(goals)
        player_candidates = []
        for cr in crates:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                p = (cr[0] + dr, cr[1] + dc)
                if p in floor and p not in crates:
                    player_candidates.append(p)
        if not player_candidates: continue
        cur_p = random.choice(player_candidates)
        cur_crates = list(crates)
        
        # Scaling pull steps based on target move count
        num_pulls = random.randint(int(target_moves_min * 2.5), int(target_moves_max * 4.5))
        for _ in range(num_pulls):
            pulls = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                c_pos = (cur_p[0] - dr, cur_p[1] - dc)
                p_next = (cur_p[0] + dr, cur_p[1] + dc)
                if c_pos in cur_crates and p_next in floor and p_next not in cur_crates:
                    pulls.append((c_pos, p_next))
            walks = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                p_next = (cur_p[0] + dr, cur_p[1] + dc)
                if p_next in floor and p_next not in cur_crates:
                    walks.append(p_next)
                    
            if pulls and random.random() < 0.70:
                c_pos, p_next = random.choice(pulls)
                cur_crates.remove(c_pos)
                cur_crates.append(cur_p)
                cur_p = p_next
            elif walks:
                cur_p = random.choice(walks)
            else:
                break
                
        if set(cur_crates) == set(goals):
            continue
            
        res = solve_forward(walls, floor, goals, cur_p, cur_crates, max_states=35000)
        if res and res['solvable'] and target_moves_min <= res['moves'] <= target_moves_max:
            grid_lines = format_grid(lines, walls, goals, cur_p, cur_crates)
            puzzle_obj = {
                'name': f'{name} ({res["moves"]}m)',
                'moves': res['moves'],
                'pushes': res['pushes'],
                'states': res['states'],
                'crates': num_crates,
                'path': res['path'],
                'lines': grid_lines
            }
            if not any(p['moves'] == res['moves'] for p in found):
                found.append(puzzle_obj)
                print(f'  [FOUND] {puzzle_obj["name"]} -> {res["moves"]} moves, {res["pushes"]} pushes, {res["states"]} states')
    return found

# Test with target_moves_min=25, target_moves_max=40
template_s = '''
  #####
  #   #
  #   ##
### #  #
#   #  #
#   # ##
#      #
########
'''
puzs = generate_targeted_puzzles(template_s, 'S-Corridor', 3, 25, 40, count=2)
print('Results:', len(puzs))


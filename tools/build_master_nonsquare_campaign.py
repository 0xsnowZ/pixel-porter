import sys
import random
import time
from collections import deque
import json
import os

random.seed(2026)

def solve_forward(walls, floor, goals, player, crates, max_states=30000):
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

def generate_one(template_str, name, num_crates, min_m, max_m, max_states=25000, max_att=300):
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
        
    best_candidate = None
    for attempt in range(max_att):
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
        
        num_pulls = random.randint(int(min_m * 2.2), int(max_m * 4.2))
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
                    
            if pulls and random.random() < 0.68:
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
            
        res = solve_forward(walls, floor, goals, cur_p, cur_crates, max_states=max_states)
        if res and res['solvable']:
            m = res['moves']
            if min_m <= m <= max_m:
                return {
                    'name': name,
                    'moves': m,
                    'pushes': res['pushes'],
                    'states': res['states'],
                    'crates': num_crates,
                    'path': res['path'],
                    'lines': format_grid(lines, walls, goals, cur_p, cur_crates)
                }
            if best_candidate is None or abs(m - (min_m + max_m)//2) < abs(best_candidate['moves'] - (min_m + max_m)//2):
                best_candidate = {
                    'name': name,
                    'moves': m,
                    'pushes': res['pushes'],
                    'states': res['states'],
                    'crates': num_crates,
                    'path': res['path'],
                    'lines': format_grid(lines, walls, goals, cur_p, cur_crates)
                }
    return best_candidate

# Templates library
T_PINWHEEL = '''
  ###
  # #
  # ####
###    #
#      #
#### # #
   # #
   ###
'''

T_L_ROOM = '''
#####
#   #
#   ###
#     #
#   ###
#   #
#...#
#####
'''

T_CORNER_NOOK = '''
  #####
###   #
#     #
#     #
#   ###
#   #
#####
'''

T_S_CORRIDOR = '''
  #####
  #   #
  #   ##
### #  #
#   #  #
#   # ##
#      #
########
'''

T_PILLAR_HALL = '''
######
#    #
# ## #
#    #
# ## #
#    #
######
'''

T_ISLAND_LOOP = '''
#######
#     #
# ### #
# # # #
# ### #
#     #
#######
'''

T_STEPPED_DEPOT = '''
  ######
  #    #
###    #
#      #
#    ###
######
'''

T_TWIN_BAYS = '''
########
#  #   #
#      #
#  #   #
########
'''

T_VERTICAL_SHAFT = '''
######
#    #
# ## #
#  # #
#  # #
#    #
######
'''

T_CASTLE_KEEP = '''
 #####
##   ##
#     #
#     #
##   ##
 #####
'''

T_T_DEPOT = '''
#########
#       #
###   ###
  #   #
  #   #
  #####
'''

T_AIRLOCK = '''
##### #####
#   ###   #
#         #
#   ###   #
##### #####
'''

T_DIAMOND = '''
   ###
  ## ##
 ##   ##
##     ##
#       #
##     ##
 ##   ##
  #####
'''

T_ZIGZAG = '''
  #####
  #   #
###   #
#   ###
#   #
### ###
  # #
  ###
'''

T_FORTRESS = '''
  #####
 ##   ##
##  #  ##
#       #
##     ##
 #######
'''

T_POCKET_S = '''
  ######
  #    #
###    #
#    # #
#  ### #
#      #
########
'''

T_CRUCIFORM = '''
  #####
  #   #
###   ###
#       #
#       #
###   ###
  #   #
  #####
'''

T_EXTENDED_L = '''
######
#    ###
#      #
###    #
  #    #
  ######
'''

T_GRAND_RING = '''
 #######
##     ##
#  ###  #
#  # #  #
#  ###  #
##     ##
 #######
'''

# Plan for all 50 levels
LEVEL_SPECS = [
    # Chapter 1: The Port Docks (Levels 1-10) -> Moves: 10 to 22
    (1, 'Ref Level 1 Pinwheel', T_PINWHEEL, 4, 12, 12), # Exact ref 1
    (2, 'Stepped L-Room I', T_L_ROOM, 2, 8, 14),
    (3, 'Corner Nook I', T_CORNER_NOOK, 2, 10, 15),
    (4, 'S-Corridor I', T_S_CORRIDOR, 2, 12, 16),
    (5, 'T-Depot I', T_T_DEPOT, 2, 12, 18),
    (6, 'Island Loop I', T_ISLAND_LOOP, 2, 14, 20),
    (7, 'Airlock Chambers I', T_AIRLOCK, 2, 14, 20),
    (8, 'Castle Keep I', T_CASTLE_KEEP, 3, 16, 22),
    (9, 'Stepped Depot I', T_STEPPED_DEPOT, 3, 16, 22),
    (10, 'Twin Bays I', T_TWIN_BAYS, 3, 18, 24),

    # Chapter 2: The Depots (Levels 11-20) -> Moves: 22 to 34
    (11, 'Pillar Hall I', T_PILLAR_HALL, 3, 20, 26),
    (12, 'Stepped L-Room II', T_L_ROOM, 3, 22, 28),
    (13, 'S-Corridor II', T_S_CORRIDOR, 3, 22, 28),
    (14, 'Diamond Depot I', T_DIAMOND, 3, 24, 30),
    (15, 'Zigzag Run I', T_ZIGZAG, 3, 24, 30),
    (16, 'Twin Bays II', T_TWIN_BAYS, 3, 26, 32),
    (17, 'Pinwheel Cross II', T_PINWHEEL, 3, 26, 32),
    (18, 'Extended L-Bay I', T_EXTENDED_L, 3, 28, 34),
    (19, 'Vertical Shaft I', T_VERTICAL_SHAFT, 3, 28, 34),
    (20, 'Castle Keep II', T_CASTLE_KEEP, 4, 28, 36),

    # Chapter 3: The Rail Yard (Levels 21-30) -> Moves: 32 to 44
    (21, 'Pocket S-Bend I', T_POCKET_S, 3, 30, 38),
    (22, 'Cruciform Depot I', T_CRUCIFORM, 3, 30, 38),
    (23, 'Fortress Vault I', T_FORTRESS, 3, 32, 40),
    (24, 'Island Loop II', T_ISLAND_LOOP, 3, 32, 40),
    (25, 'Pillar Hall II', T_PILLAR_HALL, 4, 34, 42),
    (26, 'Stepped Depot II', T_STEPPED_DEPOT, 4, 34, 42),
    (27, 'Airlock Chambers II', T_AIRLOCK, 3, 36, 44),
    (28, 'Grand Ring I', T_GRAND_RING, 3, 36, 44),
    (29, 'Diamond Depot II', T_DIAMOND, 4, 36, 44),
    (30, 'Pinwheel Cross III', T_PINWHEEL, 4, 38, 46),

    # Chapter 4: The Vaults (Levels 31-40) -> Moves: 42 to 54
    (31, 'Fortress Vault II', T_FORTRESS, 4, 40, 48),
    (32, 'Pocket S-Bend II', T_POCKET_S, 4, 40, 48),
    (33, 'Cruciform Depot II', T_CRUCIFORM, 4, 42, 50),
    (34, 'Island Loop III', T_ISLAND_LOOP, 4, 42, 50),
    (35, 'Grand Ring II', T_GRAND_RING, 4, 44, 52),
    (36, 'Airlock Chambers III', T_AIRLOCK, 4, 44, 52),
    (37, 'Twin Bays III', T_TWIN_BAYS, 4, 46, 54),
    (38, 'Castle Keep III', T_CASTLE_KEEP, 4, 46, 54),
    (39, 'Pillar Hall III', T_PILLAR_HALL, 4, 46, 54),
    (40, 'Stepped Depot III', T_STEPPED_DEPOT, 4, 48, 56),

    # Chapter 5: Master Works (Levels 41-50) -> Moves: 50 to 68
    (41, 'Grand Ring Master', T_GRAND_RING, 4, 48, 58),
    (42, 'Cruciform Master', T_CRUCIFORM, 4, 50, 60),
    (43, 'Fortress Master', T_FORTRESS, 4, 50, 60),
    (44, 'Pocket S-Bend Master', T_POCKET_S, 4, 52, 62),
    (45, 'Island Loop Master', T_ISLAND_LOOP, 4, 52, 62),
    (46, 'Pinwheel Master', T_PINWHEEL, 4, 54, 64),
    (47, 'Grand Ring Quintet', T_GRAND_RING, 5, 54, 66),
    (48, 'Castle Keep Master', T_CASTLE_KEEP, 4, 56, 68),
    (49, 'Airlock Master', T_AIRLOCK, 4, 56, 68),
    (50, 'The Grand Architect', T_GRAND_RING, 5, 58, 70)
]

campaign = []

# Special handling for Level 1 (exact ref 1)
ref1_lines = [
    '  ###',
    '  #.#',
    '  # ####',
    '###$ $ .#',
    '#. $ @##',
    '####$#',
    '   #.#',
    '   ###'
]
w1, f1, g1, c1, p1 = set(), set(), set(), [], None
for r, l in enumerate(ref1_lines):
    for c, ch in enumerate(l):
        if ch == '#': w1.add((r, c))
        elif ch == '.': g1.add((r, c)); f1.add((r, c))
        elif ch == '$': c1.append((r, c)); f1.add((r, c))
        elif ch == '@': p1 = (r, c); f1.add((r, c))
        elif ch == ' ': f1.add((r, c))
res1 = solve_forward(w1, f1, g1, p1, c1)
campaign.append({
    'lvl': 1,
    'name': 'Ref Level 1 Pinwheel',
    'moves': res1['moves'],
    'pushes': res1['pushes'],
    'states': res1['states'],
    'crates': 4,
    'path': res1['path'],
    'lines': ref1_lines
})
print(f'Level 01: Ref Level 1 Pinwheel -> {res1["moves"]}m, {res1["pushes"]}p, {res1["states"]}st')

for lvl_num, name, tmpl, num_c, min_m, max_m in LEVEL_SPECS[1:]:
    puz = generate_one(tmpl, name, num_c, min_m, max_m, max_states=25000, max_att=250)
    if not puz:
        # Fallback with relaxed bounds
        puz = generate_one(tmpl, name, num_c, min_m - 4, max_m + 8, max_states=30000, max_att=400)
    puz['lvl'] = lvl_num
    campaign.append(puz)
    print(f'Level {lvl_num:02d}: {puz["name"]:25s} -> {puz["moves"]:2d}m, {puz["pushes"]:2d}p, {puz["states"]:5d}st, crates: {puz["crates"]}')

# Sort levels 2..50 by moves ascending while preserving smooth progression
campaign_sorted = [campaign[0]] + sorted(campaign[1:], key=lambda p: (p['moves'], p['pushes']))
for idx, p in enumerate(campaign_sorted):
    p['lvl'] = idx + 1

os.makedirs('/tmp/nonsquare_levels', exist_ok=True)
optimal_moves_dict = {}

for p in campaign_sorted:
    lvl = p['lvl']
    optimal_moves_dict[lvl] = p['moves']
    path = f'/tmp/nonsquare_levels/level_{lvl:02d}.sok'
    with open(path, 'w') as f:
        f.write('\n'.join(p['lines']) + '\n')

with open('/tmp/nonsquare_campaign.json', 'w') as f:
    json.dump(campaign_sorted, f, indent=2)

print('\nCampaign Generation Completed!')
print(f'Level 1 to 50 moves: {[p["moves"] for p in campaign_sorted]}')
print(f'Average moves: {sum(p["moves"] for p in campaign_sorted)/50:.1f}')
print(f'Average pushes: {sum(p["pushes"] for p in campaign_sorted)/50:.1f}')


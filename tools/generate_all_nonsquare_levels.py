import sys
import random
import time
from collections import deque
import json
import os

# Set seed for reproducible campaign generation
random.seed(42)

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

def generate_puzzles_from_template(template_str, name, num_crates, count=3, min_moves=10, max_moves=65):
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
    while len(found) < count and attempts < 150:
        attempts += 1
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
        
        # Pull walk
        num_pulls = random.randint(35, 150)
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
                    
            if pulls and random.random() < 0.65:
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
            
        res = solve_forward(walls, floor, goals, cur_p, cur_crates, max_states=25000)
        if res and res['solvable'] and min_moves <= res['moves'] <= max_moves:
            grid_lines = format_grid(lines, walls, goals, cur_p, cur_crates)
            puzzle_obj = {
                'name': f'{name} #{len(found)+1}',
                'moves': res['moves'],
                'pushes': res['pushes'],
                'states': res['states'],
                'crates': num_crates,
                'path': res['path'],
                'lines': grid_lines
            }
            if not any(p['moves'] == res['moves'] and p['crates'] == num_crates for p in found):
                found.append(puzzle_obj)
    return found

# ==============================================================================
# 20 AUTHENTIC NON-SQUARE TEMPLATES INSPIRED BY REF_LEVELS
# ==============================================================================

TEMPLATES = [
    # 1. Pinwheel Cross (from ref 1.jpeg)
    ('Pinwheel Cross', '''
  ###
  # #
  # ####
###    #
#      #
#### # #
   # #
   ###
''', [3, 4]),

    # 2. Stepped L-Shape (from ref 2.jpeg)
    ('Stepped L-Room', '''
#####
#   #
#   ###
#     #
#   ###
#   #
#...#
#####
''', [2, 3]),

    # 3. Corner Nook (from ref 3.jpeg)
    ('Corner Nook', '''
  #####
###   #
#     #
#     #
#   ###
#   #
#####
''', [2, 3]),

    # 4. S-Winding Corridor (from ref 4.jpeg)
    ('S-Corridor', '''
  #####
  #   #
  #   ##
### #  #
#   #  #
#   # ##
#      #
########
''', [2, 3]),

    # 5. Twin Pillar Room (from ref 8.jpeg)
    ('Pillar Hall', '''
######
#    #
# ## #
#    #
# ## #
#    #
######
''', [3, 4]),

    # 6. Central Column Donut
    ('Island Loop', '''
#######
#     #
# ### #
# # # #
# ### #
#     #
#######
''', [2, 3, 4]),

    # 7. Asymmetric Dock (from ref 5.jpeg)
    ('Stepped Depot', '''
  ######
  #    #
###    #
#      #
#    ###
######
''', [3, 4]),

    # 8. Twin Bays (from ref 10.jpeg)
    ('Twin Bays', '''
########
#  #   #
#      #
#  #   #
########
''', [3, 4]),

    # 9. Narrow Shaft (from ref 12.jpeg)
    ('Vertical Shaft', '''
######
#    #
# ## #
#  # #
#  # #
#    #
######
''', [2, 3]),

    # 10. Castle Keep / Notched Corners (from ref 7.jpeg & 15.jpeg)
    ('Castle Keep', '''
 #####
##   ##
#     #
#     #
##   ##
 #####
''', [3, 4]),

    # 11. T-Junction Depot
    ('T-Depot', '''
#########
#       #
###   ###
  #   #
  #   #
  #####
''', [2, 3]),

    # 12. Trident 3-Bay
    ('Trident Bay', '''
 #######
 #     #
## # # ##
#  # #  #
#########
''', [2, 3]),

    # 13. Airlock Double Chamber
    ('Airlock Chambers', '''
##### #####
#   ###   #
#         #
#   ###   #
##### #####
''', [2, 3, 4]),

    # 14. Diamond Depot
    ('Diamond Depot', '''
   ###
  ## ##
 ##   ##
##     ##
#       #
##     ##
 ##   ##
  #####
''', [3, 4]),

    # 15. Zigzag Corridor
    ('Zigzag Run', '''
  #####
  #   #
###   #
#   ###
#   #
### ###
  # #
  ###
''', [2, 3]),

    # 16. Fortress Vault
    ('Fortress Vault', '''
  #####
 ##   ##
##  #  ##
#       #
##     ##
 #######
''', [3, 4]),

    # 17. S-Bend with Pocket (from ref 14.jpeg)
    ('Pocket S-Bend', '''
  ######
  #    #
###    #
#    # #
#  ### #
#      #
########
''', [3, 4]),

    # 18. Stepped Cross (from ref 13.jpeg)
    ('Cruciform Depot', '''
  #####
  #   #
###   ###
#       #
#       #
###   ###
  #   #
  #####
''', [3, 4]),

    # 19. Extended L-Bay
    ('Extended L-Bay', '''
######
#    ###
#      #
###    #
  #    #
  ######
''', [2, 3]),

    # 20. Master Ring Chamber
    ('Grand Ring', '''
 #######
##     ##
#  ###  #
#  # #  #
#  ###  #
##     ##
 #######
''', [3, 4, 5])
]

all_puzzles = []

# Include signature Reference Level 1 directly
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
# Solve ref 1
w1 = set()
f1 = set()
g1 = set()
c1 = []
p1 = None
for r, l in enumerate(ref1_lines):
    for c, ch in enumerate(l):
        if ch == '#': w1.add((r, c))
        elif ch == '.': g1.add((r, c)); f1.add((r, c))
        elif ch == '$': c1.append((r, c)); f1.add((r, c))
        elif ch == '@': p1 = (r, c); f1.add((r, c))
        elif ch == ' ': f1.add((r, c))
res1 = solve_forward(w1, f1, g1, p1, c1)
if res1:
    all_puzzles.append({
        'name': 'Ref Level 1 Pinwheel',
        'moves': res1['moves'],
        'pushes': res1['pushes'],
        'states': res1['states'],
        'crates': 4,
        'path': res1['path'],
        'lines': ref1_lines
    })

print(f'Added Ref Level 1 (Moves: {res1["moves"]})')

# Generate puzzles across all templates
for name, tmpl, crate_opts in TEMPLATES:
    for num_c in crate_opts:
        puzs = generate_puzzles_from_template(tmpl, name, num_c, count=2, min_moves=10, max_moves=65)
        all_puzzles.extend(puzs)
        print(f'Template "{name}" ({num_c} crates): generated {len(puzs)} puzzles')

print(f'\nTotal generated puzzles: {len(all_puzzles)}')

# Sort by moves ascending
all_puzzles.sort(key=lambda p: (p['moves'], p['pushes'], p['crates']))

# Remove duplicate layouts or exact same move counts if too clustered
selected = []
for p in all_puzzles:
    # ensure non-square
    lines = p['lines']
    # Check that it has non-square characteristics (leading spaces or stepped line lengths)
    has_leading_space = any(l.startswith(' ') for l in lines)
    has_varying_length = len(set(len(l) for l in lines)) > 1
    if not (has_leading_space or has_varying_length):
        continue
    # Keep diverse puzzles
    selected.append(p)

print(f'Selected valid non-square puzzles: {len(selected)}')

# Take top 50
campaign = selected[:50]
if len(campaign) < 50:
    print(f'Warning: only {len(campaign)} puzzles selected, taking all.')
else:
    print(f'Successfully curated 50 non-square campaign levels!')
    print(f'Moves range: {campaign[0]["moves"]} to {campaign[-1]["moves"]}')
    print(f'Crates range: {min(p["crates"] for p in campaign)} to {max(p["crates"] for p in campaign)}')

# Save campaign summary to json
with open('/tmp/nonsquare_campaign.json', 'w') as f:
    json.dump([{
        'lvl': idx + 1,
        'name': p['name'],
        'moves': p['moves'],
        'pushes': p['pushes'],
        'crates': p['crates'],
        'states': p['states'],
        'lines': p['lines']
    } for idx, p in enumerate(campaign)], f, indent=2)

print('Saved to /tmp/nonsquare_campaign.json')

from collections import deque
import sys

def solve(lines):
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

    visited = set([(player, crates)])
    q = deque([(player, crates, 0, 0, '')])
    states = 0
    while q:
        states += 1
        if states > 100000:
            return None, f'State limit ({states})'
            
        p, cr, moves, pushes, path = q.popleft()
        if set(cr) == goals:
            return (moves, pushes, path), f'Solved ({moves}m, {pushes}p, {states}st)'
            
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
                if ((nr, nc), new_cr) not in visited:
                    visited.add(((nr, nc), new_cr))
                    q.append(((nr, nc), new_cr, moves + 1, pushes + 1, path + name))
            else:
                if ((nr, nc), cr) not in visited:
                    visited.add(((nr, nc), cr))
                    q.append(((nr, nc), cr, moves + 1, pushes, path + name.lower()))
                    
    return None, f'Unsolvable ({states} states)'

# Let's define the 15 reference levels accurately:

levels = {}

# Level 1: Cross / Pinwheel (from 1.jpeg)
levels[1] = [
    '  ###   ',
    '  #.#   ',
    '  # ####',
    '###$ $ .#',
    '#. $ @##',
    '####$#  ',
    '   #.#  ',
    '   ###  '
]

# Let's inspect 3.jpeg:
# 4 crates, 4 goals in corner
levels[3] = [
    '  ##### ',
    '###   # ',
    '# @$$ # ',
    '#  $  # ',
    '#.$#  # ',
    '#..$  # ',
    '#..   # ',
    '####### '
]

# Let's inspect 4.jpeg:
# 3 goals vertical in left corridor, 3 crates in S-bend
levels[4] = [
    '  ##### ',
    '  #@  # ',
    '  # $ ##',
    '### #  #',
    '#.# #  #',
    '#.# $ ##',
    '#.$  $# ',
    '####### '
]

# Let's inspect 5.jpeg:
# 5 crates, 2x3 goal cluster
levels[5] = [
    '  ######',
    '  #    #',
    '###$$$ #',
    '#@ $.. #',
    '#  $..##',
    '####  # ',
    '   #### '
]

# Level 8 from 8.jpeg:
# Goals in middle (2x2), crates around, player at left
levels[8] = [
    '######  ',
    '#    #  ',
    '#@$..$# ',
    '# $..$# ',
    '# $  $# ',
    '######  '
]

# Level 10 from 10.jpeg:
# Stepped room, goals top-left and top-right (2x2 each), crates in middle
levels[10] = [
    '########',
    '#..$ ..#',
    '#..$ ..#',
    '# $$$$ #',
    '#  @   #',
    '########'
]

for lvl_num, grid in levels.items():
    sol, msg = solve(grid)
    print(f'Level {lvl_num}: {msg}')


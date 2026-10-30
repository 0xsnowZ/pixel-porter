from collections import deque

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
    print(f'Player: {player}, Crates: {crates}, Goals: {goals}')
    if not player:
        return 'No player found!'
    visited = set([(player, crates)])
    q = deque([(player, crates, 0, 0, '')])
    while q:
        p, cr, moves, pushes, path = q.popleft()
        if set(cr) == goals:
            return (moves, pushes, path)
        pr, pc = p
        for dr, dc, name in [(-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')]:
            nr, nc = pr + dr, pc + dc
            if (nr, nc) in walls: continue
            if (nr, nc) in cr:
                nnr, nnc = nr + dr, nc + dc
                if (nnr, nnc) in walls or (nnr, nnc) in cr: continue
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
    return 'Unsolvable!'

lines_lvl1 = [
    '  ###    ',
    '  #.#    ',
    '  # #####',
    '###$ $ .#',
    '# .$@ ###',
    '####$#   ',
    '   #.#   ',
    '   ###   '
]

print('Lvl 1:', solve(lines_lvl1))


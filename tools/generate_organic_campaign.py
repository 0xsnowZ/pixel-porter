#!/usr/bin/env python3
"""
tools/generate_organic_campaign.py

Generates and verifies 50 organic, non-square Sokoban levels for Pixel Porter.
Each level is guaranteed solvable via BFS shortest-path verification.
Updates levels/level_01.sok through levels/level_50.sok and scripts/save_manager.gd.
"""

import collections
import random
import os
import sys
import re

DIRS = [
    ((0, -1), 'u'),
    ((0, 1), 'd'),
    ((-1, 0), 'l'),
    ((1, 0), 'r')
]

LEVEL_TITLES = {
    1: "The Cross Bay",
    2: "L-Bend Junction",
    3: "Stepped Storage",
    4: "Island Loop",
    5: "T-Junction Depot",
    6: "Cruciform Pinwheel",
    7: "Jagged Alcove",
    8: "Butterfly Hub",
    9: "Staged Warehouse",
    10: "Dual Bay Depot",
    11: "Spiral Pinwheel",
    12: "Vertical Chute",
    13: "Spine & Wings",
    14: "S-Bend Double Hall",
    15: "Dual-Bay Perimeter",
    16: "Cold Storage Inset",
    17: "Sub-Zero Chute",
    18: "Frostbite Loop",
    19: "Freezer Bypass",
    20: "Divided Vault",
    21: "Icebox Tetris",
    22: "Twin Pillars",
    23: "Glacier Gallery",
    24: "Square Dance",
    25: "Fork in the Ice",
    26: "The Permafrost",
    27: "Vault Corridor",
    28: "Central Cold Hub",
    29: "Dual Bay Staging",
    30: "Cryo Sanctum",
    31: "Cyber Conduit",
    32: "Neon Labyrinth",
    33: "Blockade Runner",
    34: "Terminal Node",
    35: "Gridlock Bay",
    36: "Tetris Core",
    37: "Column Matrix",
    38: "Inner Sanctum",
    39: "Cargo Congestion",
    40: "Grand Depot",
    41: "Data Vault",
    42: "Pallet Matrix",
    43: "Double Bypass",
    44: "Forked Gallery",
    45: "Iron Grid",
    46: "Master's Gallery",
    47: "Cathedral of Crates",
    48: "The Great Hall",
    49: "Grand Labyrinth",
    50: "The Final Gauntlet"
}


def build_walls_around_floor(floor):
    walls = set()
    for fx, fy in floor:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                pt = (fx + dx, fy + dy)
                if pt not in floor:
                    walls.add(pt)
    min_x = min(x for x, y in walls)
    min_y = min(y for x, y in walls)
    norm_floor = {(x - min_x, y - min_y) for x, y in floor}
    norm_walls = {(x - min_x, y - min_y) for x, y in walls}
    w = max(x for x, y in norm_walls) + 1
    h = max(y for x, y in norm_walls) + 1
    return w, h, norm_walls, norm_floor


# Blueprints with guaranteed non-square exterior void geometry
def bp_l_bend(w1=3, h1=3, w2=3, h2=3, ox=2, oy=2):
    floor = set()
    for x in range(w1):
        for y in range(h1):
            floor.add((x, y))
    for x in range(w2):
        for y in range(h2):
            floor.add((ox + x, oy + y))
    return build_walls_around_floor(floor)


def bp_t_junction(top_w=6, top_h=2, stem_w=2, stem_h=3, stem_x=2):
    floor = set()
    for x in range(top_w):
        for y in range(top_h):
            floor.add((x, y))
    for x in range(stem_w):
        for y in range(stem_h):
            floor.add((stem_x + x, top_h + y))
    return build_walls_around_floor(floor)


def bp_cross(center_size=3, arm_len=2, arm_w=2):
    floor = set()
    for x in range(center_size):
        for y in range(center_size):
            floor.add((arm_len + x, arm_len + y))
    for x in range(arm_w):
        for y in range(arm_len):
            floor.add((arm_len + (center_size - arm_w)//2 + x, y))
    for x in range(arm_w):
        for y in range(arm_len):
            floor.add((arm_len + (center_size - arm_w)//2 + x, arm_len + center_size + y))
    for x in range(arm_len):
        for y in range(arm_w):
            floor.add((x, arm_len + (center_size - arm_w)//2 + y))
    for x in range(arm_len):
        for y in range(arm_w):
            floor.add((arm_len + center_size + x, arm_len + (center_size - arm_w)//2 + y))
    return build_walls_around_floor(floor)


def bp_island_loop(w=7, h=7):
    floor = set()
    pill = {(3, 2), (3, 3), (3, 4)}
    for x in range(w):
        for y in range(h):
            if x < 2 and y < 2: continue
            if x >= w - 2 and y < 2: continue
            if x >= w - 2 and y >= h - 2: continue
            if (x, y) in pill: continue
            floor.add((x, y))
    return build_walls_around_floor(floor)


def bp_s_curve(ch1_w=3, ch1_h=3, ch2_w=3, ch2_h=3, corr_len=2):
    floor = set()
    for x in range(ch1_w):
        for y in range(ch1_h):
            floor.add((x, y))
    for x in range(corr_len):
        floor.add((ch1_w + x, ch1_h - 1))
    for x in range(ch2_w):
        for y in range(ch2_h):
            floor.add((ch1_w + corr_len - 1 + x, ch1_h - 1 + y))
    return build_walls_around_floor(floor)


def bp_butterfly(wing_w=3, wing_h=6, neck_w=4, neck_h=2):
    floor = set()
    for x in range(wing_w):
        for y in range(wing_h):
            floor.add((x, y))
    ny = (wing_h - neck_h) // 2
    for x in range(neck_w):
        for y in range(neck_h):
            floor.add((wing_w + x, ny + y))
    for x in range(wing_w):
        for y in range(wing_h):
            floor.add((wing_w + neck_w + x, y))
    return build_walls_around_floor(floor)


def bp_stepped_hall():
    floor = set()
    for x in range(3):
        for y in range(3):
            floor.add((x, y))
    for x in range(3):
        for y in range(3):
            floor.add((1 + x, 2 + y))
    for x in range(3):
        for y in range(3):
            floor.add((2 + x, 4 + y))
    return build_walls_around_floor(floor)


def bp_chute_bays(chute_h=6, bay_w=3, bay_h=3):
    floor = set()
    for y in range(chute_h):
        floor.add((1, y))
        floor.add((2, y))
    for x in range(bay_w):
        for y in range(bay_h):
            floor.add((3 + x, 1 + y))
    return build_walls_around_floor(floor)


def solve_bfs(w, h, walls, goals, crates, player, max_states=45000):
    if crates == goals:
        return True, 0, 0, ""

    dirs = [
        ((0, -1), 'u'),
        ((0, 1), 'd'),
        ((-1, 0), 'l'),
        ((1, 0), 'r')
    ]

    start_crates = tuple(sorted(crates))
    queue = collections.deque([(player, start_crates, "", 0)])
    visited = {(player, start_crates)}

    def is_deadlock(pos):
        if pos in goals:
            return False
        w_u = (pos[0], pos[1]-1) in walls or pos[1] <= 0
        w_d = (pos[0], pos[1]+1) in walls or pos[1] >= h - 1
        w_l = (pos[0]-1, pos[1]) in walls or pos[0] <= 0
        w_r = (pos[0]+1, pos[1]) in walls or pos[0] >= w - 1
        return (w_u and w_l) or (w_u and w_r) or (w_d and w_l) or (w_d and w_r)

    states_count = 0
    while queue:
        states_count += 1
        if states_count > max_states:
            return False, 0, 0, "TIMEOUT"

        p, c_tuple, moves_str, pushes_count = queue.popleft()
        c_set = set(c_tuple)

        for (dx, dy), m_char in dirs:
            np = (p[0] + dx, p[1] + dy)
            if np in walls or np[0] < 0 or np[0] >= w or np[1] < 0 or np[1] >= h:
                continue

            if np in c_set:
                n_crate = (np[0] + dx, np[1] + dy)
                if n_crate in walls or n_crate in c_set or n_crate[0] < 0 or n_crate[0] >= w or n_crate[1] < 0 or n_crate[1] >= h:
                    continue
                if is_deadlock(n_crate):
                    continue

                new_c_set = set(c_set)
                new_c_set.remove(np)
                new_c_set.add(n_crate)

                if new_c_set == goals:
                    return True, len(moves_str) + 1, pushes_count + 1, moves_str + m_char

                new_c_tuple = tuple(sorted(new_c_set))
                nxt_state = (np, new_c_tuple)
                if nxt_state not in visited:
                    visited.add(nxt_state)
                    queue.append((np, new_c_tuple, moves_str + m_char, pushes_count + 1))
            else:
                nxt_state = (np, c_tuple)
                if nxt_state not in visited:
                    visited.add(nxt_state)
                    queue.append((np, c_tuple, moves_str + m_char, pushes_count))

    return False, 0, 0, "UNSOLVABLE"


def generate_single_level(blueprint_func, bp_args, num_crates, min_moves, max_moves=70, max_attempts=120):
    for attempt in range(max_attempts):
        w, h, walls, floor = blueprint_func(*bp_args)
        floor_cells = list(floor)
        if len(floor_cells) < num_crates + 2:
            continue

        # Choose goal cluster
        anchor = random.choice(floor_cells)
        sorted_by_dist = sorted(floor_cells, key=lambda c: (c[0]-anchor[0])**2 + (c[1]-anchor[1])**2)
        goals = set(sorted_by_dist[:num_crates])
        crates = set(goals)

        # Place player
        adj = []
        for cx, cy in crates:
            for (dx, dy), _ in DIRS:
                np = (cx + dx, cy + dy)
                if np in floor and np not in crates:
                    adj.append(np)
        if not adj:
            continue
        player = random.choice(adj)

        # Reverse pull walk
        num_pulls = random.randint(40, 160)
        for _ in range(num_pulls):
            if random.random() < 0.65:
                adj_c = []
                for c in crates:
                    dx, dy = c[0] - player[0], c[1] - player[1]
                    if abs(dx) + abs(dy) == 1:
                        adj_c.append((c, (dx, dy)))
                if adj_c:
                    c, (dx, dy) = random.choice(adj_c)
                    new_p = (player[0] - dx, player[1] - dy)
                    if new_p in floor and new_p not in crates:
                        crates.remove(c)
                        crates.add(player)
                        player = new_p
            else:
                (dx, dy), _ = random.choice(DIRS)
                new_p = (player[0] + dx, player[1] + dy)
                if new_p in floor and new_p not in crates:
                    player = new_p

        if crates == goals:
            continue

        solvable, moves, pushes, sol = solve_bfs(w, h, walls, goals, crates, player, max_states=40000)
        if solvable and min_moves <= moves <= max_moves and pushes >= num_crates:
            return {
                "width": w,
                "height": h,
                "walls": walls,
                "goals": goals,
                "crates": crates,
                "player": player,
                "moves": moves,
                "pushes": pushes,
                "solution": sol
            }
    return None


def format_sokoban_text(lvl_data, title, level_num):
    w = lvl_data["width"]
    h = lvl_data["height"]
    walls = lvl_data["walls"]
    goals = lvl_data["goals"]
    crates = lvl_data["crates"]
    player = lvl_data["player"]
    moves = lvl_data["moves"]
    pushes = lvl_data["pushes"]

    lines = [
        f"; Level {level_num}: {title} ({w}x{h}, {len(crates)} crates)",
        f"; Verified solvable: {moves} moves, {pushes} pushes"
    ]

    for y in range(h):
        row = []
        for x in range(w):
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
        lines.append(''.join(row).rstrip())
    return '\n'.join(lines) + '\n'


# Handcrafted organic templates for introductory and key levels
HANDCRAFTED_LEVELS = {
    1: """
######
#   .#
# $  ##
# @   #
#     #
#######
""",
    4: """
  ###  
  #.#  
###$###
#.$@$.#
###$###
  #.#  
  ###  
"""
}


def parse_raw_map(text):
    lines = [l.rstrip('\r\n') for l in text.strip().split('\n') if l.strip() and not l.startswith(';')]
    h = len(lines)
    w = max(len(l) for l in lines)
    walls = set()
    goals = set()
    crates = set()
    player = None
    for y, line in enumerate(lines):
        for x, ch in enumerate(line):
            pos = (x, y)
            if ch == '#': walls.add(pos)
            elif ch == '.': goals.add(pos)
            elif ch == '$': crates.add(pos)
            elif ch == '*': crates.add(pos); goals.add(pos)
            elif ch == '@': player = pos
            elif ch == '+': player = pos; goals.add(pos)
    return w, h, walls, goals, crates, player


def generate_all_50_levels():
    random.seed(1337)
    results = {}
    optimal_moves = []

    print("\n" + "="*60)
    print("   GENERATING 50 ORGANIC SOLVABLE LEVELS FOR PIXEL PORTER   ")
    print("="*60 + "\n")

    for lvl in range(1, 51):
        title = LEVEL_TITLES.get(lvl, f"Warehouse Shift {lvl}")
        data = None

        # Tier & Blueprint selection based on level index
        if lvl in HANDCRAFTED_LEVELS:
            raw = HANDCRAFTED_LEVELS[lvl]
            w, h, walls, goals, crates, player = parse_raw_map(raw)
            solv, m, p, sol = solve_bfs(w, h, walls, goals, crates, player)
            if solv:
                data = {
                    "width": w, "height": h, "walls": walls, "goals": goals,
                    "crates": crates, "player": player, "moves": m, "pushes": p, "solution": sol
                }

        if data is None:
            # Procedural organic generation per Tier:
            if lvl <= 5: # Tier 1 intro: 1 crate, 8-16 moves
                bp = random.choice([bp_l_bend, bp_t_junction, bp_stepped_hall])
                args = (3, 3, 3, 3, 2, 2) if bp == bp_l_bend else ((5, 2, 2, 3, 1) if bp == bp_t_junction else ())
                data = generate_single_level(bp, args, 1, 8, 16)
            elif lvl <= 15: # Tier 1-2: 2 crates, 10-22 moves
                bp = random.choice([bp_l_bend, bp_s_curve, bp_t_junction, bp_stepped_hall, bp_chute_bays, bp_island_loop])
                if bp == bp_l_bend: args = (3, 3, 3, 3, 2, 2)
                elif bp == bp_s_curve: args = (3, 3, 3, 3, 2)
                elif bp == bp_t_junction: args = (5, 2, 2, 3, 1)
                elif bp == bp_stepped_hall: args = ()
                elif bp == bp_chute_bays: args = (6, 3, 3)
                else: args = (7, 7) # bp_island_loop
                data = generate_single_level(bp, args, 2, 10, 22)
            elif lvl <= 30: # Tier 3 (Chapter 1 end / Chapter 2): 2-3 crates, 14-28 moves
                bp = random.choice([bp_cross, bp_island_loop, bp_s_curve, bp_chute_bays, bp_stepped_hall, bp_butterfly])
                crates_cnt = 2 if lvl <= 22 else 3
                if bp == bp_cross: args = (3, 2, 2)
                elif bp == bp_island_loop: args = (7, 7)
                elif bp == bp_s_curve: args = (3, 3, 3, 3, 2)
                elif bp == bp_chute_bays: args = (6, 3, 3)
                elif bp == bp_stepped_hall: args = ()
                else: args = (3, 6, 4, 2) # bp_butterfly
                data = generate_single_level(bp, args, crates_cnt, 12, 28)
            elif lvl <= 45: # Tier 4 (Chapter 2 end / Chapter 3): 3-4 crates, 16-35 moves
                bp = random.choice([bp_cross, bp_butterfly, bp_island_loop, bp_s_curve, bp_chute_bays, bp_stepped_hall])
                crates_cnt = 3 if lvl <= 38 else 4
                if bp == bp_cross: args = (3, 2, 2)
                elif bp == bp_butterfly: args = (3, 6, 4, 2)
                elif bp == bp_island_loop: args = (7, 7)
                elif bp == bp_s_curve: args = (3, 3, 3, 3, 2)
                elif bp == bp_chute_bays: args = (6, 3, 3)
                else: args = () # bp_stepped_hall
                data = generate_single_level(bp, args, crates_cnt, 14, 35)
            else: # Tier 5 (Chapter 3 climax): 4-5 crates, 20-45 moves
                bp = random.choice([bp_cross, bp_butterfly, bp_island_loop, bp_chute_bays])
                crates_cnt = 4 if lvl < 50 else 5
                if bp == bp_cross: args = (3, 2, 2)
                elif bp == bp_butterfly: args = (3, 6, 4, 2)
                elif bp == bp_island_loop: args = (7, 7)
                else: args = (6, 3, 3) # bp_chute_bays
                data = generate_single_level(bp, args, crates_cnt, 16, 45)

        # Fallback if specific generator timed out
        if data is None:
            data = generate_single_level(bp_l_bend, (3, 3, 3, 3, 2, 2), 2, 8, 30)

        results[lvl] = data
        optimal_moves.append(data["moves"])

        # Write to disk
        out_path = f"levels/level_{lvl:02d}.sok"
        content = format_sokoban_text(data, title, lvl)
        with open(out_path, "w") as f:
            f.write(content)

        print(f"[{lvl:02d}/50] Level {lvl:02d}: {title:22s} | {data['width']}x{data['height']} | {len(data['crates'])} crates | {data['moves']:2d} moves | {data['pushes']:2d} pushes | PASS ✓")

    print("\n" + "="*60)
    print("ALL 50 LEVELS SUCCESSFULLY GENERATED AND VERIFIED!")
    print("="*60 + "\n")

    # Update save_manager.gd OPTIMAL_MOVES
    save_mgr_path = "scripts/save_manager.gd"
    if os.path.exists(save_mgr_path):
        with open(save_mgr_path, "r") as f:
            sm_content = f.read()

        moves_formatted = "const OPTIMAL_MOVES: Array[int] = [\n"
        for i in range(0, 50, 10):
            chunk = optimal_moves[i:i+10]
            moves_formatted += "\t" + ", ".join(str(m) for m in chunk) + (",\n" if i + 10 < 50 else "\n")
        moves_formatted += "]"

        pattern = r"const OPTIMAL_MOVES: Array\[int\] = \[[^\]]*\]"
        new_sm_content = re.sub(pattern, moves_formatted, sm_content, flags=re.MULTILINE)

        with open(save_mgr_path, "w") as f:
            f.write(new_sm_content)
        print("Updated scripts/save_manager.gd OPTIMAL_MOVES array.")

    return optimal_moves


if __name__ == '__main__':
    generate_all_50_levels()

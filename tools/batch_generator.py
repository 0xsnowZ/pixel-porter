#!/usr/bin/env python3
import random
import os
import sys

from generate_pipeline import generate_candidate

TIER_NAMES = {
    # 11-15 (Tier 2: 7x7, 2 crates)
    11: "Side Step",
    12: "Switchback",
    13: "Crossroads",
    14: "Twin Pillars",
    15: "Storage Nook",
    # 16-30 (Tier 3: 8x8, 2-3 crates)
    16: "Chamber Shuffle",
    17: "The Alcove",
    18: "Bypass Lane",
    19: "Square Dance",
    20: "Divided Hall",
    21: "Cargo Hold",
    22: "Docking Station",
    23: "Narrow Passage",
    24: "Box Canyon",
    25: "Turnstile",
    26: "Symmetric Split",
    27: "Vault Corridor",
    28: "Central Island",
    29: "Fork in the Road",
    30: "The Quad",
    # 31-45 (Tier 4: 9x9, 3-4 crates)
    31: "Warehouse Maze",
    32: "Freight Bay",
    33: "Blockade Runner",
    34: "Tetris Corridor",
    35: "The Citadel",
    36: "Labyrinthine",
    37: "Column Grid",
    38: "Inner Sanctum",
    39: "Cargo Congestion",
    40: "Gridlock",
    41: "Grand Depot",
    42: "Pallet Stack",
    43: "Double Bypass",
    44: "Forked Gallery",
    45: "Iron Vault",
    # 46-50 (Tier 5: 10x10, 4-5 crates)
    46: "Master's Gallery",
    47: "Cathedral of Crates",
    48: "The Great Hall",
    49: "Grand Labyrinth",
    50: "The Final Gauntlet"
}

def generate_tier(w, h, num_crates, num_obstacles, min_moves, count, start_lvl):
    print(f"\nGenerating {count} levels for Tier ({w}x{h}, {num_crates} crates, min_moves={min_moves})...")
    candidates = []
    seen_hashes = set()

    attempts = 0
    while len(candidates) < count and attempts < 1200:
        attempts += 1
        cand = generate_candidate(w, h, num_crates, num_obstacles, min_moves=min_moves, max_attempts=1)
        if cand:
            h_key = (frozenset(cand['crates']), frozenset(cand['goals']))
            if h_key in seen_hashes:
                continue
            seen_hashes.add(h_key)
            candidates.append(cand)
            print(f"  [Found {len(candidates)}/{count}] Moves={cand['moves']}, Pushes={cand['pushes']}")

    if len(candidates) < count:
        print(f"Warning: only generated {len(candidates)} of {count} candidates.")

    # Sort candidates by moves + pushes (difficulty ramp)
    candidates.sort(key=lambda c: (c['moves'] * 1.5 + c['pushes'] * 2.0))
    return candidates[:count]

def main():
    random.seed(42) # Deterministic reproducibility

    results = {}

    # Tier 2: Levels 11-15 (7x7, 2 crates, min_moves 8)
    t2 = generate_tier(7, 7, num_crates=2, num_obstacles=2, min_moves=8, count=5, start_lvl=11)
    for i, c in enumerate(t2):
        results[11 + i] = c

    # Tier 3: Levels 16-30 (8x8, 2 to 3 crates, min_moves 10)
    # First 8 with 2 crates, next 7 with 3 crates
    t3_a = generate_tier(8, 8, num_crates=2, num_obstacles=3, min_moves=10, count=7, start_lvl=16)
    t3_b = generate_tier(8, 8, num_crates=3, num_obstacles=2, min_moves=11, count=8, start_lvl=23)
    t3 = t3_a + t3_b
    t3.sort(key=lambda c: (c['moves'] * 1.5 + c['pushes'] * 2.0))
    for i, c in enumerate(t3):
        results[16 + i] = c

    # Tier 4: Levels 31-45 (9x9, 3 to 4 crates, min_moves 12)
    # 8 with 3 crates, 7 with 4 crates
    t4_a = generate_tier(9, 9, num_crates=3, num_obstacles=4, min_moves=12, count=8, start_lvl=31)
    t4_b = generate_tier(9, 9, num_crates=4, num_obstacles=3, min_moves=13, count=7, start_lvl=39)
    t4 = t4_a + t4_b
    t4.sort(key=lambda c: (c['moves'] * 1.5 + c['pushes'] * 2.0))
    for i, c in enumerate(t4):
        results[31 + i] = c

    # Tier 5: Levels 46-50 (10x10, 4 crates, min_moves 14)
    t5 = generate_tier(10, 10, num_crates=4, num_obstacles=5, min_moves=14, count=5, start_lvl=46)
    t5.sort(key=lambda c: (c['moves'] * 1.5 + c['pushes'] * 2.0))
    for i, c in enumerate(t5):
        results[46 + i] = c

    # Write out levels 11 to 50
    os.makedirs("levels", exist_ok=True)
    for lvl in range(11, 51):
        cand = results.get(lvl)
        if not cand:
            print(f"Error: Missing level {lvl}")
            continue

        name = TIER_NAMES.get(lvl, f"Level {lvl}")
        filename = f"levels/level_{lvl:02d}.sok"
        content = f"; Level {lvl}: {name} ({cand['width']}x{cand['height']}, {len(cand['crates'])} crates)\n"
        content += f"; Verified solvable: {cand['moves']} moves, {cand['pushes']} pushes\n"
        content += cand['text'] + "\n"

        with open(filename, "w") as f:
            f.write(content)
        print(f"Wrote {filename}: {cand['moves']} moves, {cand['pushes']} pushes")

if __name__ == '__main__':
    main()

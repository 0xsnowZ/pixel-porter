#!/usr/bin/env python3
"""
tools/order_and_verify_campaign.py

Orders all 50 levels into an authentic, professional difficulty progression.
Verifies every level via BFS shortest-path search.
Outputs the complete OPTIMAL_MOVES array for scripts/save_manager.gd.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.build_professional_campaign import parse_sokoban, solve_sokoban
from tools.curate_full_campaign import LEVELS as RAW_LEVELS

# We assign each raw level to its curated slot in the campaign
ORDER_MAP = [
    # Chapter 1: The Warehouse Depot (Levels 1 - 15)
    (1, 1, "First Steps"),
    (2, 2, "Around the Pillar"),
    (3, 4, "Switchback Alley"),
    (4, 3, "The Winding Hall"),
    (5, 5, "Corner Caution"),
    (6, 6, "Dual Cargo"),
    (7, 14, "Airlock Choke"),
    (8, 12, "Asymmetric Alcove"),
    (9, 10, "Twin Pillars"),
    (10, 16, "Cold Entry"),
    (11, 7, "Passing Pocket"),
    (12, 9, "T-Junction Depot"),
    (13, 8, "Sequential Bay"),
    (14, 11, "Siding Maneuver"),
    (15, 13, "Central Cross"),
    
    # Chapter 2: Cold Storage (Levels 16 - 35)
    (16, 15, "The Turnstile"),
    (17, 22, "Frost Chute"),
    (18, 18, "Triple Threat"),
    (19, 26, "Double Bay Staging"),
    (20, 20, "T-Vault"),
    (21, 28, "Clean Cross Vault"),
    (22, 21, "Clean Depot"),
    (23, 24, "Freezer Bypass"),
    (24, 23, "Frostbite Loop"),
    (25, 29, "Permafrost Corridor"),
    (26, 36, "Tetris Core"),
    (27, 30, "Cryo Sanctum"),
    (28, 27, "Glacier Gallery"),
    (29, 19, "Freezer Airlock"),
    (30, 25, "Icebox Tetris"),
    
    # Chapter 3: Cyber Cargo (Levels 31 - 50)
    (31, 47, "Cyber Sanctum"),
    (32, 31, "Cyber Conduit"),
    (33, 43, "Double Bypass"),
    (34, 41, "Data Vault"),
    (35, 42, "Pallet Matrix"),
    (36, 40, "Grand Depot"),
    (37, 44, "Forked Gallery"),
    (38, 37, "Column Matrix"),
    (39, 45, "Iron Grid"),
    (40, 35, "Gridlock Bay"),
    (41, 46, "Master's Gallery"),
    (42, 39, "Cargo Congestion"),
    (43, 34, "Terminal Node"),
    (44, 32, "Quad Dock"),
    (45, 33, "Pinwheel Core"),
    (46, 38, "Inner Sanctum"),
    (47, 17, "Frosty Pocket"),
    (48, 50, "The Final Gauntlet"),
    (49, 48, "Cathedral of Crates"),
    (50, 49, "The Great Hall")
]

FINAL_LEVELS = {}
OPTIMAL_MOVES = []
OPTIMAL_PUSHES = []

print("=" * 80)
print("   PIXEL PORTER - 50-LEVEL PROFESSIONAL CAMPAIGN PROGRESSION   ")
print("=" * 80)
print(f"{'Lvl':<5} | {'Size':<6} | {'Crates':<6} | {'Moves':<6} | {'Pushes':<6} | {'Push %':<7} | {'Title'}")
print("-" * 80)

for target_slot, raw_slot, title in ORDER_MAP:
    raw_map = RAW_LEVELS[raw_slot]["map"].strip()
    w, h, walls, goals, crates, player = parse_sokoban(raw_map)
    nc = len(crates)
    
    res, m, p, path = solve_sokoban(w, h, walls, goals, crates, player, max_states=60000)
    assert res, f"Level {target_slot} ({title}) failed solve!"
    
    ratio = (p / m) * 100 if m else 0
    print(f"Lvl {target_slot:02d} | {w}x{h:<3} | {nc:<6} | {m:<6} | {p:<6} | {ratio:5.1f}% | {title}")
    
    FINAL_LEVELS[target_slot] = {
        "name": title,
        "width": w,
        "height": h,
        "crates": nc,
        "moves": m,
        "pushes": p,
        "path": path,
        "map": raw_map
    }
    OPTIMAL_MOVES.append(m)
    OPTIMAL_PUSHES.append(p)

print("=" * 80)
print(f"Total Campaign Moves : {sum(OPTIMAL_MOVES)} (avg {sum(OPTIMAL_MOVES)/50:.1f})")
print(f"Total Campaign Pushes: {sum(OPTIMAL_PUSHES)} (avg {sum(OPTIMAL_PUSHES)/50:.1f})")
print(f"Overall Push Density : {sum(OPTIMAL_PUSHES)/sum(OPTIMAL_MOVES)*100:.1f}%")
print("=" * 80)
print("\nOPTIMAL_MOVES Array:")
print(OPTIMAL_MOVES)

#!/usr/bin/env python3
"""
tools/curate_full_campaign.py

Assembles and verifies all 50 professional Sokoban levels for Pixel Porter.
Every level is verified solvable via BFS shortest-path search.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.build_professional_campaign import parse_sokoban, solve_sokoban

LEVELS = {}

# ==============================================================================
# CHAPTER 1: THE WAREHOUSE DEPOT (Levels 1 - 15)
# Environment: Red Brick Depot, High Visibility
# Crates: 1 crate (Levels 1-5), 2 crates (Levels 6-15)
# ==============================================================================

# Level 1: First Steps (6x6, 1 crate) [Fixture required by test_grid_logic.gd]
LEVELS[1] = {
    "name": "First Steps",
    "map": """
######
#   .#
# $  #
# @  #
#    #
######
"""
}

# Level 2: Around the Pillar (6x6, 1 crate)
LEVELS[2] = {
    "name": "Around the Pillar",
    "map": """
######
#   .#
# #  #
# $  #
#  @ #
######
"""
}

# Level 3: The Winding Hall (6x6, 1 crate)
LEVELS[3] = {
    "name": "The Winding Hall",
    "map": """
######
#  . #
#  # #
#  $ #
# @  #
######
"""
}

# Level 4: Switchback Alley (7x7, 1 crate)
LEVELS[4] = {
    "name": "Switchback Alley",
    "map": """
#######
#   . #
#  ## #
#  $  #
#  @  #
#     #
#######
"""
}

# Level 5: Corner Caution (7x7, 1 crate)
LEVELS[5] = {
    "name": "Corner Caution",
    "map": """
#######
#  .  #
#  #  #
#  $  #
# @#  #
#     #
#######
"""
}

# Level 6: Dual Cargo (7x7, 2 crates)
LEVELS[6] = {
    "name": "Dual Cargo",
    "map": """
#######
# . $ #
#  $  #
#  .  #
#  @  #
#     #
#######
"""
}

# Level 7: Passing Pocket (7x7, 2 crates)
LEVELS[7] = {
    "name": "Passing Pocket",
    "map": """
#######
#. $ .#
#     #
#  #  #
#  $  #
#@    #
#######
"""
}

# Level 8: Sequential Bay (7x7, 2 crates)
LEVELS[8] = {
    "name": "Sequential Bay",
    "map": """
#######
#   . #
# # . #
# # $ #
# $ @ #
#     #
#######
"""
}

# Level 9: T-Junction Depot (7x7, 2 crates)
LEVELS[9] = {
    "name": "T-Junction Depot",
    "map": """
#######
# . . #
#  #  #
#  $  #
# $#  #
#  @  #
#######
"""
}

# Level 10: Twin Pillars (7x8, 2 crates)
LEVELS[10] = {
    "name": "Twin Pillars",
    "map": """
#######
# . $ #
# # # #
#     #
# # # #
# $ . #
#  @  #
#######
"""
}

# Level 11: Siding Maneuver (7x8, 2 crates)
LEVELS[11] = {
    "name": "Siding Maneuver",
    "map": """
#######
# .   #
#  $  #
#  #  #
#  $  #
#   . #
#  @  #
#######
"""
}

# Level 12: Asymmetric Alcove (7x7, 2 crates)
LEVELS[12] = {
    "name": "Asymmetric Alcove",
    "map": """
#######
# . $ #
# #   #
#   # #
# $ . #
#  @  #
#######
"""
}

# Level 13: Central Cross (7x8, 2 crates)
LEVELS[13] = {
    "name": "Central Cross",
    "map": """
#######
#  .  #
#  #  #
# $ $ #
#  #  #
#  .  #
#  @  #
#######
"""
}

# Level 14: Airlock Choke (8x8, 2 crates)
LEVELS[14] = {
    "name": "Airlock Choke",
    "map": """
########
# .  # #
# $  # #
#  #   #
#  # $ #
#  # . #
#  @   #
########
"""
}

# Level 15: The Turnstile (8x9, 2 crates)
LEVELS[15] = {
    "name": "The Turnstile",
    "map": """
########
# . $  #
# ##   #
#    # #
# #    #
#   ## #
#  $ . #
#  @   #
########
"""
}

# ==============================================================================
# CHAPTER 2: COLD STORAGE (Levels 16 - 35)
# Environment: Frostbite Vault, Dual-Chamber Warehouses
# Crates: 2 crates (Levels 16-17), 3 crates (Levels 18-30), 4 crates (Levels 31-35)
# ==============================================================================

# Level 16: Cold Entry (7x8, 2 crates)
LEVELS[16] = {
    "name": "Cold Entry",
    "map": """
#######
# . $ #
#     #
# # # #
#     #
# $ . #
#  @  #
#######
"""
}

# Level 17: Frosty Pocket (8x7, 2 crates)
LEVELS[17] = {
    "name": "Frosty Pocket",
    "map": """
########
#  . . #
#  # # #
#  $ $ #
#  # # #
#   @  #
########
"""
}

# Level 18: Triple Threat (7x7, 3 crates)
LEVELS[18] = {
    "name": "Triple Threat",
    "map": """
#######
# . . #
#  $  #
# $ $ #
#  .  #
#  @  #
#######
"""
}

# Level 19: Freezer Airlock (8x8, 3 crates)
LEVELS[19] = {
    "name": "Freezer Airlock",
    "map": """
########
# .    #
# #. # #
# #$ $ #
# #. # #
# $    #
#   @  #
########
"""
}

# Level 20: T-Vault (7x8, 3 crates)
LEVELS[20] = {
    "name": "T-Vault",
    "map": """
#######
# . . #
#  $  #
#  #  #
# $ $ #
#  .  #
#  @  #
#######
"""
}

# Level 21: Clean Depot (7x8, 3 crates)
LEVELS[21] = {
    "name": "Clean Depot",
    "map": """
#######
# . . #
#  $  #
#  $  #
#  #  #
# $ . #
#  @  #
#######
"""
}

# Level 22: Frost Chute (7x8, 3 crates)
LEVELS[22] = {
    "name": "Frost Chute",
    "map": """
#######
# . . #
#  $  #
# $ $ #
#  .  #
#  #  #
#  @  #
#######
"""
}

# Level 23: Frostbite Loop (8x9, 3 crates)
LEVELS[23] = {
    "name": "Frostbite Loop",
    "map": """
########
# .  . #
#  $   #
#  ##  #
#  $   #
#  ##  #
# $  . #
#  @   #
########
"""
}

# Level 24: Freezer Bypass (8x8, 3 crates)
LEVELS[24] = {
    "name": "Freezer Bypass",
    "map": """
########
# .  $ #
# #  # #
# .  $ #
# #  # #
# .  $ #
#   @  #
########
"""
}

# Level 25: Icebox Tetris (7x8, 3 crates)
LEVELS[25] = {
    "name": "Icebox Tetris",
    "map": """
#######
# . $ #
# $ # #
#  $  #
# # . #
#  .  #
#  @  #
#######
"""
}

# Level 26: Double Bay Staging (7x7, 3 crates)
LEVELS[26] = {
    "name": "Double Bay Staging",
    "map": """
#######
# . $ #
# . $ #
# . $ #
#     #
#  @  #
#######
"""
}

# Level 27: Glacier Gallery (8x8, 3 crates)
LEVELS[27] = {
    "name": "Glacier Gallery",
    "map": """
########
#  .   #
# .#.# #
#  $   #
#  #   #
# $#$  #
#  @   #
########
"""
}

# Level 28: Clean Cross Vault (7x7, 3 crates)
LEVELS[28] = {
    "name": "Clean Cross Vault",
    "map": """
#######
#  .  #
# .#. #
#  $  #
# $ $ #
#  @  #
#######
"""
}

# Level 29: Permafrost Corridor (7x8, 3 crates)
LEVELS[29] = {
    "name": "Permafrost Corridor",
    "map": """
#######
# . $ #
#  #  #
# $ . #
#  #  #
# . $ #
#  @  #
#######
"""
}

# Level 30: Cryo Sanctum (7x8, 3 crates)
LEVELS[30] = {
    "name": "Cryo Sanctum",
    "map": """
#######
# . $ #
#  #  #
# $ $ #
#  #  #
# . . #
#  @  #
#######
"""
}

# ==============================================================================
# CHAPTER 3: CYBER CARGO (Levels 31 - 50)
# Environment: Cyber Matrix, Advanced Multi-Crate Logistics
# Crates: 4 crates (Levels 31-47), 5 crates (Levels 48-50)
# ==============================================================================

# Level 31: Cyber Conduit (7x7, 4 crates) [Intro 4 Crates]
LEVELS[31] = {
    "name": "Cyber Conduit",
    "map": """
#######
# . . #
# $ $ #
#  @  #
# $ $ #
# . . #
#######
"""
}

# Level 32: Quad Dock (7x7, 4 crates)
LEVELS[32] = {
    "name": "Quad Dock",
    "map": """
#######
# . $ #
# . $ #
#  @  #
# . $ #
# . $ #
#######
"""
}

# Level 33: Pinwheel Core (7x7, 4 crates)
LEVELS[33] = {
    "name": "Pinwheel Core",
    "map": """
#######
# . $ #
# $ . #
#  @  #
# . $ #
# $ . #
#######
"""
}

# Level 34: Terminal Node (7x8, 4 crates)
LEVELS[34] = {
    "name": "Terminal Node",
    "map": """
#######
# . $ #
#  #  #
# . $ #
#  @  #
# $ . #
# $ . #
#######
"""
}

# Level 35: Gridlock Bay (7x7, 4 crates with 1 staged)
LEVELS[35] = {
    "name": "Gridlock Bay",
    "map": """
#######
# . $ #
# . $ #
#  @  #
# . $ #
# *   #
#######
"""
}

# Level 36: Tetris Core (7x7, 3 crates breather)
LEVELS[36] = {
    "name": "Tetris Core",
    "map": """
#######
# . $ #
#  $  #
#  #  #
# $ . #
#  .  #
#  @  #
#######
"""
}

# Level 37: Column Matrix (7x7, 4 crates with 2 staged)
LEVELS[37] = {
    "name": "Column Matrix",
    "map": """
#######
# . $ #
# *   #
#  @  #
# *   #
# . $ #
#######
"""
}

# Level 38: Inner Sanctum (7x9, 4 crates)
LEVELS[38] = {
    "name": "Inner Sanctum",
    "map": """
#######
# . $ #
# # # #
# . $ #
#  @  #
# . $ #
# # # #
# . $ #
#######
"""
}

# Level 39: Cargo Congestion (7x7, 4 crates)
LEVELS[39] = {
    "name": "Cargo Congestion",
    "map": """
#######
# . . #
# $ $ #
#  #  #
# $ $ #
# . . #
#  @  #
#######
"""
}

# Level 40: Grand Depot (7x8, 4 crates)
LEVELS[40] = {
    "name": "Grand Depot",
    "map": """
#######
# . $ #
# *   #
#  @  #
# . $ #
# *   #
#######
"""
}

# Level 41: Data Vault (7x8, 4 crates)
LEVELS[41] = {
    "name": "Data Vault",
    "map": """
#######
# *   #
# . $ #
#  @  #
# . $ #
# *   #
#######
"""
}

# Level 42: Pallet Matrix (7x8, 4 crates)
LEVELS[42] = {
    "name": "Pallet Matrix",
    "map": """
#######
# . $ #
# . $ #
#  #  #
#  @  #
# *   #
# *   #
#######
"""
}

# Level 43: Double Bypass (7x8, 4 crates)
LEVELS[43] = {
    "name": "Double Bypass",
    "map": """
#######
# *   #
# *   #
#  #  #
#  @  #
# . $ #
# . $ #
#######
"""
}

# Level 44: Forked Gallery (7x7, 4 crates)
LEVELS[44] = {
    "name": "Forked Gallery",
    "map": """
#######
# . $ #
# *   #
#  @  #
# . $ #
#   * #
#######
"""
}

# Level 45: Iron Grid (7x7, 4 crates)
LEVELS[45] = {
    "name": "Iron Grid",
    "map": """
#######
# . $ #
#   * #
#  @  #
#   * #
# . $ #
#######
"""
}

# Level 46: Master's Gallery (7x8, 4 crates)
LEVELS[46] = {
    "name": "Master's Gallery",
    "map": """
#######
# * . #
# $   #
#  @  #
# $   #
# * . #
#######
"""
}

# Level 47: Cyber Sanctum (7x8, 4 crates)
LEVELS[47] = {
    "name": "Cyber Sanctum",
    "map": """
#######
# . * #
# $   #
#  @  #
# $   #
# . * #
#######
"""
}

# Level 48: Cathedral of Crates (7x8, 5 crates) [Intro 5 Crates]
LEVELS[48] = {
    "name": "Cathedral of Crates",
    "map": """
#######
# *   #
# . $ #
# *   #
#  @  #
# *   #
# . $ #
#######
"""
}

# Level 49: The Great Hall (7x8, 5 crates)
LEVELS[49] = {
    "name": "The Great Hall",
    "map": """
#######
# . $ #
# *   #
# *   #
#  @  #
# *   #
# . $ #
#######
"""
}

# Level 50: The Final Gauntlet (7x8, 5 crates) [Grand Finale]
LEVELS[50] = {
    "name": "The Final Gauntlet",
    "map": """
#######
# *   #
# *   #
# . $ #
#  @  #
# . $ #
# *   #
#######
"""
}

if __name__ == '__main__':
    print("Testing 50 professional candidate levels...")
    solved_count = 0
    total_moves = 0
    total_pushes = 0
    failures = []
    
    for lvl in range(1, 51):
        info = LEVELS[lvl]
        w, h, walls, goals, crates, player = parse_sokoban(info["map"])
        nc = len(crates)
        ng = len(goals)
        if nc != ng:
            failures.append((lvl, f"crates({nc}) != goals({ng})"))
            continue
            
        res, m, p, path = solve_sokoban(w, h, walls, goals, crates, player, max_states=60000)
        ratio = (p / m) if m else 0
        status = "PASS" if res else "FAIL"
        
        if res:
            solved_count += 1
            total_moves += m
            total_pushes += p
            print(f"Lvl {lvl:02d} | {w}x{h} | {nc} crates | {m:2d} moves | {p:2d} pushes | ratio={ratio:.2f} | {status} | {info['name']}")
        else:
            failures.append((lvl, f"UNSOLVABLE/TIMEOUT ({info['name']})"))
            print(f"Lvl {lvl:02d} | {w}x{h} | {nc} crates | FAIL | {info['name']}")
            
    print("-" * 75)
    print(f"Result: {solved_count}/50 levels verified solvable!")
    if solved_count == 50:
        print(f"Total moves: {total_moves} (avg {total_moves/50:.1f} per level)")
        print(f"Total pushes: {total_pushes} (avg {total_pushes/50:.1f} per level)")
        print(f"Overall push ratio: {total_pushes/total_moves:.2f}")
    else:
        print(f"Failures: {failures}")

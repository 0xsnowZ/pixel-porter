#!/usr/bin/env python3
"""
tools/test_all_50_levels.py
Designs and tests candidate layouts for all 50 levels.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.build_professional_campaign import parse_sokoban, solve_sokoban

LEVEL_DEFS = {}

# --- CHAPTER 1: THE WAREHOUSE DEPOT (Levels 1 - 15) ---

# Level 1: First Steps (6x6, 1 crate) [Fixture]
LEVEL_DEFS[1] = """
######
#   .#
# $  #
# @  #
#    #
######
"""

# Level 2: Around the Pillar (6x6, 1 crate)
LEVEL_DEFS[2] = """
######
#   .#
# #  #
# $  #
#  @ #
######
"""

# Level 3: The Winding Hall (6x6, 1 crate)
LEVEL_DEFS[3] = """
######
#  . #
#  # #
#  $ #
# @  #
######
"""

# Level 4: Switchback Alley (7x7, 1 crate)
LEVEL_DEFS[4] = """
#######
#   . #
#  ## #
#  $  #
#  @  #
#     #
#######
"""

# Level 5: Corner Caution (7x7, 1 crate)
LEVEL_DEFS[5] = """
#######
#  .  #
#  #  #
#  $  #
# @#  #
#     #
#######
"""

# Level 6: Dual Cargo (7x7, 2 crates)
LEVEL_DEFS[6] = """
#######
# . $ #
#  $  #
#  .  #
#  @  #
#     #
#######
"""

# Level 7: Passing Pocket (7x7, 2 crates)
LEVEL_DEFS[7] = """
#######
#. $ .#
#     #
#  #  #
#  $  #
#@    #
#######
"""

# Level 8: Sequential Bay (7x7, 2 crates)
LEVEL_DEFS[8] = """
#######
#   . #
# # . #
# # $ #
# $ @ #
#     #
#######
"""

# Level 9: T-Junction Depot (7x7, 2 crates)
LEVEL_DEFS[9] = """
#######
# . . #
#  #  #
#  $  #
# $#  #
#  @  #
#######
"""

# Level 10: Twin Pillars (7x7, 2 crates)
LEVEL_DEFS[10] = """
#######
# . $ #
# # # #
#     #
# # # #
# $ . #
#  @  #
#######
"""

# Level 11: Siding Maneuver (7x7, 2 crates)
LEVEL_DEFS[11] = """
#######
# .   #
#  $  #
#  #  #
#  $  #
#   . #
#  @  #
#######
"""

# Level 12: Asymmetric Alcove (7x7, 2 crates)
LEVEL_DEFS[12] = """
#######
# . $ #
# #   #
#   # #
# $ . #
#  @  #
#######
"""

# Level 13: Central Cross (7x7, 2 crates)
LEVEL_DEFS[13] = """
#######
#  .  #
#  #  #
# $#$ #
#  #  #
#  .  #
#  @  #
#######
"""

# Level 14: Airlock Choke (8x7, 2 crates)
LEVEL_DEFS[14] = """
########
# .  # #
# $  # #
#  #   #
#  # $ #
#  # . #
#  @   #
########
"""

# Level 15: The Turnstile (8x8, 2 crates)
LEVEL_DEFS[15] = """
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

# --- CHAPTER 2: COLD STORAGE (Levels 16 - 35) ---

# Level 16: Cold Entry (7x7, 2 crates)
LEVEL_DEFS[16] = """
#######
# . $ #
#     #
# # # #
#     #
# $ . #
#  @  #
#######
"""

# Level 17: Frosty Pocket (8x7, 2 crates)
LEVEL_DEFS[17] = """
########
#  . . #
#  # # #
#  $ $ #
#  # # #
#   @  #
########
"""

# Level 18: Triple Threat (7x7, 3 crates)
LEVEL_DEFS[18] = """
#######
# . . #
#  $  #
# $ $ #
#  .  #
#  @  #
#######
"""

# Level 19: Freezer Airlock (8x8, 3 crates)
LEVEL_DEFS[19] = """
########
# .    #
# #. # #
# #$ $ #
# #. # #
# $    #
#   @  #
########
"""

# Level 20: T-Vault (7x7, 3 crates)
LEVEL_DEFS[20] = """
#######
# . . #
#  $  #
#  #  #
# $ $ #
#  .  #
#  @  #
#######
"""

# Level 21: Clean Depot (7x7, 3 crates)
LEVEL_DEFS[21] = """
#######
# . . #
#  $  #
#  $  #
#  #  #
# $ . #
#  @  #
#######
"""

# Level 22: Depth Lock 3 (8x7, 3 crates)
LEVEL_DEFS[22] = """
########
#    . #
# ## . #
# ## . #
#  $ $ #
#  $   #
#  @   #
########
"""

# Level 23: Frostbite Loop (8x8, 3 crates)
LEVEL_DEFS[23] = """
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

# Level 24: Freezer Bypass (8x8, 3 crates)
LEVEL_DEFS[24] = """
########
# .  $ #
# #  # #
# .  $ #
# #  # #
# .  $ #
#   @  #
########
"""

# Level 25: Icebox Tetris (7x8, 3 crates)
LEVEL_DEFS[25] = """
#######
# . $ #
# $ # #
#  $  #
# # . #
#  .  #
#  @  #
#######
"""

# Level 26: Pallet Transfer (8x8, 3 crates)
LEVEL_DEFS[26] = """
########
# .  . #
# #$ # #
#    # #
# #$ # #
#    # #
# .  $ #
#  @   #
########
"""

# Level 27: Glacier Gallery (8x8, 3 crates)
LEVEL_DEFS[27] = """
########
#  .   #
# .#.# #
#  $   #
#  #   #
# $#$  #
#  @   #
########
"""

# Level 28: Central Cold Hub (8x8, 3 crates)
LEVEL_DEFS[28] = """
########
# .  . #
#  $$  #
#  ##  #
#  $$  #
# .  . #
#  @   #
########
"""

# Level 29: Dual Bay Staging (8x8, 3 crates)
LEVEL_DEFS[29] = """
########
# .  . #
#  $   #
# #  # #
#   $  #
# #  # #
# .  $ #
#  @   #
########
"""

# Level 30: Cryo Sanctum (8x8, 3 crates)
LEVEL_DEFS[30] = """
########
# . $  #
# #.#  #
#   $  #
#  #.# #
#  $   #
#  @   #
########
"""

# --- CHAPTER 3: CYBER CARGO (Levels 31 - 50) ---

# Level 31: Cyber Conduit (8x8, 4 crates)
LEVEL_DEFS[31] = """
########
# .  . #
#  $$  #
# #  # #
#  $$  #
# .  . #
#  @   #
########
"""

# Level 32: Neon Labyrinth (8x8, 4 crates)
LEVEL_DEFS[32] = """
########
# .  . #
# $  $ #
#  ##  #
# $  $ #
# .  . #
#  @   #
########
"""

# Level 33: Blockade Runner (8x8, 4 crates)
LEVEL_DEFS[33] = """
########
# .  . #
#  $$  #
# #  # #
#  $$  #
#  ..  #
#  @   #
########
"""

# Level 34: Terminal Node (8x8, 4 crates)
LEVEL_DEFS[34] = """
########
#  ..  #
#  $$  #
# #  # #
#  $$  #
#  ..  #
#  @   #
########
"""

# Level 35: Gridlock Bay (8x8, 4 crates)
LEVEL_DEFS[35] = """
########
# .  . #
#  $$  #
#  ##  #
#  $$  #
# .  . #
#   @  #
########
"""

# Level 36: Tetris Core (7x7, 3 crates breather)
LEVEL_DEFS[36] = """
#######
# . . #
#  $  #
# #$# #
#  $  #
#  .  #
#  @  #
#######
"""

# Level 37: Column Matrix (8x8, 4 crates)
LEVEL_DEFS[37] = """
########
# .  . #
# #$ # #
# $  $ #
# #$ # #
# .  . #
#  @   #
########
"""

# Level 38: Inner Sanctum (8x8, 4 crates)
LEVEL_DEFS[38] = """
########
#  ..  #
# $##$ #
#      #
# $##$ #
#  ..  #
#  @   #
########
"""

# Level 39: Cargo Congestion (8x8, 4 crates)
LEVEL_DEFS[39] = """
########
# .  . #
#  $$  #
#  ##  #
# $  $ #
# .  . #
#  @   #
########
"""

# Level 40: Grand Depot (8x8, 4 crates)
LEVEL_DEFS[40] = """
########
# .  . #
#  $$  #
#      #
#  $$  #
# .  . #
#  @   #
########
"""

# Level 41: Data Vault (8x8, 4 crates)
LEVEL_DEFS[41] = """
########
#  ..  #
# $  $ #
#  ##  #
# $  $ #
#  ..  #
#  @   #
########
"""

# Level 42: Pallet Matrix (8x8, 4 crates)
LEVEL_DEFS[42] = """
########
# .  . #
# #$$# #
#      #
# #$$# #
# .  . #
#  @   #
########
"""

# Level 43: Double Bypass (8x8, 4 crates)
LEVEL_DEFS[43] = """
########
# .  . #
#  $ $ #
#  ### #
#  $ $ #
# .  . #
#  @   #
########
"""

# Level 44: Forked Gallery (8x8, 4 crates)
LEVEL_DEFS[44] = """
########
#  ..  #
# #  # #
#  $$  #
#  $$  #
#  ..  #
#  @   #
########
"""

# Level 45: Iron Grid (8x8, 4 crates)
LEVEL_DEFS[45] = """
########
# .  . #
# #  # #
#  $$  #
#  $$  #
# #  # #
# .  . #
#  @   #
########
"""

# Level 46: Master's Gallery (8x8, 4 crates)
LEVEL_DEFS[46] = """
########
#  ..  #
# #$$# #
#  ##  #
# #$$# #
#  ..  #
#  @   #
########
"""

# Level 47: Cyber Sanctum (8x8, 4 crates)
LEVEL_DEFS[47] = """
########
# .  . #
#  $$  #
#  ##  #
#  $$  #
#  ..  #
#  @   #
########
"""

# Level 48: Cathedral of Crates (8x8, 5 crates)
LEVEL_DEFS[48] = """
########
# .  . #
#  $$  #
#  .$  #
#  $$  #
# .  . #
#  @   #
########
"""

# Level 49: The Great Hall (8x8, 5 crates)
LEVEL_DEFS[49] = """
########
# .  . #
# $  $ #
#  .$  #
# $  $ #
# .  . #
#  @   #
########
"""

# Level 50: The Final Gauntlet (8x8, 5 crates)
LEVEL_DEFS[50] = """
########
#  ..  #
# $  $ #
#  .$  #
# $  $ #
#  ..  #
#  @   #
########
"""

if __name__ == '__main__':
    print("Testing 50 candidate levels...")
    solved_count = 0
    for lvl in range(1, 51):
        if lvl not in LEVEL_DEFS:
            print(f"Lvl {lvl:02d}: MISSING")
            continue
        w, h, walls, goals, crates, player = parse_sokoban(LEVEL_DEFS[lvl])
        nc = len(crates)
        ng = len(goals)
        if nc != ng:
            print(f"Lvl {lvl:02d}: ERROR crates({nc}) != goals({ng})")
            continue
        res, m, p, path = solve_sokoban(w, h, walls, goals, crates, player, max_states=40000)
        ratio = (p / m) if m else 0
        status = "PASS" if res else "FAIL"
        if res: solved_count += 1
        print(f"Lvl {lvl:02d} | {w}x{h} | {nc} crates | {m:2d} moves | {p:2d} pushes | ratio={ratio:.2f} | {status}")
    print(f"\nResult: {solved_count}/50 levels solved successfully!")


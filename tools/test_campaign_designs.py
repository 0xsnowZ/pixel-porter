#!/usr/bin/env python3
"""
tools/test_campaign_designs.py
Tests candidate warehouse layouts for all 50 levels.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.build_professional_campaign import parse_sokoban, solve_sokoban

CANDIDATES = {}

# Level 1: First Steps (Fixed fixture, 6x6, 1 crate)
CANDIDATES[1] = """
######
#   .#
# $  #
# @  #
#    #
######
"""

# Level 2: Around the Pillar (6x6, 1 crate)
# Player maneuvers around a pillar to push crate into far goal
CANDIDATES[2] = """
######
#   .#
# #  #
# $  #
#  @ #
######
"""

# Level 3: The Winding Hall (6x6, 1 crate)
# L-turn corridor requiring repositioning
CANDIDATES[3] = """
######
#  . #
#  # #
#  $ #
# @  #
######
"""

# Level 4: The Cross Dock (7x7, 1 crate)
# Central island with 4-way corridor
CANDIDATES[4] = """
#######
#  .  #
#  #  #
#  $  #
# @#  #
#     #
#######
"""

# Level 5: Corner Caution (7x7, 1 crate)
# Avoid corner deadlock trap
CANDIDATES[5] = """
#######
#     #
# #.  #
# # $ #
#   # #
# @   #
#######
"""

# Level 6: Dual Cargo (7x7, 2 crates)
# Intro to 2 crates: independent lanes
CANDIDATES[6] = """
#######
# . $ #
#  $  #
#  .  #
#  @  #
#     #
#######
"""

# Level 7: Passing Pocket (7x7, 2 crates)
# Central pillar with two goals and pocket
CANDIDATES[7] = """
#######
#. $ .#
#     #
#  #  #
#  $  #
#@    #
#######
"""

# Level 8: Sequential Bay (7x7, 2 crates)
# Depth lock: back goal must be filled first!
CANDIDATES[8] = """
#######
#  .. #
#  $$ #
#  ## #
#  @  #
#     #
#######
"""

# Level 9: T-Junction Depot (7x7, 2 crates)
CANDIDATES[9] = """
#######
# . . #
#  #  #
#  $  #
# $#  #
#  @  #
#######
"""

# Level 10: Twin Pillars (7x7, 2 crates)
CANDIDATES[10] = """
#######
# . $ #
# # # #
#     #
# # # #
# $ . #
#  @  #
#######
"""

if __name__ == '__main__':
    for lvl in range(1, 11):
        if lvl not in CANDIDATES: continue
        w, h, walls, goals, crates, player = parse_sokoban(CANDIDATES[lvl])
        res, m, p, path = solve_sokoban(w, h, walls, goals, crates, player)
        print(f"Lvl {lvl:02d}: solved={res}, size={w}x{h}, crates={len(crates)}, moves={m}, pushes={p}, ratio={p/m if m else 0:.2f}, path={path}")

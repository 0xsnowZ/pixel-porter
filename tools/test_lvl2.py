import sys
sys.path.append('/home/snowz/godot')
from tools.test_solver import solve

# Let's test Level 2 candidate
lvl2_candidate = [
    '#####    ',
    '#  @#    ',
    '# $$#  ##',
    '# $ ###.#',
    '###    .#',
    ' ## ## .#',
    ' #   ####',
    ' #####   '
]

print('Lvl 2 candidate 1:', solve(lvl2_candidate))

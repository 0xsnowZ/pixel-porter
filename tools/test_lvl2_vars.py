import sys
sys.path.append('/home/snowz/godot')
from tools.inspect_all_jpegs import solve_grid

# Let's test candidate variations for Level 2
# From 2.jpeg:
# Top left: 3x3 pocket with worker and 3 crates
# Lower passage: connects around pillar to right chute with 3 goals
candidates = [
    # Var A:
    [
        '#####    ',
        '#  @#    ',
        '# $$#  ##',
        '# $ ####.#',
        '##     #.#',
        ' # ### #.#',
        ' #   # ###',
        ' #####    '
    ],
    # Var B:
    [
        '#####    ',
        '#  @#    ',
        '# $$#  ##',
        '# $ ####.#',
        '##     #.#',
        ' ###   #.#',
        '   ##### #'
    ],
    # Var C:
    [
        '#####    ',
        '#  @#    ',
        '# $$#  ##',
        '# $ ####.#',
        '##     #.#',
        ' #  ## #.#',
        ' #   # ###',
        ' #####    '
    ],
    # Var D:
    [
        '#####    ',
        '#  @#    ',
        '# $$#  ##',
        '# $ ####.#',
        '##      .#',
        ' #  ##  .#',
        ' #   #####',
        ' #####    '
    ],
    # Var E:
    [
        '#####    ',
        '#  @#    ',
        '# $$#  ##',
        '# $ ####.#',
        '##     #.#',
        ' ##    #.#',
        '  ###### #'
    ],
    # Var F:
    [
        '#####    ',
        '#  @#    ',
        '# $$#  ##',
        '# $ ####.#',
        '##     #.#',
        ' #  ## #.#',
        ' ####  ###',
        '    ####  '
    ],
    # Var G:
    [
        '#####    ',
        '#  @#    ',
        '# $$#  ##',
        '# $ ####.#',
        '##     #.#',
        ' #     #.#',
        ' ####### #'
    ]
]

for i, cand in enumerate(candidates):
    sol, msg = solve_grid(cand)
    print(f'Var {chr(65+i)}: {msg}')


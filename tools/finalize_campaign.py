import json
import os

with open('/tmp/nonsquare_campaign.json') as f:
    campaign = json.load(f)

# Level 1 is the PRD tutorial level
lvl1_lines = [
    '######',
    '#   .#',
    '# $  #',
    '# @  #',
    '#    #',
    '######'
]

# We replace Level 1 with the tutorial, and place the 49 non-square levels at 2..50
# Notice campaign[0] was the Ref 1 Pinwheel (12 moves). It will become Level 2!
final_campaign = [{
    'lvl': 1,
    'name': 'Tutorial Depot',
    'moves': 5,
    'pushes': 3,
    'crates': 1,
    'states': 25,
    'lines': lvl1_lines
}]

for idx, p in enumerate(campaign[:49]):
    p_copy = dict(p)
    p_copy['lvl'] = idx + 2
    final_campaign.append(p_copy)

# Write all 50 levels to /home/snowz/godot/levels/
for p in final_campaign:
    lvl = p['lvl']
    path = f'/home/snowz/godot/levels/level_{lvl:02d}.sok'
    with open(path, 'w') as f:
        f.write('\n'.join(p['lines']) + '\n')

with open('/tmp/final_nonsquare_campaign.json', 'w') as f:
    json.dump(final_campaign, f, indent=2)

moves = [p['moves'] for p in final_campaign]
print('Final 50 Levels OPTIMAL_MOVES:')
for row in range(5):
    print('\t' + ', '.join(str(m) for m in moves[row*10:(row+1)*10]) + ',')


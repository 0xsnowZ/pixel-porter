from PIL import Image
import numpy as np

def analyze_image(path):
    im = Image.open(path).convert('RGB')
    arr = np.array(im)
    h, w, _ = arr.shape
    
    # In each image, find the screen bounding box
    # The screen has a white/cyan border
    # Let's find rows with the horizontal border lines
    # Top border is around y=15..25
    # Bottom border of grid is around 75-85% of h
    # Left border is around x=8..15
    # Right border is around w-15..w-8
    
    # We can detect them by finding the max horizontal line of high cyan/white
    # Or by finding the vertical range of the grid
    # Let's search for the 4 border lines
    top_y = 20
    for y in range(12, 35):
        if np.sum((arr[y, :, 1] > 140) & (arr[y, :, 2] > 180)) > w * 0.4:
            top_y = y
            break
            
    bot_y = int(h * 0.85)
    for y in range(int(h * 0.88), int(h * 0.70), -1):
        if np.sum((arr[y, :, 1] > 140) & (arr[y, :, 2] > 180)) > w * 0.4:
            bot_y = y
            break

    left_x = 10
    for x in range(5, 25):
        if np.sum((arr[:, x, 1] > 140) & (arr[:, x, 2] > 180)) > h * 0.4:
            left_x = x
            break

    right_x = w - 10
    for x in range(w - 5, w - 25, -1):
        if np.sum((arr[:, x, 1] > 140) & (arr[:, x, 2] > 180)) > h * 0.4:
            right_x = x
            break

    dy = (bot_y - top_y) / 9.0
    dx = (right_x - left_x) / 9.0
    
    result = []
    for r in range(9):
        row_chars = []
        for c in range(9):
            cy = int(top_y + (r + 0.5) * dy)
            cx = int(left_x + (c + 0.5) * dx)
            patch = arr[cy-7:cy+7, cx-7:cx+7]
            rgb = patch.mean(axis=(0, 1))
            r_val, g_val, b_val = rgb
            
            # Goal: bright blue
            if b_val > 140 and b_val > r_val + 40:
                row_chars.append('.')
            # Worker: blue hat with skin face (b in 110..180, g in 90..140, r in 20..60)
            elif 20 < r_val < 60 and 90 < g_val < 140 and 110 < b_val < 180:
                row_chars.append('@')
            # Tree: dark background with green
            elif r_val < 55 and b_val < 90 and g_val < 130:
                row_chars.append('_')
            # Brick: reddish brown
            elif r_val > 80 and b_val > 80 and g_val < 130:
                row_chars.append('#')
            # Floor: bright green
            elif g_val > 120 and g_val > r_val + 50 and g_val > b_val + 40:
                row_chars.append(' ')
            # Crate: light brownish/grey
            elif r_val > 65 and g_val > 110 and b_val > 90:
                row_chars.append('$')
            else:
                row_chars.append('?')
        result.append(''.join(row_chars))
    return result

for i in [1, 2, 3, 4, 5]:
    print(f'=== Level {i} ===')
    grid = analyze_image(f'/home/snowz/godot/ref_levels/{i}.jpeg')
    for r, row in enumerate(grid):
        print(f'{r}: {row}')


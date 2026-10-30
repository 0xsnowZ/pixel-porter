from PIL import Image
import numpy as np

def classify_cell(patch):
    # patch is (H, W, 3)
    rgb = patch.mean(axis=(0, 1))
    std = patch.std(axis=(0, 1))
    r, g, b = rgb
    
    # Blue goal: dominant blue, B > 140, B > R + 40
    if b > 140 and b > r + 40 and b > g - 20:
        return '.'
        
    # Player: blue hat / green body / face (r < 60, 70 < g < 150, 100 < b < 190)
    # But distinguish from goal: goal has much higher B, less green
    # Player has face/hat: std is relatively high, b in 100..170, g in 80..140
    # Let's check center of player
    
    # Tree (exterior void): dark background with green pine (R < 55, B < 90, G in 50..130)
    if r < 60 and b < 95 and g < 140:
        return ' ' # void / tree
        
    # Wall (brick): reddish-purple/brown (R > 85, B > 95, G < 125, |R - B| < 50)
    if r > 80 and b > 85 and g < 130:
        return '#'
        
    # Floor: bright green (G > 120, G > R + 60, G > B + 60)
    if g > 120 and g > r + 50 and g > b + 40:
        return ' ' # green floor inside
        
    # Crate: light box with X (R > 75, G > 120, B > 100)
    if r > 65 and g > 110 and b > 90:
        return '$'
        
    return '?'

def get_playfield_bounds(arr):
    h, w, _ = arr.shape
    ymin = 20
    for y in range(10, 40):
        row = arr[y, :, :]
        if np.sum((row[:, 1] > 140) & (row[:, 2] > 180)) > w * 0.4:
            ymin = y
            break
            
    # Bottom line of playfield: look for the bottom border line of the grid
    # Often around y = 200..320
    # Let's find it by scanning backwards from h - 30
    ymax = int(h * 0.88)
    for y in range(h - 30, int(h * 0.6), -1):
        row = arr[y, :, :]
        if np.sum((row[:, 1] > 140) & (row[:, 2] > 180)) > w * 0.3:
            ymax = y
            break

    xmin = 10
    for x in range(5, 30):
        col = arr[:, x, :]
        if np.sum((col[:, 1] > 140) & (col[:, 2] > 180)) > h * 0.4:
            xmin = x
            break

    xmax = w - 10
    for x in range(w - 10, w - 35, -1):
        col = arr[:, x, :]
        if np.sum((col[:, 1] > 140) & (col[:, 2] > 180)) > h * 0.4:
            xmax = x
            break

    return xmin, xmax, ymin, ymax

for lvl in range(1, 16):
    im = Image.open(f'/home/snowz/godot/ref_levels/{lvl}.jpeg').convert('RGB')
    arr = np.array(im)
    xmin, xmax, ymin, ymax = get_playfield_bounds(arr)
    dy = (ymax - ymin) / 9.0
    dx = (xmax - xmin) / 9.0
    
    print(f'=== LEVEL {lvl} (dx={dx:.1f}, dy={dy:.1f}) ===')
    grid = []
    for r in range(9):
        line = ''
        for c in range(9):
            cy = int(ymin + (r + 0.5) * dy)
            cx = int(xmin + (c + 0.5) * dx)
            patch = arr[cy-6:cy+6, cx-6:cx+6]
            ch = classify_cell(patch)
            line += ch
        print(f'{r}: {line}')

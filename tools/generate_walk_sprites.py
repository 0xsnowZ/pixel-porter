#!/usr/bin/env python3
"""
Pixel Porter - Walking Sprite Animation Generator
Generates 2-frame walking cycles for all 4 cardinal directions:
- player_down_walk1.png, player_down_walk2.png
- player_up_walk1.png, player_up_walk2.png
- player_left_walk1.png, player_left_walk2.png
- player_right_walk1.png, player_right_walk2.png
"""

import os
from PIL import Image, ImageDraw

OUTPUT_DIR = "/home/snowz/godot/assets"
SIZE = 128
cx = SIZE // 2
head_y = 36
head_r = 18
cap_y = head_y - 10


def draw_cap_down(d, cy_offset=0):
    y = cap_y + cy_offset
    d.pieslice([cx - 20, y - 16, cx + 20, y + 16], 180, 360, fill=(225, 36, 32, 255), outline=(140, 18, 15, 255), width=2)
    d.ellipse([cx - 3, y - 18, cx + 3, y - 12], fill=(160, 20, 16, 255))
    d.rectangle([cx - 22, y - 2, cx + 22, y + 6], fill=(175, 24, 20, 255), outline=(120, 15, 12, 255))
    d.line([(cx - 20, y - 1), (cx + 20, y - 1)], fill=(245, 80, 75, 255), width=1)


def draw_face_down(d, cy_offset=0):
    hy = head_y + cy_offset
    d.ellipse([cx - head_r, hy - head_r, cx + head_r, hy + head_r],
              fill=(252, 205, 168, 255), outline=(195, 135, 95, 255), width=2)
    d.ellipse([cx - 15, hy + 2, cx - 9, hy + 8], fill=(245, 165, 145, 160))
    d.ellipse([cx + 9, hy + 2, cx + 15, hy + 8], fill=(245, 165, 145, 160))
    d.ellipse([cx - 10, hy - 4, cx - 3, hy + 4], fill=(25, 25, 30, 255))
    d.ellipse([cx + 3, hy - 4, cx + 10, hy + 4], fill=(25, 25, 30, 255))
    d.point((cx - 7, hy - 2), fill=(255, 255, 255, 255))
    d.point((cx + 6, hy - 2), fill=(255, 255, 255, 255))
    d.arc([cx - 6, hy + 4, cx + 6, hy + 11], 0, 180, fill=(160, 80, 50, 255), width=2)


def generate_down_walk():
    for frame in [1, 2]:
        img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)

        # Shadow
        d.ellipse([cx - 32, 100, cx + 32, 120], fill=(0, 0, 0, 95))

        bob = 2 if frame == 1 else 1

        # Legs & Boots stride offset
        # Frame 1: Left leg forward (down), Right leg back (up)
        # Frame 2: Right leg forward (down), Left leg back (up)
        l_offset = 4 if frame == 1 else -4
        r_offset = -4 if frame == 1 else 4

        # Boots
        # Left boot
        d.rectangle([cx - 25, 94 + l_offset, cx - 7, 108 + l_offset], fill=(70, 42, 22, 255), outline=(35, 18, 8, 255))
        d.rectangle([cx - 25, 106 + l_offset, cx - 7, 110 + l_offset], fill=(45, 25, 12, 255))
        # Right boot
        d.rectangle([cx + 7, 94 + r_offset, cx + 25, 108 + r_offset], fill=(70, 42, 22, 255), outline=(35, 18, 8, 255))
        d.rectangle([cx + 7, 106 + r_offset, cx + 25, 110 + r_offset], fill=(45, 25, 12, 255))

        # Overalls legs
        d.rectangle([cx - 23, 72 + bob, cx - 6, 96 + l_offset], fill=(38, 75, 142, 255), outline=(20, 42, 85, 255))
        d.rectangle([cx + 6, 72 + bob, cx + 23, 96 + r_offset], fill=(38, 75, 142, 255), outline=(20, 42, 85, 255))

        # Overalls Torso
        d.rectangle([cx - 22, 48 + bob, cx + 22, 76 + bob], fill=(46, 88, 165, 255), outline=(20, 42, 85, 255))
        # Red worker shirt
        d.rectangle([cx - 28, 48 + bob, cx - 22, 68 + bob], fill=(215, 42, 38, 255), outline=(130, 20, 18, 255))
        d.rectangle([cx + 22, 48 + bob, cx + 28, 68 + bob], fill=(215, 42, 38, 255), outline=(130, 20, 18, 255))

        # Suspenders
        d.line([(cx - 14, 48 + bob), (cx - 14, 62 + bob)], fill=(28, 58, 115, 255), width=6)
        d.line([(cx + 14, 48 + bob), (cx + 14, 62 + bob)], fill=(28, 58, 115, 255), width=6)
        d.rectangle([cx - 17, 60 + bob, cx - 11, 65 + bob], fill=(235, 185, 55, 255))
        d.rectangle([cx + 11, 60 + bob, cx + 17, 65 + bob], fill=(235, 185, 55, 255))
        d.rectangle([cx - 8, 62 + bob, cx + 8, 72 + bob], fill=(38, 75, 142, 255), outline=(25, 50, 98, 255))

        # Gloves / Arms swinging with stride
        l_arm_swing = -3 if frame == 1 else 4
        r_arm_swing = 4 if frame == 1 else -3
        d.ellipse([cx - 32, 64 + bob + l_arm_swing, cx - 20, 78 + bob + l_arm_swing], fill=(240, 240, 245, 255), outline=(150, 155, 165, 255))
        d.ellipse([cx + 20, 64 + bob + r_arm_swing, cx + 32, 78 + bob + r_arm_swing], fill=(240, 240, 245, 255), outline=(150, 155, 165, 255))

        # Head & Cap
        draw_face_down(d, bob)
        draw_cap_down(d, bob)

        out_path = os.path.join(OUTPUT_DIR, f"player_down_walk{frame}.png")
        img.save(out_path)
        print(f"Saved {out_path}")


def generate_up_walk():
    for frame in [1, 2]:
        img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        u = ImageDraw.Draw(img)

        # Shadow
        u.ellipse([cx - 32, 100, cx + 32, 120], fill=(0, 0, 0, 95))
        bob = 2 if frame == 1 else 1

        l_offset = -4 if frame == 1 else 4
        r_offset = 4 if frame == 1 else -4

        # Boots (back view)
        u.rectangle([cx - 25, 94 + l_offset, cx - 7, 108 + l_offset], fill=(60, 36, 18, 255), outline=(35, 18, 8, 255))
        u.rectangle([cx - 25, 106 + l_offset, cx - 7, 110 + l_offset], fill=(45, 25, 12, 255))
        u.rectangle([cx + 7, 94 + r_offset, cx + 25, 108 + r_offset], fill=(60, 36, 18, 255), outline=(35, 18, 8, 255))
        u.rectangle([cx + 7, 106 + r_offset, cx + 25, 110 + r_offset], fill=(45, 25, 12, 255))

        # Overalls legs
        u.rectangle([cx - 23, 72 + bob, cx - 6, 96 + l_offset], fill=(32, 65, 125, 255), outline=(20, 42, 85, 255))
        u.rectangle([cx + 6, 72 + bob, cx + 23, 96 + r_offset], fill=(32, 65, 125, 255), outline=(20, 42, 85, 255))

        # Overalls back
        u.rectangle([cx - 22, 48 + bob, cx + 22, 76 + bob], fill=(40, 80, 150, 255), outline=(20, 42, 85, 255))
        u.rectangle([cx - 28, 48 + bob, cx - 22, 68 + bob], fill=(195, 36, 32, 255), outline=(130, 20, 18, 255))
        u.rectangle([cx + 22, 48 + bob, cx + 28, 68 + bob], fill=(195, 36, 32, 255), outline=(130, 20, 18, 255))

        u.line([(cx - 14, 48 + bob), (cx + 14, 76 + bob)], fill=(25, 52, 105, 255), width=6)
        u.line([(cx + 14, 48 + bob), (cx - 14, 76 + bob)], fill=(25, 52, 105, 255), width=6)

        # Head (back view / dark hair)
        hy = head_y + bob
        u.ellipse([cx - head_r, hy - head_r, cx + head_r, hy + head_r], fill=(55, 35, 25, 255))

        # Red cap back
        cy = cap_y + bob
        u.pieslice([cx - 20, cy - 18, cx + 20, cy + 14], 180, 360, fill=(225, 36, 32, 255), outline=(140, 18, 15, 255), width=2)
        u.arc([cx - 8, cy - 2, cx + 8, cy + 8], 0, 180, fill=(252, 205, 168, 255), width=4)
        u.line([(cx - 8, cy + 4), (cx + 8, cy + 4)], fill=(150, 20, 16, 255), width=2)

        out_path = os.path.join(OUTPUT_DIR, f"player_up_walk{frame}.png")
        img.save(out_path)
        print(f"Saved {out_path}")


def generate_side_walk():
    for frame in [1, 2]:
        img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        l = ImageDraw.Draw(img)

        # Shadow
        l.ellipse([cx - 32, 100, cx + 26, 120], fill=(0, 0, 0, 95))
        bob = 2 if frame == 1 else 1

        # Walk 1: Front foot reaches forward left, rear foot back
        # Walk 2: Rear foot steps through, front foot planted
        if frame == 1:
            # Front boot extended left
            l.rectangle([cx - 28, 96, cx - 10, 110], fill=(70, 42, 22, 255), outline=(35, 18, 8, 255))
            l.rectangle([cx - 30, 108, cx - 10, 112], fill=(45, 25, 12, 255))
            # Rear boot back
            l.rectangle([cx + 6, 90, cx + 20, 104], fill=(55, 32, 16, 255), outline=(35, 18, 8, 255))
        else:
            # Front boot planted
            l.rectangle([cx - 18, 94, cx - 2, 108], fill=(70, 42, 22, 255), outline=(35, 18, 8, 255))
            l.rectangle([cx - 20, 106, cx - 2, 110], fill=(45, 25, 12, 255))
            # Rear boot stepping through
            l.rectangle([cx - 6, 98, cx + 10, 111], fill=(55, 32, 16, 255), outline=(35, 18, 8, 255))
            l.rectangle([cx - 8, 109, cx + 10, 113], fill=(45, 25, 12, 255))

        # Legs & Overalls
        l.rectangle([cx - 20, 70 + bob, cx + 6, 96 + bob], fill=(38, 75, 142, 255), outline=(20, 42, 85, 255))
        l.rectangle([cx - 14, 48 + bob, cx + 16, 76 + bob], fill=(46, 88, 165, 255), outline=(20, 42, 85, 255))

        d_shirt_x = cx + 8
        l.rectangle([d_shirt_x, 48 + bob, d_shirt_x + 8, 68 + bob], fill=(215, 42, 38, 255), outline=(130, 20, 18, 255))

        # Pushing/Walking Arm with natural swinging locomotion
        arm_reach = -24 if frame == 1 else -18
        l.line([(cx + 4, 56 + bob), (cx + arm_reach, 60 + bob)], fill=(215, 42, 38, 255), width=10)
        l.ellipse([cx + arm_reach - 10, 52 + bob, cx + arm_reach + 4, 68 + bob], fill=(240, 240, 245, 255), outline=(150, 155, 165, 255))

        # Head (profile left)
        hy = head_y + bob
        l.ellipse([cx - 16, hy - 16, cx + 16, hy + 16], fill=(252, 205, 168, 255), outline=(195, 135, 95, 255), width=2)
        l.polygon([(cx - 14, hy), (cx - 20, hy + 3), (cx - 14, hy + 6)], fill=(252, 205, 168, 255))
        l.ellipse([cx - 12, hy - 4, cx - 6, hy + 4], fill=(25, 25, 30, 255))
        l.point((cx - 10, hy - 2), fill=(255, 255, 255, 255))

        # Red Cap with visor pointing LEFT
        cy = cap_y + bob
        l.pieslice([cx - 18, cy - 16, cx + 18, cy + 16], 180, 360, fill=(225, 36, 32, 255), outline=(140, 18, 15, 255), width=2)
        l.polygon([(cx - 16, cy + 2), (cx - 32, cy + 6), (cx - 14, cy + 10)], fill=(175, 24, 20, 255), outline=(120, 15, 12, 255))

        out_path_l = os.path.join(OUTPUT_DIR, f"player_left_walk{frame}.png")
        img.save(out_path_l)
        print(f"Saved {out_path_l}")

        # Mirror for RIGHT
        img_r = img.transpose(Image.FLIP_LEFT_RIGHT)
        out_path_r = os.path.join(OUTPUT_DIR, f"player_right_walk{frame}.png")
        img_r.save(out_path_r)
        print(f"Saved {out_path_r}")


if __name__ == "__main__":
    generate_down_walk()
    generate_up_walk()
    generate_side_walk()
    print("Done generating walking cycle sprites.")

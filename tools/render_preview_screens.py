#!/usr/bin/env python3
"""
Pixel Porter - UI & Gameplay Preview Visualizer
Generates accurate 540x960 visual render previews of:
- Main Menu
- Gameplay Board (Level 1)
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ARTIFACT_DIR = "/home/snowz/.gemini/antigravity-ide/brain/9a93013c-7615-47d7-ae14-3f8a6be1d265"
ASSETS_DIR = "/home/snowz/godot/assets"
W, H = 540, 960

def get_font(size):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except:
        return ImageFont.load_default()

def get_regular_font(size):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def draw_styled_button(draw, rect, text, is_primary=False, is_success=False, font=None):
    x0, y0, x1, y1 = rect
    r = 10
    if is_primary:
        bg = (218, 138, 30)
        border_top = (255, 220, 115)
        border_bot = (110, 55, 10)
        text_col = (255, 255, 255)
    elif is_success:
        bg = (46, 148, 82)
        border_top = (115, 230, 148)
        border_bot = (20, 82, 35)
        text_col = (255, 255, 255)
    else:
        bg = (33, 43, 61)
        border_top = (184, 138, 51)
        border_bot = (75, 55, 18)
        text_col = (240, 244, 250)

    # Button shadow
    draw.rounded_rectangle([x0 + 1, y0 + 3, x1 + 1, y1 + 3], radius=r, fill=(0, 0, 0, 90))
    # Button body
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=bg)
    # 3D bevel borders
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, outline=border_top, width=2)
    # Thicker bottom bevel
    draw.line([(x0 + r, y1), (x1 - r, y1)], fill=border_bot, width=4)

    # Text centered
    if font:
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = (x0 + x1 - tw) // 2
        ty = (y0 + y1 - th) // 2 - 2
        # Text shadow
        draw.text((tx, ty + 1), text, font=font, fill=(0, 0, 0, 220))
        draw.text((tx, ty), text, font=font, fill=text_col)

def render_main_menu_preview():
    # Load warehouse background
    bg_path = os.path.join(ASSETS_DIR, "warehouse_bg.jpg")
    bg = Image.open(bg_path).convert("RGBA").resize((W, H))

    # Dim vignette overlay
    overlay = Image.new("RGBA", (W, H), (15, 20, 31, 175))
    menu_img = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(menu_img)

    # Logo
    logo_path = os.path.join(ASSETS_DIR, "logo.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA").resize((200, 200))
        # Logo subtle backlight glow
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(glow)
        g_draw.ellipse([(W//2 - 120, 70), (W//2 + 120, 290)], fill=(255, 195, 45, 60))
        glow = glow.filter(ImageFilter.GaussianBlur(25))
        menu_img = Image.alpha_composite(menu_img, glow)
        menu_img.paste(logo, (W//2 - 100, 80), logo)

    draw = ImageDraw.Draw(menu_img)
    f_sub = get_font(13)
    f_btn = get_font(16)
    f_btn_pri = get_font(18)
    f_foot = get_regular_font(12)

    # Subtitle
    sub_text = "★ A CLASSIC SOKOBAN PUZZLE ★"
    bbox = f_sub.getbbox(sub_text)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw)//2, 295), sub_text, font=f_sub, fill=(245, 209, 89))

    # Arcade Console Card
    card_x0, card_y0 = (W - 320)//2, 335
    card_x1, card_y1 = card_x0 + 320, 875
    # Card shadow
    draw.rounded_rectangle([card_x0 + 4, card_y0 + 6, card_x1 + 4, card_y1 + 6], radius=16, fill=(0, 0, 0, 160))
    # Card slate body
    draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=16, fill=(23, 31, 43, 240), outline=(173, 128, 46), width=2)

    # 4 Corner decorative rivets on card
    for rx, ry in [(card_x0 + 10, card_y0 + 10), (card_x1 - 10, card_y0 + 10), (card_x0 + 10, card_y1 - 10), (card_x1 - 10, card_y1 - 10)]:
        draw.ellipse([rx - 3, ry - 3, rx + 3, ry + 3], fill=(215, 165, 55), outline=(50, 35, 15))

    # Buttons
    btn_w, btn_h = 280, 52
    bx0 = (W - btn_w)//2
    bx1 = bx0 + btn_w

    buttons_data = [
        ("PLAY", True, f_btn_pri, 52),
        ("LEVEL SELECT", False, f_btn, 50),
        ("SOUND: ON", False, f_btn, 48),
        ("HAPTICS: ON", False, f_btn, 48),
        ("LANGUAGE: English", False, f_btn, 48),
        ("CREDITS", False, f_btn, 44),
    ]

    curr_y = card_y0 + 24
    for b_title, is_pri, fnt, bh in buttons_data:
        draw_styled_button(draw, (bx0, curr_y, bx1, curr_y + bh), b_title, is_primary=is_pri, font=fnt)
        curr_y += bh + 14

    # Footer
    foot_text = "Pixel Porter v1.0 • Android"
    f_bbox = f_foot.getbbox(foot_text)
    draw.text(((W - (f_bbox[2] - f_bbox[0]))//2, 915), foot_text, font=f_foot, fill=(140, 155, 180))

    out_path = os.path.join(ARTIFACT_DIR, "preview_main_menu.png")
    menu_img.save(out_path)
    print("Saved preview_main_menu.png")


def render_gameplay_preview():
    # Load warehouse background dimmed
    bg_path = os.path.join(ASSETS_DIR, "warehouse_bg.jpg")
    bg = Image.open(bg_path).convert("RGBA").resize((W, H))
    overlay = Image.new("RGBA", (W, H), (15, 20, 31, 190))
    game_img = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(game_img)

    f_top = get_font(18)
    f_stats = get_regular_font(15)
    f_btn = get_font(16)

    # Top Bar
    draw.rectangle([0, 0, W, 68], fill=(20, 28, 41, 245), outline=(184, 138, 51), width=1)
    draw.line([(0, 68), (W, 68)], fill=(184, 138, 51), width=2)
    # Menu btn
    draw_styled_button(draw, (16, 12, 62, 54), "⌂", font=f_top)
    # Level label
    draw.text((80, 24), "LEVEL 1 / 50", font=f_top, fill=(250, 217, 72))
    # Stats
    draw.text((W - 200, 25), "MOVES: 0  |  PUSHES: 0", font=f_stats, fill=(225, 235, 250))

    # Bottom Bar
    draw.rectangle([0, H - 76, W, H], fill=(20, 28, 41, 245))
    draw.line([(0, H - 76), (W, H - 76)], fill=(184, 138, 51), width=2)
    draw_styled_button(draw, (16, H - 64, 96, H - 16), "< Prev", font=f_btn)
    draw_styled_button(draw, (108, H - 64, 216, H - 16), "Undo ↶", font=f_btn)
    draw_styled_button(draw, (228, H - 64, 428, H - 16), "Restart ↺", is_primary=True, font=f_btn)
    draw_styled_button(draw, (440, H - 64, 524, H - 16), "Next >", is_success=True, font=f_btn)

    # Game Board (5x5 grid from Level 1)
    # Level 1 map:
    # #####
    # #   #
    # # $ #
    # #.@ #
    # #####
    tile_sz = 84
    grid_w, grid_h = 5, 5
    board_px_w, board_px_h = grid_w * tile_sz, grid_h * tile_sz
    gx0 = (W - board_px_w) // 2
    gy0 = (H - board_px_h) // 2

    # Board Loading Bay Frame
    frame_m = 12
    fx0, fy0 = gx0 - frame_m, gy0 - frame_m
    fx1, fy1 = gx0 + board_px_w + frame_m, gy0 + board_px_h + frame_m
    # Drop shadow
    draw.rectangle([fx0 + 8, fy0 + 10, fx1 + 8, fy1 + 10], fill=(0, 0, 0, 160))
    # Frame slate
    draw.rectangle([fx0, fy0, fx1, fy1], fill=(30, 37, 50), outline=(198, 153, 56), width=3)
    # Bolts
    for bx, by in [(fx0 + 6, fy0 + 6), (fx1 - 6, fy0 + 6), (fx0 + 6, fy1 - 6), (fx1 - 6, fy1 - 6)]:
        draw.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(235, 185, 70), outline=(45, 30, 10))

    # Load Tile Textures
    tex_wall = Image.open(os.path.join(ASSETS_DIR, "wall_brick.png")).convert("RGBA").resize((tile_sz, tile_sz))
    tex_f1 = Image.open(os.path.join(ASSETS_DIR, "floor_tile_1.png")).convert("RGBA").resize((tile_sz, tile_sz))
    tex_f2 = Image.open(os.path.join(ASSETS_DIR, "floor_tile_2.png")).convert("RGBA").resize((tile_sz, tile_sz))
    tex_goal = Image.open(os.path.join(ASSETS_DIR, "goal_pad.png")).convert("RGBA").resize((tile_sz, tile_sz))
    tex_crate = Image.open(os.path.join(ASSETS_DIR, "crate_normal.png")).convert("RGBA").resize((tile_sz, tile_sz))
    tex_player = Image.open(os.path.join(ASSETS_DIR, "player_down.png")).convert("RGBA").resize((tile_sz, tile_sz))

    level_1_grid = [
        "#####",
        "#   #",
        "# $ #",
        "#.@ #",
        "#####"
    ]

    for y in range(grid_h):
        for x in range(grid_w):
            ch = level_1_grid[y][x]
            tx = gx0 + x * tile_sz
            ty = gy0 + y * tile_sz
            if ch == '#':
                game_img.paste(tex_wall, (tx, ty), tex_wall)
            else:
                f_tex = tex_f1 if (x + y) % 2 == 0 else tex_f2
                game_img.paste(f_tex, (tx, ty), f_tex)
                # Overhang shadow if top is wall
                if y > 0 and level_1_grid[y - 1][x] == '#':
                    s_overlay = Image.new("RGBA", (tile_sz, int(tile_sz * 0.22)), (0, 0, 0, 110))
                    game_img.paste(s_overlay, (tx, ty), s_overlay)

                if ch == '.':
                    game_img.paste(tex_goal, (tx, ty), tex_goal)
                elif ch == '$':
                    game_img.paste(tex_crate, (tx, ty), tex_crate)
                elif ch == '@':
                    game_img.paste(tex_player, (tx, ty), tex_player)

    out_path = os.path.join(ARTIFACT_DIR, "preview_gameplay.png")
    game_img.save(out_path)
    print("Saved preview_gameplay.png")

if __name__ == "__main__":
    render_main_menu_preview()
    render_gameplay_preview()

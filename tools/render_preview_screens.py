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
        logo = Image.open(logo_path).convert("RGBA").resize((220, 226))
        menu_img.paste(logo, (W//2 - 110, 65), logo)

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
                    # Ground contact shadow (positioned directly under boot soles)
                    s_layer = Image.new("RGBA", (tile_sz, tile_sz), (0, 0, 0, 0))
                    s_draw = ImageDraw.Draw(s_layer)
                    rad = tile_sz / 2.0
                    sc_x = rad
                    sc_y = tile_sz * 0.94
                    # Outer soft ambient shadow
                    rx_o, ry_o = rad * 0.54, rad * 0.18
                    s_draw.ellipse([sc_x - rx_o, sc_y - ry_o, sc_x + rx_o, sc_y + ry_o], fill=(0, 0, 0, 56))
                    # Inner core contact shadow
                    rx_i, ry_i = rad * 0.40, rad * 0.11
                    s_draw.ellipse([sc_x - rx_i, sc_y - ry_i, sc_x + rx_i, sc_y + ry_i], fill=(0, 0, 0, 82))
                    game_img.alpha_composite(s_layer, (tx, ty))
                    game_img.alpha_composite(tex_player, (tx, ty))

    out_path = os.path.join(ARTIFACT_DIR, "preview_gameplay.png")
    game_img.save(out_path)
    print("Saved preview_gameplay.png")

    # Also render close-up comparison of fixed shadow facing LEFT vs DOWN on warehouse floor
    preview_shadow_comparison(tile_sz)


def preview_shadow_comparison(tile_sz):
    # Close-up comparison of fixed shadow on warehouse floor (DOWN vs LEFT)
    tex_f1 = Image.open(os.path.join(ASSETS_DIR, "floor_tile_1.png")).convert("RGBA").resize((tile_sz, tile_sz))
    tex_down = Image.open(os.path.join(ASSETS_DIR, "player_down.png")).convert("RGBA").resize((tile_sz, tile_sz))
    tex_left = Image.open(os.path.join(ASSETS_DIR, "player_left.png")).convert("RGBA").resize((tile_sz, tile_sz))
    
    pad = 20
    comp_w = tile_sz * 2 + pad * 3
    comp_h = tile_sz + pad * 2 + 30
    comp_img = Image.new("RGBA", (comp_w, comp_h), (24, 28, 38, 255))
    d = ImageDraw.Draw(comp_img)

    for idx, (p_tex, label, is_left) in enumerate([(tex_down, "Facing DOWN", False), (tex_left, "Facing LEFT", True)]):
        bx = pad + idx * (tile_sz + pad)
        by = pad + 24
        # Floor
        comp_img.alpha_composite(tex_f1, (bx, by))
        # Shadow
        s_layer = Image.new("RGBA", (tile_sz, tile_sz), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(s_layer)
        rad = tile_sz / 2.0
        sc_x = rad + (-rad * 0.04 if is_left else 0.0)
        sc_y = tile_sz * 0.94
        rx_o, ry_o = rad * 0.54, rad * 0.18
        s_draw.ellipse([sc_x - rx_o, sc_y - ry_o, sc_x + rx_o, sc_y + ry_o], fill=(0, 0, 0, 56))
        rx_i, ry_i = rad * 0.40, rad * 0.11
        s_draw.ellipse([sc_x - rx_i, sc_y - ry_i, sc_x + rx_i, sc_y + ry_i], fill=(0, 0, 0, 82))
        comp_img.alpha_composite(s_layer, (bx, by))
        # Character
        comp_img.alpha_composite(p_tex, (bx, by))
        # Label
        d.text((bx + tile_sz//2, pad), label, fill=(220, 230, 245, 255), anchor="mt")

    out_comp = os.path.join(ARTIFACT_DIR, "preview_player_shadow.png")
    comp_img.save(out_comp)
    print("Saved preview_player_shadow.png")


def render_win_modal_preview():
    # Base is gameplay preview
    gp_path = os.path.join(ARTIFACT_DIR, "preview_gameplay.png")
    if os.path.exists(gp_path):
        base = Image.open(gp_path).convert("RGBA")
    else:
        bg_path = os.path.join(ASSETS_DIR, "warehouse_bg.jpg")
        base = Image.open(bg_path).convert("RGBA").resize((W, H))

    # Dim overlay with frosted glass blur backdrop
    blurred_base = base.filter(ImageFilter.GaussianBlur(12))
    dim = Image.new("RGBA", (W, H), (8, 12, 18, 175))
    win_img = Image.alpha_composite(blurred_base, dim)
    draw = ImageDraw.Draw(win_img)

    # Confetti celebration particles
    import random
    rng = random.Random(42)
    confetti_colors = [
        (255, 215, 0, 220),   # Gold
        (50, 205, 50, 220),    # Lime green
        (255, 69, 0, 220),     # Orange red
        (30, 144, 255, 220),   # Dodger blue
        (255, 105, 180, 220),  # Hot pink
        (138, 43, 226, 220),   # Purple
    ]
    for _ in range(45):
        cx = rng.randint(40, W - 40)
        cy = rng.randint(120, H - 150)
        cw = rng.randint(8, 16)
        ch = rng.randint(5, 10)
        col = rng.choice(confetti_colors)
        draw.rectangle([cx, cy, cx + cw, cy + ch], fill=col)

    # Main victory card modal: [55, 210, 485, 725]
    mx0, my0, mx1, my1 = 55, 210, 485, 725
    r = 16
    # Modal drop shadow
    draw.rounded_rectangle([mx0 + 2, my0 + 6, mx1 + 2, my1 + 6], radius=r, fill=(0, 0, 0, 160))
    # Modal background
    draw.rounded_rectangle([mx0, my0, mx1, my1], radius=r, fill=(20, 26, 38, 250))
    # Modal gold border
    draw.rounded_rectangle([mx0, my0, mx1, my1], radius=r, outline=(235, 192, 71), width=3)

    # Arched Header Banner: [85, 188, 455, 254]
    bx0, by0, bx1, by1 = 85, 188, 455, 254
    draw.rounded_rectangle([bx0 + 2, by0 + 4, bx1 + 2, by1 + 4], radius=12, fill=(0, 0, 0, 120))
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=12, fill=(217, 46, 46))
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=12, outline=(255, 217, 89), width=3)
    f_banner = get_font(21)
    b_text = "LEVEL COMPLETED!"
    bbox = f_banner.getbbox(b_text)
    btw = bbox[2] - bbox[0]
    draw.text(((W - btw)//2, by0 + 17), b_text, font=f_banner, fill=(255, 245, 220))

    # 3 Golden Stars (Enlarged Hero Element)
    f_star_sm = get_font(68)
    f_star_lg = get_font(88)

    b_sm = f_star_sm.getbbox("★")
    w_sm = b_sm[2] - b_sm[0]
    b_lg = f_star_lg.getbbox("★")
    w_lg = b_lg[2] - b_lg[0]

    x2 = (W - w_lg) // 2
    x1 = 170 - w_sm // 2
    x3 = 370 - w_sm // 2
    y_lg = 240
    y_sm = 258

    # Star 1 (Left)
    draw.text((x1 + 3, y_sm + 4), "★", font=f_star_sm, fill=(0, 0, 0, 190))
    for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        draw.text((x1 + ox, y_sm + oy), "★", font=f_star_sm, fill=(110, 65, 10))
    draw.text((x1, y_sm), "★", font=f_star_sm, fill=(255, 218, 56))

    # Star 2 (Center, enlarged & elevated)
    draw.text((x2 + 4, y_lg + 5), "★", font=f_star_lg, fill=(0, 0, 0, 210))
    for ox, oy in [(-3, 0), (3, 0), (0, -3), (0, 3)]:
        draw.text((x2 + ox, y_lg + oy), "★", font=f_star_lg, fill=(110, 65, 10))
    draw.text((x2, y_lg), "★", font=f_star_lg, fill=(255, 228, 68))

    # Star 3 (Right)
    draw.text((x3 + 3, y_sm + 4), "★", font=f_star_sm, fill=(0, 0, 0, 190))
    for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        draw.text((x3 + ox, y_sm + oy), "★", font=f_star_sm, fill=(110, 65, 10))
    draw.text((x3, y_sm), "★", font=f_star_sm, fill=(255, 218, 56))

    # Wooden Placard for Level Number: [175, 342, 365, 396]
    px0, py0, px1, py1 = 175, 342, 365, 396
    draw.rounded_rectangle([px0, py0, px1, py1], radius=8, fill=(64, 41, 26))
    draw.rounded_rectangle([px0, py0, px1, py1], radius=8, outline=(217, 158, 64), width=2)
    f_placard = get_font(20)
    p_text = "LEVEL 4"
    bbox = f_placard.getbbox(p_text)
    ptw = bbox[2] - bbox[0]
    draw.text(((W - ptw)//2, py0 + 13), p_text, font=f_placard, fill=(255, 230, 166))

    # 3 Stat Cards: MOVES, TIME, PUSHES
    f_stat_title = get_font(10)
    f_stat_val = get_font(18)
    card_configs = [
        (80, "👟", "MOVES", "4", (50, 140, 230)),
        (215, "⏱", "TIME", "00:08", (230, 65, 65)),
        (350, "📦", "PUSHES", "2", (235, 140, 45)),
    ]
    cw, ch = 110, 88
    cy0 = 420
    for cx0, icon, title, val, accent in card_configs:
        cx1 = cx0 + cw
        cy1 = cy0 + ch
        # Card background
        draw.rounded_rectangle([cx0, cy0, cx1, cy1], radius=10, fill=(16, 21, 31, 230))
        draw.rounded_rectangle([cx0, cy0, cx1, cy1], radius=10, outline=(82, 97, 122, 180), width=2)
        # Accent top bar
        draw.line([(cx0 + 8, cy0 + 3), (cx1 - 8, cy0 + 3)], fill=accent, width=3)

        # Title
        t_box = f_stat_title.getbbox(title)
        ttw = t_box[2] - t_box[0]
        draw.text(((cx0 + cx1 - ttw)//2, cy0 + 16), title, font=f_stat_title, fill=(150, 170, 195))

        # Value
        v_box = f_stat_val.getbbox(val)
        vtw = v_box[2] - v_box[0]
        draw.text(((cx0 + cx1 - vtw)//2, cy0 + 44), val, font=f_stat_val, fill=(245, 248, 255))

    # Target Hint
    f_hint = get_regular_font(13)
    hint_text = "★ 3★ Target: ≤ 7 moves ★"
    h_box = f_hint.getbbox(hint_text)
    htw = h_box[2] - h_box[0]
    draw.text(((W - htw)//2, 532), hint_text, font=f_hint, fill=(215, 230, 248))

    # 3 Chunky Action Buttons: Red Menu (⌂), Green Next (▶), Blue Retry (↺)
    f_btn_icon = get_font(18)

    # Red Menu Button
    draw_styled_button_custom(draw, (80, 615, 185, 680), "⌂ MENU", (210, 56, 56), (255, 140, 140), (120, 25, 25), f_btn_icon)
    # Green Next Button (larger in center)
    draw_styled_button_custom(draw, (200, 615, 340, 680), "▶ NEXT", (46, 148, 82), (115, 230, 148), (20, 82, 35), f_btn_icon)
    # Blue Retry Button
    draw_styled_button_custom(draw, (355, 615, 460, 680), "↺ RETRY", (46, 132, 224), (160, 215, 255), (20, 75, 140), f_btn_icon)

    out_path = os.path.join(ARTIFACT_DIR, "preview_win_modal.png")
    win_img.save(out_path)
    print("Saved preview_win_modal.png")


def draw_styled_button_custom(draw, rect, text, bg, border_top, border_bot, font):
    x0, y0, x1, y1 = rect
    r = 10
    draw.rounded_rectangle([x0 + 1, y0 + 3, x1 + 1, y1 + 3], radius=r, fill=(0, 0, 0, 100))
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=bg)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, outline=border_top, width=2)
    draw.line([(x0 + r, y1), (x1 - r, y1)], fill=border_bot, width=4)
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (x0 + x1 - tw) // 2
    ty = (y0 + y1 - th) // 2 - 2
    draw.text((tx, ty + 1), text, font=font, fill=(0, 0, 0, 200))
    draw.text((tx, ty), text, font=font, fill=(255, 255, 255))


def render_splash_screen_preview():
    splash_path = os.path.join(ASSETS_DIR, "splash.png")
    if os.path.exists(splash_path):
        img = Image.open(splash_path).convert("RGBA").resize((W, H))
        draw = ImageDraw.Draw(img)

        # Draw the single dynamic Godot loading UI (matching scenes/splash_screen.tscn)
        # Position: bottom margin 32px, height 140px
        f_status = get_font(13)
        f_prompt = get_regular_font(12)

        # Status Label
        status_text = "LOADING PUZZLE LEVELS..."
        sb = f_status.getbbox(status_text)
        stw = sb[2] - sb[0]
        # Text shadow + text
        draw.text(((W - stw) // 2, 836), status_text, font=f_status, fill=(0, 0, 0, 220))
        draw.text(((W - stw) // 2, 834), status_text, font=f_status, fill=(250, 218, 72))

        # Single crisp progress bar (40px margins left/right -> 460px wide, y: 862 to 878)
        bx0, by0, bx1, by1 = 40, 860, W - 40, 876
        # Background
        draw.rounded_rectangle([bx0, by0, bx1, by1], radius=6, fill=(15, 20, 33), outline=(184, 138, 51), width=2)
        # Fill (e.g. 75%)
        progress = 0.75
        fx1 = int(bx0 + (bx1 - bx0) * progress)
        draw.rounded_rectangle([bx0 + 2, by0 + 2, fx1, by1 - 2], radius=4, fill=(245, 166, 36))
        # Top highlight line on fill
        draw.line([(bx0 + 4, by0 + 3), (fx1 - 2, by0 + 3)], fill=(255, 217, 115), width=1)

        # Tap prompt
        prompt_text = "TAP ANYWHERE TO START"
        pb = f_prompt.getbbox(prompt_text)
        ptw = pb[2] - pb[0]
        draw.text(((W - ptw) // 2, 891), prompt_text, font=f_prompt, fill=(0, 0, 0, 200))
        draw.text(((W - ptw) // 2, 890), prompt_text, font=f_prompt, fill=(190, 210, 235))

        out_path = os.path.join(ARTIFACT_DIR, "preview_splash_screen.png")
        img.save(out_path)
        print("Saved preview_splash_screen.png")


def render_level_select_preview():
    # Load warehouse background
    bg_path = os.path.join(ASSETS_DIR, "warehouse_bg.jpg")
    bg = Image.open(bg_path).convert("RGBA").resize((W, H))

    # Dim vignette overlay
    overlay = Image.new("RGBA", (W, H), (12, 16, 24, 210))
    img = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(img)

    f_title = get_font(20)
    f_badge = get_font(14)
    f_btn = get_font(15)
    f_card_title = get_font(13)
    f_sub = get_regular_font(12)
    f_lvl_num = get_font(16)
    f_lvl_sub = get_font(11)

    # 1. Top Bar Panel
    draw.rectangle([0, 0, W, 62], fill=(20, 28, 41, 245))
    draw.line([(0, 62), (W, 62)], fill=(184, 138, 51), width=2)

    # Back button: (16, 10, 106, 52)
    draw_styled_button(draw, (16, 10, 106, 52), "← Back", is_primary=False, font=f_btn)

    # Title: SELECT LEVEL (centered)
    title_text = "SELECT LEVEL"
    tb = f_title.getbbox(title_text)
    tw = tb[2] - tb[0]
    draw.text(((W - tw) // 2, 19), title_text, font=f_title, fill=(0, 0, 0, 200))
    draw.text(((W - tw) // 2, 18), title_text, font=f_title, fill=(250, 218, 72))

    # Total Stars Pill Badge: (418, 12, 524, 50)
    draw.rounded_rectangle([418, 12, 524, 50], radius=8, fill=(18, 26, 38, 240), outline=(173, 133, 46), width=2)
    draw.line([(426, 50), (516, 50)], fill=(140, 100, 30), width=1)
    stars_pill_text = "★ 12/150"
    spb = f_badge.getbbox(stars_pill_text)
    spw = spb[2] - spb[0]
    draw.text((418 + (106 - spw) // 2, 21), stars_pill_text, font=f_badge, fill=(0, 0, 0, 220))
    draw.text((418 + (106 - spw) // 2, 20), stars_pill_text, font=f_badge, fill=(255, 224, 89))

    # 2. Campaign Progress Card (under Top Bar)
    cx0, cy0, cx1, cy1 = 18, 76, W - 18, 158
    # Card shadow & body
    draw.rounded_rectangle([cx0 + 2, cy0 + 3, cx1 + 2, cy1 + 3], radius=12, fill=(0, 0, 0, 130))
    draw.rounded_rectangle([cx0, cy0, cx1, cy1], radius=12, fill=(20, 28, 41, 240), outline=(173, 128, 46), width=2)
    draw.line([(cx0 + 10, cy1), (cx1 - 10, cy1)], fill=(120, 85, 25), width=2)

    # Card Header
    camp_title = "★ WAREHOUSE CAMPAIGN ★"
    draw.text((cx0 + 14, cy0 + 10), camp_title, font=f_card_title, fill=(250, 217, 89))
    badge_text = "50 SECTORS"
    bb = f_sub.getbbox(badge_text)
    draw.text((cx1 - 14 - (bb[2] - bb[0]), cy0 + 11), badge_text, font=f_sub, fill=(184, 204, 235))

    # Progress bar trough & fill
    pbx0, pby0, pbx1, pby1 = cx0 + 14, cy0 + 34, cx1 - 14, cy0 + 44
    draw.rounded_rectangle([pbx0, pby0, pbx1, pby1], radius=5, fill=(15, 20, 31), outline=(51, 64, 89), width=1)
    # Fill: 12 / 150 stars = 8%
    p_fill_w = int((pbx1 - pbx0) * (12.0 / 150.0))
    draw.rounded_rectangle([pbx0 + 1, pby0 + 1, pbx0 + p_fill_w, pby1 - 1], radius=4, fill=(235, 166, 38))
    draw.line([(pbx0 + 2, pby0 + 2), (pbx0 + p_fill_w - 2, pby0 + 2)], fill=(255, 220, 115), width=1)

    # Footer sub-stats
    draw.text((cx0 + 14, cy0 + 52), "★ 12 / 150 Stars Collected", font=f_sub, fill=(217, 230, 250))
    cleared_text = "4/50 Cleared • 8%"
    cb = f_sub.getbbox(cleared_text)
    draw.text((cx1 - 14 - (cb[2] - cb[0]), cy0 + 52), cleared_text, font=f_sub, fill=(140, 166, 199))

    # 3. 50-Level Grid (5 columns, starting at y = 172)
    col_w = 88
    row_h = 86
    gap_x = 16
    gap_y = 12
    start_x = (W - (5 * col_w + 4 * gap_x)) // 2 # Centered grid
    start_y = 172

    # Level mock records:
    # 1: 3★, 5m (Completed)
    # 2: 3★, 3m (Completed)
    # 3: 3★, 5m (Completed)
    # 4: 3★, 7m (Completed)
    # 5: ▶ Play (Current Unlocked)
    # 6..50: 🔒 Locked
    level_moves = {1: 5, 2: 3, 3: 5, 4: 7}

    for idx in range(1, 51):
        r = (idx - 1) // 5
        c = (idx - 1) % 5
        bx0 = start_x + c * (col_w + gap_x)
        by0 = start_y + r * (row_h + gap_y)
        bx1 = bx0 + col_w
        by1 = by0 + row_h

        # Don't draw beyond canvas
        if by0 >= H:
            break

        if idx <= 4:
            # Completed Level: Deep industrial slate + burnished gold bevel
            draw.rounded_rectangle([bx0 + 1, by0 + 3, bx1 + 1, by1 + 3], radius=10, fill=(0, 0, 0, 90))
            draw.rounded_rectangle([bx0, by0, bx1, by1], radius=10, fill=(28, 38, 56), outline=(199, 153, 56), width=2)
            draw.line([(bx0 + 6, by1), (bx1 - 6, by1)], fill=(140, 102, 31), width=4)

            # Top highlight
            draw.line([(bx0 + 8, by0 + 2), (bx1 - 8, by0 + 2)], fill=(235, 204, 115), width=1)

            # Level number
            num_str = str(idx)
            nb = f_lvl_num.getbbox(num_str)
            nw = nb[2] - nb[0]
            draw.text((bx0 + (col_w - nw)//2, by0 + 12), num_str, font=f_lvl_num, fill=(0, 0, 0, 200))
            draw.text((bx0 + (col_w - nw)//2, by0 + 11), num_str, font=f_lvl_num, fill=(255, 240, 200))

            # Sub: ★★★ (just stars, no moves count)
            sub_str = "★★★"
            f_stars = get_font(13)
            sb = f_stars.getbbox(sub_str)
            sw = sb[2] - sb[0]
            draw.text((bx0 + (col_w - sw)//2, by0 + 48), sub_str, font=f_stars, fill=(0, 0, 0, 220))
            draw.text((bx0 + (col_w - sw)//2, by0 + 47), sub_str, font=f_stars, fill=(255, 216, 77))

        elif idx == 5:
            # Current Active Level: Glowing Radiant Amber
            draw.rounded_rectangle([bx0 + 1, by0 + 4, bx1 + 1, by1 + 4], radius=10, fill=(219, 138, 31, 140))
            draw.rounded_rectangle([bx0, by0, bx1, by1], radius=10, fill=(219, 138, 31), outline=(255, 224, 122), width=2)
            draw.line([(bx0 + 6, by1), (bx1 - 6, by1)], fill=(140, 77, 10), width=5)
            # Top gleam
            draw.line([(bx0 + 8, by0 + 2), (bx1 - 8, by0 + 2)], fill=(255, 245, 184), width=1)

            # Level number
            num_str = "5"
            nb = f_lvl_num.getbbox(num_str)
            nw = nb[2] - nb[0]
            draw.text((bx0 + (col_w - nw)//2, by0 + 12), num_str, font=f_lvl_num, fill=(0, 0, 0, 200))
            draw.text((bx0 + (col_w - nw)//2, by0 + 11), num_str, font=f_lvl_num, fill=(255, 255, 255))

            # Play arrow ▶
            play_str = "▶"
            pb = f_lvl_num.getbbox(play_str)
            pw = pb[2] - pb[0]
            draw.text((bx0 + (col_w - pw)//2, by0 + 46), play_str, font=f_lvl_num, fill=(0, 0, 0, 200))
            draw.text((bx0 + (col_w - pw)//2, by0 + 45), play_str, font=f_lvl_num, fill=(255, 255, 255))

        else:
            # Locked Levels: Crisp matte dark slate steel with subtle border and bronze lock
            draw.rounded_rectangle([bx0 + 1, by0 + 2, bx1 + 1, by1 + 2], radius=10, fill=(0, 0, 0, 60))
            draw.rounded_rectangle([bx0, by0, bx1, by1], radius=10, fill=(20, 26, 38, 235), outline=(46, 56, 77), width=1)
            draw.line([(bx0 + 6, by1), (bx1 - 6, by1)], fill=(28, 36, 48), width=2)

            # Subdued level number
            num_str = str(idx)
            nb = f_lvl_num.getbbox(num_str)
            nw = nb[2] - nb[0]
            draw.text((bx0 + (col_w - nw)//2, by0 + 14), num_str, font=f_lvl_num, fill=(112, 125, 148))

            # Neat lock symbol
            lock_str = "🔒"
            lb = f_lvl_sub.getbbox(lock_str)
            lw = lb[2] - lb[0]
            draw.text((bx0 + (col_w - lw)//2, by0 + 48), lock_str, font=f_lvl_sub, fill=(184, 150, 77))

    out_path = os.path.join(ARTIFACT_DIR, "preview_level_select.png")
    img.save(out_path)
    print("Saved preview_level_select.png")


if __name__ == "__main__":
    render_main_menu_preview()
    render_gameplay_preview()
    render_splash_screen_preview()
    render_win_modal_preview()
    render_level_select_preview()


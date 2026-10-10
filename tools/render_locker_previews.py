#!/usr/bin/env python3
"""
Pixel Porter - Porter Locker Cosmetics Visualizer (Phase 3)
Generates high-fidelity visual render previews for:
- Porter Locker Modal: Worker Outfits Tab (Classic Denim, Safety Vest, Foreman, Golden Master)
- Porter Locker Modal: Crate Skins Tab (Classic Pine, Steel Container, Hazard Crate)
- In-Game Action Preview: Equipped Worker & Crate skins with dynamic visual accessories
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

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

def draw_styled_button(draw, rect, text, is_primary=False, is_equipped=False, is_locked=False, font=None, custom_border=None):
    x0, y0, x1, y1 = rect
    r = 8
    if is_equipped:
        bg = (40, 110, 65)
        border_top = (75, 180, 110)
        border_bot = (18, 55, 30)
        text_col = (230, 255, 235)
    elif is_locked:
        bg = (24, 28, 38)
        border_top = (45, 52, 68)
        border_bot = (14, 18, 25)
        text_col = (130, 140, 155)
    elif is_primary:
        bg = (218, 138, 30)
        border_top = custom_border if custom_border else (255, 220, 115)
        border_bot = (110, 55, 10)
        text_col = (255, 255, 255)
    else:
        bg = (33, 43, 61)
        border_top = custom_border if custom_border else (80, 110, 160)
        border_bot = (18, 26, 40)
        text_col = (240, 244, 250)

    # Shadow
    draw.rounded_rectangle([x0 + 1, y0 + 3, x1 + 1, y1 + 3], radius=r, fill=(0, 0, 0, 90))
    # Fill
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=bg)
    # Border
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, outline=border_top, width=2)
    draw.line([(x0 + r, y1), (x1 - r, y1)], fill=border_bot, width=3)

    if font and text:
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = (x0 + x1 - tw) // 2
        ty = (y0 + y1 - th) // 2 - 2
        draw.text((tx, ty), text, fill=text_col, font=font)

def draw_locker_modal(active_tab="outfits", player_stars=65):
    img = Image.new("RGBA", (W, H), (14, 18, 25, 255))
    draw = ImageDraw.Draw(img)

    # Load and draw background wallpaper
    bg_path = os.path.join(ASSETS_DIR, "splash.png")
    if os.path.exists(bg_path):
        bg = Image.open(bg_path).convert("RGBA")
        bg = bg.resize((W, H), Image.Resampling.LANCZOS)
        # Dim wallpaper
        overlay = Image.new("RGBA", (W, H), (10, 14, 22, 210))
        img.paste(bg, (0, 0))
        img.alpha_composite(overlay)
        draw = ImageDraw.Draw(img)

    # Modal Backdrop blur/scrim
    scrim = Image.new("RGBA", (W, H), (6, 9, 14, 235))
    img.alpha_composite(scrim)
    draw = ImageDraw.Draw(img)

    # Main Card
    card_x0, card_y0 = 36, 90
    card_x1, card_y1 = W - 36, H - 90
    r = 18

    # Outer glow / shadow
    for offset, alpha in [(6, 40), (4, 70), (2, 100)]:
        draw.rounded_rectangle([card_x0 - offset, card_y0 - offset, card_x1 + offset, card_y1 + offset], radius=r + offset, outline=(220, 160, 40, alpha), width=1)
    
    # Card base
    draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=r, fill=(20, 26, 38, 255), outline=(218, 165, 32, 255), width=2)
    # Inner header banner
    draw.rounded_rectangle([card_x0 + 2, card_y0 + 2, card_x1 - 2, card_y0 + 74], radius=r - 2, fill=(28, 36, 52, 255))
    draw.line([(card_x0 + 2, card_y0 + 74), (card_x1 - 2, card_y0 + 74)], fill=(218, 165, 32, 180), width=2)

    font_title = get_font(20)
    font_badge = get_font(13)
    font_tabs = get_font(14)
    font_item_name = get_font(15)
    font_item_desc = get_regular_font(11)
    font_btn = get_font(12)
    font_icon = get_font(24)

    # Title
    draw.text((card_x0 + 20, card_y0 + 16), "🦺 THE PORTER LOCKER", fill=(255, 235, 170), font=font_title)
    
    # Star badge
    badge_text = f"★ {player_stars} / 150 Stars Collected"
    draw.rounded_rectangle([card_x0 + 20, card_y0 + 44, card_x1 - 20, card_y0 + 66], radius=6, fill=(35, 45, 65), outline=(230, 180, 50), width=1)
    draw.text((card_x0 + 32, card_y0 + 47), badge_text, fill=(255, 215, 64), font=font_badge)

    # Tabs
    tab_y = card_y0 + 86
    tab_h = 38
    mid_x = (card_x0 + card_x1) // 2

    is_outfits = (active_tab == "outfits")
    draw_styled_button(draw, [card_x0 + 16, tab_y, mid_x - 6, tab_y + tab_h], "👕 OUTFITS", is_primary=is_outfits, font=font_tabs)
    draw_styled_button(draw, [mid_x + 6, tab_y, card_x1 - 16, tab_y + tab_h], "📦 CRATES", is_primary=(not is_outfits), font=font_tabs)

    # Items container
    content_y0 = tab_y + tab_h + 14

    items = []
    if active_tab == "outfits":
        items = [
            {
                "id": "classic",
                "icon": "🧢",
                "name": "Classic Denim",
                "desc": "The signature red cap & blue work dungarees.",
                "stars": 0,
                "equipped": False,
                "accent": (70, 130, 230)
            },
            {
                "id": "safety_vest",
                "icon": "🦺",
                "name": "Safety Vest",
                "desc": "High-vis neon orange with reflective safety stripes.",
                "stars": 25,
                "equipped": True,
                "accent": (255, 128, 25)
            },
            {
                "id": "foreman",
                "icon": "👷",
                "name": "Foreman",
                "desc": "Polished industrial hardhat & durable khaki workwear.",
                "stars": 60,
                "equipped": False,
                "accent": (235, 205, 50)
            },
            {
                "id": "golden_porter",
                "icon": "👑",
                "name": "Golden Master",
                "desc": "Radiant prestige uniform with shimmering aura.",
                "stars": 120,
                "equipped": False,
                "accent": (255, 215, 50)
            }
        ]
    else:
        items = [
            {
                "id": "classic_wood",
                "icon": "📦",
                "name": "Classic Pine",
                "desc": "Traditional pine shipping crate with steel brackets.",
                "stars": 0,
                "equipped": False,
                "accent": (215, 165, 90)
            },
            {
                "id": "steel_container",
                "icon": "🗄️",
                "name": "Steel Container",
                "desc": "Cold-rolled reinforced steel freight container.",
                "stars": 40,
                "equipped": False,
                "accent": (150, 190, 240)
            },
            {
                "id": "hazard_box",
                "icon": "☣️",
                "name": "Hazard Crate",
                "desc": "High-voltage caution crate with pulsing markers.",
                "stars": 80,
                "equipped": False,
                "accent": (255, 180, 40)
            }
        ]

    card_h = 100
    for idx, item in enumerate(items):
        iy0 = content_y0 + idx * (card_h + 10)
        iy1 = iy0 + card_h
        ix0 = card_x0 + 16
        ix1 = card_x1 - 16

        is_unlocked = (player_stars >= item["stars"])
        is_eq = item["equipped"]

        # Item Card Base
        card_bg = (30, 38, 54) if is_unlocked else (22, 27, 36)
        card_border = item["accent"] if is_eq else ((70, 90, 125) if is_unlocked else (45, 52, 68))
        draw.rounded_rectangle([ix0, iy0, ix1, iy1], radius=10, fill=card_bg, outline=card_border, width=2 if is_eq else 1)

        # Icon box
        draw.rounded_rectangle([ix0 + 10, iy0 + 12, ix0 + 74, iy1 - 12], radius=8, fill=(18, 23, 33), outline=item["accent"], width=1)
        draw.text((ix0 + 26, iy0 + 26), item["icon"], font=font_icon, fill=(255, 255, 255))

        # Title & Description
        title_col = (255, 230, 120) if is_eq else ((240, 246, 255) if is_unlocked else (150, 160, 175))
        draw.text((ix0 + 86, iy0 + 14), item["name"], font=font_item_name, fill=title_col)

        if is_unlocked:
            draw.text((ix0 + 86, iy0 + 36), item["desc"], font=font_item_desc, fill=(170, 185, 205))
            status_text = f"★ {item['stars']} Stars (Unlocked)" if item["stars"] > 0 else "Free Starter"
            draw.text((ix0 + 86, iy0 + 64), status_text, font=get_regular_font(10), fill=(100, 200, 130))
        else:
            draw.text((ix0 + 86, iy0 + 36), item["desc"], font=font_item_desc, fill=(130, 140, 155))
            draw.text((ix0 + 86, iy0 + 64), f"🔒 {item['stars']} Stars required (Collect {item['stars'] - player_stars} more)", font=get_font(10), fill=(255, 120, 90))

        # Equip / Action Button
        btn_w, btn_h = 92, 36
        bx1 = ix1 - 12
        bx0 = bx1 - btn_w
        by0 = iy0 + (card_h - btn_h) // 2
        by1 = by0 + btn_h

        if is_eq:
            draw_styled_button(draw, [bx0, by0, bx1, by1], "✓ IN USE", is_equipped=True, font=font_btn)
        elif is_unlocked:
            draw_styled_button(draw, [bx0, by0, bx1, by1], "EQUIP", is_primary=True, font=font_btn)
        else:
            draw_styled_button(draw, [bx0, by0, bx1, by1], "LOCKED", is_locked=True, font=font_btn)

    # Close Button
    close_y = card_y1 - 58
    draw_styled_button(draw, [card_x0 + 40, close_y, card_x1 - 40, close_y + 44], "BACK TO MENU", font=get_font(14))

    return img

def draw_in_game_cosmetics_preview():
    img = Image.new("RGBA", (W, H), (14, 18, 25, 255))
    draw = ImageDraw.Draw(img)

    # Cyber Depot chapter theme (Chapter 3)
    theme = {
        "bg": (12, 14, 20),
        "floor": (24, 28, 38),
        "floor_alt": (20, 24, 32),
        "wall": (35, 42, 58),
        "wall_shadow": (16, 20, 28),
        "accent": (255, 170, 45),
        "goal": (35, 220, 135)
    }

    # Top Bar
    draw.rectangle([0, 0, W, 80], fill=(16, 20, 30))
    draw.line([(0, 80), (W, 80)], fill=(255, 170, 45), width=2)
    font_bold = get_font(18)
    font_reg = get_regular_font(13)

    # Title & Chapter Badge
    draw.text((20, 18), "LEVEL 38 / 50", fill=(255, 235, 170), font=font_bold)
    draw.text((20, 48), "MOVES: 11  •  PUSHES: 4", fill=(180, 195, 215), font=font_reg)

    # Chapter badge in top right
    draw.rounded_rectangle([W - 130, 20, W - 20, 58], radius=8, fill=(28, 34, 48), outline=(255, 170, 45), width=2)
    draw.text((W - 118, 28), "⚡ CH. 3", fill=(255, 180, 50), font=get_font(15))

    # Grid Area
    grid_size = 6
    tile = 68
    grid_w = grid_size * tile
    gx0 = (W - grid_w) // 2
    gy0 = 180

    # Draw Outer Bevel Border for Board
    draw.rounded_rectangle([gx0 - 12, gy0 - 12, gx0 + grid_w + 12, gy0 + grid_w + 12], radius=14, fill=(18, 22, 32), outline=(255, 170, 45), width=3)

    # Draw Tiles
    for r in range(grid_size):
        for c in range(grid_size):
            tx0 = gx0 + c * tile
            ty0 = gy0 + r * tile
            tx1 = tx0 + tile
            ty1 = ty0 + tile

            # Walls on border
            if r == 0 or r == grid_size - 1 or c == 0 or c == grid_size - 1:
                draw.rectangle([tx0, ty0, tx1, ty1], fill=theme["wall"], outline=theme["wall_shadow"], width=2)
                # Wall rivet details
                draw.rectangle([tx0 + 6, ty0 + 6, tx1 - 6, ty1 - 6], outline=(55, 65, 88), width=1)
            else:
                col = theme["floor"] if (r + c) % 2 == 0 else theme["floor_alt"]
                draw.rectangle([tx0, ty0, tx1, ty1], fill=col, outline=(30, 36, 48), width=1)

    # Goal Pad at (3, 4)
    g_cx = gx0 + 4 * tile + tile // 2
    g_cy = gy0 + 3 * tile + tile // 2
    draw.ellipse([g_cx - 24, g_cy - 24, g_cx + 24, g_cy + 24], fill=(30, 80, 55), outline=theme["goal"], width=3)
    draw.text((g_cx - 10, g_cy - 12), "★", fill=(255, 235, 100), font=get_font(20))

    # Crate Skin: Hazard Crate at (3, 3)
    cx0 = gx0 + 3 * tile + 4
    cy0 = gy0 + 3 * tile + 4
    cx1 = cx0 + tile - 8
    cy1 = cy0 + tile - 8

    # Hazard box base
    draw.rounded_rectangle([cx0, cy0, cx1, cy1], radius=6, fill=(225, 170, 30), outline=(255, 215, 60), width=2)
    # Caution stripes
    draw.line([(cx0 + 10, cy0 + 6), (cx0 + 6, cy0 + 10)], fill=(30, 30, 30), width=3)
    draw.line([(cx0 + 26, cy0 + 6), (cx0 + 6, cy0 + 26)], fill=(30, 30, 30), width=3)
    draw.line([(cx0 + 44, cy0 + 6), (cx0 + 6, cy0 + 44)], fill=(30, 30, 30), width=3)
    draw.line([(cx1 - 6, cy1 - 20), (cx1 - 20, cy1 - 6)], fill=(30, 30, 30), width=3)
    # Hazard Icon
    draw.text((cx0 + 18, cy0 + 14), "☣️", font=get_font(20))

    # Worker Skin: Safety Vest Worker at (3, 2)
    px0 = gx0 + 2 * tile + 6
    py0 = gy0 + 3 * tile + 6
    px1 = px0 + tile - 12
    py1 = py0 + tile - 12

    # Draw worker body with Safety Vest
    # Shadow
    draw.ellipse([px0 + 4, py1 - 8, px1 - 4, py1 + 2], fill=(0, 0, 0, 120))
    # Head & Cap
    draw.ellipse([px0 + 12, py0 + 6, px1 - 12, py0 + 26], fill=(245, 195, 150))
    draw.arc([px0 + 8, py0 + 4, px1 - 8, py0 + 20], start=180, end=360, fill=(220, 50, 40), width=4) # Red cap
    # Body with High-Vis Safety Vest
    draw.rounded_rectangle([px0 + 8, py0 + 22, px1 - 8, py1 - 8], radius=6, fill=(255, 115, 20), outline=(255, 180, 40), width=2)
    # Reflective silver stripes on vest
    draw.line([(px0 + 8, py0 + 30), (px1 - 8, py0 + 30)], fill=(240, 248, 255), width=3)
    draw.line([(px0 + 8, py0 + 38), (px1 - 8, py0 + 38)], fill=(240, 248, 255), width=3)

    # HUD Cosmetics Indicator Panel below board
    hud_y = gy0 + grid_w + 36
    draw.rounded_rectangle([36, hud_y, W - 36, hud_y + 110], radius=12, fill=(22, 28, 40), outline=(255, 170, 45), width=2)

    draw.text((54, hud_y + 14), "ACTIVE PORTER LOCKER COSMETICS", font=get_font(13), fill=(255, 220, 120))
    # Equipped badges
    draw.rounded_rectangle([54, hud_y + 42, 250, hud_y + 92], radius=6, fill=(30, 40, 58), outline=(255, 130, 30), width=1)
    draw.text((64, hud_y + 48), "🦺 Safety Vest", font=get_font(12), fill=(255, 180, 80))
    draw.text((64, hud_y + 68), "Neon orange + reflectors", font=get_regular_font(10), fill=(180, 195, 215))

    draw.rounded_rectangle([270, hud_y + 42, W - 54, hud_y + 92], radius=6, fill=(30, 40, 58), outline=(255, 190, 40), width=1)
    draw.text((280, hud_y + 48), "☣️ Hazard Crate", font=get_font(12), fill=(255, 215, 60))
    draw.text((280, hud_y + 68), "High-voltage caution rim", font=get_regular_font(10), fill=(180, 195, 215))

    # Controls Bar
    btn_y = hud_y + 130
    draw_styled_button(draw, [36, btn_y, 140, btn_y + 44], "RESET ↺", font=get_font(13))
    draw_styled_button(draw, [156, btn_y, 260, btn_y + 44], "UNDO ↶", font=get_font(13))
    draw_styled_button(draw, [276, btn_y, W - 36, btn_y + 44], "HINT 💡", is_primary=True, font=get_font(13))

    return img

def main():
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    temp_dir = os.path.join(ARTIFACT_DIR, ".tempmediaStorage")
    os.makedirs(temp_dir, exist_ok=True)

    print("Generating Porter Locker Outfits Modal Preview...")
    img_outfits = draw_locker_modal(active_tab="outfits", player_stars=65)
    outfits_path = os.path.join(temp_dir, "preview_locker_outfits.png")
    img_outfits.save(outfits_path, "PNG")
    print(f"Saved: {outfits_path}")

    print("Generating Porter Locker Crates Modal Preview...")
    img_crates = draw_locker_modal(active_tab="crates", player_stars=65)
    crates_path = os.path.join(temp_dir, "preview_locker_crates.png")
    img_crates.save(crates_path, "PNG")
    print(f"Saved: {crates_path}")

    print("Generating In-Game Cosmetics Action Preview...")
    img_ingame = draw_in_game_cosmetics_preview()
    ingame_path = os.path.join(temp_dir, "preview_in_game_cosmetics.png")
    img_ingame.save(ingame_path, "PNG")
    print(f"Saved: {ingame_path}")

if __name__ == "__main__":
    main()

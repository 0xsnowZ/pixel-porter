#!/usr/bin/env python3
"""
tools/render_main_menu_preview.py

Generates an accurate visual mockup of the proposed 3-Tier Modern Main Menu:
- TopBar HUD: Player Stars badge & Sector indicator on left, Quick squircle buttons [🌐] [🏆] [⚙] on right
- Hero Center: Floating 3D Pixel Sokoban: Warehouse Rush logo
- Action Deck:
    - Primary Hero Button: [ ▶ CONTINUE (SECTOR 4) ] (radiant gold)
    - Secondary Deck: [ 🗺️ LEVEL SELECT ] [ 🦺 THE LOCKER ] side-by-side
- Borderless, spacious, high-value presentation over warehouse_bg.jpg
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ARTIFACT_DIR = "/home/snowz/.gemini/antigravity-ide/brain/585b805d-dc89-49ec-9d75-7dca930224d1"
BG_PATH = "/home/snowz/godot/assets/warehouse_bg.jpg"
LOGO_PATH = "/home/snowz/godot/assets/logo.png"


def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def render_mockup():
    bg = Image.open(BG_PATH).convert("RGBA")
    w, h = bg.size  # 540x960

    # 1. Atmospheric subtle vignette (only 35% opacity, letting the gorgeous background shine!)
    vignette = Image.new("RGBA", (w, h), (10, 14, 22, 90))
    bg.paste(vignette, (0, 0), vignette)

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 2. TIER 1: TOP HUD (Safe Area, y=44..96)
    # -------------------------------------------------------------
    # Left: Player Progress Pill [★ 42/150 • Sector 4]
    star_x0, star_y0, star_w, star_h = 24, 48, 170, 40
    draw.rounded_rectangle([star_x0, star_y0, star_x0 + star_w, star_y0 + star_h], radius=10, fill=(16, 22, 34, 210), outline=(245, 173, 35, 180), width=1)
    
    f_star = get_font(13, bold=True)
    draw.text((star_x0 + 14, star_y0 + 11), "★ 42/150", font=f_star, fill=(255, 215, 64, 255))
    draw.text((star_x0 + 94, star_y0 + 11), "• Sector 4", font=get_font(12, bold=False), fill=(180, 200, 225, 230))

    # Right: Quick Squircle Utility Buttons [🌐] [🏆] [⚙]
    btn_size = 40
    btn_gap = 10
    rx_start = w - 24 - (3 * btn_size + 2 * btn_gap)  # 540 - 24 - 140 = 376

    quick_icons = [
        ("🌐", "Lang"),
        ("🏆", "Achieve"),
        ("⚙", "Settings")
    ]
    for i, (icon, name) in enumerate(quick_icons):
        bx = rx_start + i * (btn_size + btn_gap)
        by = star_y0
        # Glassmorphic button
        draw.rounded_rectangle([bx, by, bx + btn_size, by + btn_size], radius=10, fill=(18, 26, 40, 210), outline=(80, 105, 140, 160), width=1)
        # Icon
        f_ico = get_font(16, bold=False)
        ibbox = f_ico.getbbox(icon)
        iw = ibbox[2] - ibbox[0]
        ih = ibbox[3] - ibbox[1]
        draw.text((bx + (btn_size - iw) // 2, by + (btn_size - ih) // 2 - 2), icon, font=f_ico, fill=(240, 245, 255, 240))

    # 3. TIER 2: HERO BRANDING (Logo)
    # -------------------------------------------------------------
    logo = Image.open(LOGO_PATH).convert("RGBA")
    # Resize logo to fit nicely at width ~320
    lw, lh = logo.size
    target_lw = 320
    target_lh = int(lh * (target_lw / float(lw)))
    logo_resized = logo.resize((target_lw, target_lh), Image.Resampling.LANCZOS)
    
    logo_x = (w - target_lw) // 2
    logo_y = 120
    bg.paste(logo_resized, (logo_x, logo_y), logo_resized)

    # Subtitle badge under logo
    sub_text = "★ RETRO WAREHOUSE SOKOBAN ★"
    f_sub = get_font(13, bold=True)
    sbbox = f_sub.getbbox(sub_text)
    sw = sbbox[2] - sbbox[0]
    sx = (w - sw) // 2
    sy = logo_y + target_lh + 12

    # Pill behind subtitle
    pad_x, pad_y = 16, 5
    draw.rounded_rectangle([sx - pad_x, sy - pad_y, sx + sw + pad_x, sy + 16 + pad_y], radius=8, fill=(12, 16, 26, 190), outline=(245, 173, 35, 120), width=1)
    draw.text((sx, sy), sub_text, font=f_sub, fill=(255, 215, 64, 255))

    # 4. TIER 3: FOCUSED ACTION DECK (Bottom y=670..880)
    # -------------------------------------------------------------
    deck_x0 = 36
    deck_x1 = w - 36
    deck_w = deck_x1 - deck_x0  # 468

    # A. Primary Hero Button [ CONTINUE (SECTOR 4) ]
    hero_y0 = 680
    hero_h = 60
    hero_y1 = hero_y0 + hero_h

    # Ambient golden glow behind hero button
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.rounded_rectangle([deck_x0 - 4, hero_y0 - 4, deck_x1 + 4, hero_y1 + 4], radius=16, fill=(245, 173, 35, 80))
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    bg.paste(glow, (0, 0), glow)

    # Hero Button Base & Border
    draw.rounded_rectangle([deck_x0, hero_y0, deck_x1, hero_y1], radius=14, fill=(245, 168, 30, 255), outline=(255, 235, 150, 255), width=2)
    # Top specular shine
    draw.line([(deck_x0 + 14, hero_y0 + 2), (deck_x1 - 14, hero_y0 + 2)], fill=(255, 245, 200, 220), width=1)

    # Hero Button Text
    hero_text = "▶  CONTINUE  (SECTOR 4)"
    f_hero = get_font(18, bold=True)
    hbbox = f_hero.getbbox(hero_text)
    hw = hbbox[2] - hbbox[0]
    hx = (w - hw) // 2
    hy = hero_y0 + (hero_h - (hbbox[3] - hbbox[1])) // 2 - 2

    # Crisp shadow & dark navy lettering
    draw.text((hx, hy + 2), hero_text, font=f_hero, fill=(120, 60, 0, 200))
    draw.text((hx, hy), hero_text, font=f_hero, fill=(20, 24, 34, 255))

    # B. Secondary Dual Deck: [ 🗺️ LEVEL SELECT ] and [ 🦺 THE LOCKER ]
    sec_y0 = hero_y1 + 14
    sec_h = 52
    sec_y1 = sec_y0 + sec_h
    gap = 12
    card_w = (deck_w - gap) // 2  # ~228

    # Left: Level Select
    c1_x0 = deck_x0
    c1_x1 = c1_x0 + card_w
    draw.rounded_rectangle([c1_x0, sec_y0, c1_x1, sec_y1], radius=12, fill=(18, 24, 38, 235), outline=(90, 115, 150, 200), width=1)
    # Inner subtle glow line
    draw.line([(c1_x0 + 10, sec_y0 + 1), (c1_x1 - 10, sec_y0 + 1)], fill=(130, 160, 200, 120), width=1)

    t_levels = "🗺️  50 SECTORS"
    f_card = get_font(14, bold=True)
    lbbox = f_card.getbbox(t_levels)
    draw.text(((c1_x0 + c1_x1 - (lbbox[2] - lbbox[0])) // 2, sec_y0 + 16), t_levels, font=f_card, fill=(240, 246, 255, 245))

    # Right: Locker (Cosmetics)
    c2_x0 = c1_x1 + gap
    c2_x1 = deck_x1
    draw.rounded_rectangle([c2_x0, sec_y0, c2_x1, sec_y1], radius=12, fill=(18, 24, 38, 235), outline=(90, 115, 150, 200), width=1)
    draw.line([(c2_x0 + 10, sec_y0 + 1), (c2_x1 - 10, sec_y0 + 1)], fill=(130, 160, 200, 120), width=1)

    t_locker = "🦺  THE LOCKER"
    kbbox = f_card.getbbox(t_locker)
    draw.text(((c2_x0 + c2_x1 - (kbbox[2] - kbbox[0])) // 2, sec_y0 + 16), t_locker, font=f_card, fill=(240, 246, 255, 245))

    # 5. FOOTER (Bottom Safe Margin)
    f_foot = get_font(11, bold=False)
    foot_text = "Pixel Sokoban: Warehouse Rush v1.0 • Android"
    ftbbox = f_foot.getbbox(foot_text)
    draw.text(((w - (ftbbox[2] - ftbbox[0])) // 2, h - 34), foot_text, font=f_foot, fill=(140, 155, 180, 180))

    bg.paste(overlay, (0, 0), overlay)

    out_path = os.path.join(ARTIFACT_DIR, "main_menu_premium_mockup.png")
    bg.save(out_path, "PNG")
    print("Modern main menu mockup successfully saved to:", out_path)


if __name__ == "__main__":
    render_mockup()

#!/usr/bin/env python3
"""
tools/render_store_assets.py

Generates professional, high-impact marketing visuals for Pixel Porter Google Play Store listing:
1. 512x512 High-Res App Icon (assets/store_icon_512.png)
2. 1024x500 Feature Graphic Banner (assets/feature_graphic_1024x500.png)
3. 5 Portrait Promotional Screenshots (1080x1920) with high-contrast ASO caption headers:
   - promo_1_levels.png: "50 CLEVER RETRO LEVELS"
   - promo_2_chapters.png: "3 WAREHOUSE CHAPTERS"
   - promo_3_locker.png: "THE PORTER LOCKER"
   - promo_4_hints.png: "SMART HINT ECONOMY"
   - promo_5_achievements.png: "9 WAREHOUSE ACHIEVEMENTS"

Also outputs copies directly into the IDE artifacts directory for instant review.
"""

import os
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ARTIFACTS_DIR = "/home/snowz/.gemini/antigravity-ide/brain/9a93013c-7615-47d7-ae14-3f8a6be1d265"
ASSETS_DIR = "/home/snowz/godot/assets"

# Common Fonts
def get_font(size, bold=False):
    # Try common Linux system fonts
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/noto/NotoSans-Bold.ttf" if bold else "/usr/share/fonts/noto/NotoSans-Regular.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def create_radial_gradient(size, inner_color, outer_color):
    w, h = size
    img = Image.new("RGBA", size, outer_color)
    # Fast concentric circle approximation
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    max_r = int(((w/2)**2 + (h/2)**2)**0.5)
    center_x, center_y = w // 2, h // 2
    
    # Draw gradient rings
    steps = 60
    for i in range(steps, 0, -1):
        ratio = i / float(steps)
        r = int(max_r * ratio)
        col = (
            int(inner_color[0] + (outer_color[0] - inner_color[0]) * ratio),
            int(inner_color[1] + (outer_color[1] - inner_color[1]) * ratio),
            int(inner_color[2] + (outer_color[2] - inner_color[2]) * ratio),
            255
        )
        draw.ellipse([center_x - r, center_y - r, center_x + r, center_y + r], fill=col)
    
    return overlay


# ==============================================================================
# 1. 512x512 HIGH-RES STORE ICON
# ==============================================================================
def render_store_icon():
    print("Generating 512x512 Store Icon...")
    size = (512, 512)
    img = Image.new("RGBA", size, (15, 23, 42, 255)) # Slate dark base
    
    # 1. Background Radial Glow
    bg_glow = create_radial_gradient(size, (30, 41, 59, 255), (10, 15, 28, 255))
    img.paste(bg_glow, (0, 0))
    draw = ImageDraw.Draw(img)

    # 2. Isometric Grid / Floor Pattern subtle overlay
    for y in range(320, 512, 24):
        draw.line([(0, y), (512, y)], fill=(30, 58, 90, 80), width=2)
    for x in range(0, 512, 32):
        draw.line([(x, 320), (x - 60, 512)], fill=(30, 58, 90, 80), width=2)
        draw.line([(x, 320), (x + 60, 512)], fill=(30, 58, 90, 80), width=2)

    # 3. Glowing Goal Pad in Foreground
    pad_box = [160, 390, 352, 470]
    draw.ellipse(pad_box, fill=(16, 185, 129, 90), outline=(52, 211, 153, 230), width=4)
    draw.ellipse([185, 410, 327, 450], fill=(5, 150, 105, 140))
    # Glowing Target Cross
    draw.line([(256, 400), (256, 460)], fill=(110, 231, 183, 240), width=4)
    draw.line([(210, 430), (302, 430)], fill=(110, 231, 183, 240), width=4)

    # 4. Large Golden Wooden / Heavy Duty Crate
    crate_x, crate_y = 260, 210
    crate_w, crate_h = 180, 180
    # Drop shadow
    shadow = Image.new("RGBA", size, (0,0,0,0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rectangle([crate_x - 10, crate_y + 10, crate_x + crate_w + 10, crate_y + crate_h + 15], fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    img.paste(shadow, (0,0), shadow)

    # Crate body
    draw.rectangle([crate_x, crate_y, crate_x + crate_w, crate_y + crate_h], fill=(217, 119, 6), outline=(245, 158, 11), width=5)
    # Crate cross planks
    draw.line([(crate_x, crate_y), (crate_x + crate_w, crate_y + crate_h)], fill=(180, 83, 9), width=8)
    draw.line([(crate_x, crate_y + crate_h), (crate_x + crate_w, crate_y)], fill=(180, 83, 9), width=8)
    # Crate inner frame
    draw.rectangle([crate_x + 16, crate_y + 16, crate_x + crate_w - 16, crate_y + crate_h - 16], outline=(251, 191, 36), width=4)
    # Corner bolts
    for bx, by in [(crate_x + 10, crate_y + 10), (crate_x + crate_w - 10, crate_y + 10), (crate_x + 10, crate_y + crate_h - 10), (crate_x + crate_w - 10, crate_y + crate_h - 10)]:
        draw.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=(254, 240, 138))

    # 5. Pixel Porter Character pushing the crate
    char_x, char_y = 80, 170
    # Safety Hard Hat
    draw.ellipse([char_x + 30, char_y, char_x + 130, char_y + 60], fill=(245, 158, 11), outline=(251, 191, 36), width=4)
    draw.rectangle([char_x + 20, char_y + 40, char_x + 140, char_y + 55], fill=(217, 119, 6)) # Hat brim
    # Head & Face
    draw.rectangle([char_x + 45, char_y + 55, char_x + 115, char_y + 110], fill=(254, 215, 170))
    # Cheerful Eyes (Anime / Pixel Style)
    draw.rectangle([char_x + 85, char_y + 70, char_x + 95, char_y + 85], fill=(15, 23, 42))
    draw.rectangle([char_x + 88, char_y + 72, char_x + 93, char_y + 76], fill=(255, 255, 255))
    draw.arc([char_x + 75, char_y + 85, char_x + 105, char_y + 102], 0, 180, fill=(225, 29, 72), width=3)
    # Blue Work Dungarees + Neon Orange Vest
    draw.rectangle([char_x + 35, char_y + 110, char_x + 125, char_y + 190], fill=(30, 58, 138)) # Dungarees
    # High-vis Neon Vest
    draw.rectangle([char_x + 35, char_y + 110, char_x + 75, char_y + 180], fill=(249, 115, 22))
    draw.rectangle([char_x + 85, char_y + 110, char_x + 125, char_y + 180], fill=(249, 115, 22))
    draw.line([(char_x + 35, char_y + 140), (char_x + 125, char_y + 140)], fill=(254, 240, 138), width=6) # Reflective band
    # Pushing Arms (Muscular, gripping the crate)
    draw.line([(char_x + 110, char_y + 130), (crate_x + 15, crate_y + 50)], fill=(254, 215, 170), width=18)
    draw.line([(char_x + 105, char_y + 155), (crate_x + 15, crate_y + 85)], fill=(254, 215, 170), width=18)
    # Heavy Worker Boots
    draw.rectangle([char_x + 30, char_y + 190, char_x + 70, char_y + 240], fill=(67, 56, 202))
    draw.rectangle([char_x + 75, char_y + 190, char_x + 115, char_y + 240], fill=(67, 56, 202))
    draw.rectangle([char_x + 20, char_y + 225, char_x + 70, char_y + 245], fill=(120, 53, 15)) # Boot
    draw.rectangle([char_x + 75, char_y + 225, char_x + 125, char_y + 245], fill=(120, 53, 15)) # Boot

    # 6. Sleek Rounded Border & Inner Bevel
    border_mask = Image.new("L", size, 0)
    bdraw = ImageDraw.Draw(border_mask)
    bdraw.rounded_rectangle([10, 10, 502, 502], radius=90, fill=255)
    
    # Outer subtle golden neon rim
    rim_img = Image.new("RGBA", size, (0,0,0,0))
    rdraw = ImageDraw.Draw(rim_img)
    rdraw.rounded_rectangle([10, 10, 502, 502], radius=90, outline=(245, 158, 11, 230), width=8)
    rdraw.rounded_rectangle([18, 18, 494, 494], radius=84, outline=(251, 191, 36, 120), width=3)

    final_img = Image.new("RGBA", size, (0, 0, 0, 0))
    final_img.paste(img, (0, 0), border_mask)
    final_img.paste(rim_img, (0, 0), rim_img)

    out_path = os.path.join(ASSETS_DIR, "store_icon_512.png")
    final_img.save(out_path, "PNG")
    art_path = os.path.join(ARTIFACTS_DIR, "store_icon_512.png")
    final_img.save(art_path, "PNG")
    print("Store icon saved to:", out_path)


# ==============================================================================
# 2. 1024x500 GOOGLE PLAY FEATURE GRAPHIC
# ==============================================================================
def render_feature_graphic():
    print("Generating 1024x500 Feature Graphic Banner...")
    size = (1024, 500)
    w, h = size
    img = Image.new("RGBA", size, (15, 23, 42, 255))
    
    # 1. Tri-Chapter Split Gradient (Terracotta Brick -> Cryo Cyan -> Cyber Purple)
    draw = ImageDraw.Draw(img)
    for x in range(w):
        t = x / float(w)
        if t < 0.35: # Chapter 1: Warm Brick
            col = (int(30 + 40 * (t/0.35)), int(20 + 20 * (t/0.35)), int(40 - 10 * (t/0.35)), 255)
        elif t < 0.70: # Chapter 2: Cold Cryo Blue
            t2 = (t - 0.35) / 0.35
            col = (int(20 - 10 * t2), int(35 + 45 * t2), int(55 + 50 * t2), 255)
        else: # Chapter 3: High-Tech Cyber Violet
            t3 = (t - 0.70) / 0.30
            col = (int(25 + 40 * t3), int(20 + 10 * t3), int(65 + 40 * t3), 255)
        draw.line([(x, 0), (x, h)], fill=col)

    # 2. Industrial Warehouse Texture & Grid Lines
    for y in range(0, h, 20):
        draw.line([(0, y), (w, y)], fill=(255, 255, 255, 12), width=1)
    for x in range(0, w, 24):
        draw.line([(x, 0), (x, h)], fill=(255, 255, 255, 10), width=1)

    # Conveyor belt floor at bottom
    draw.rectangle([0, 390, w, h], fill=(10, 15, 26, 240))
    draw.line([(0, 390), (w, 390)], fill=(245, 158, 11), width=4)
    # Conveyor hazard stripes
    for cx in range(-20, w + 40, 40):
        draw.polygon([(cx, 390), (cx + 20, 390), (cx + 5, 415), (cx - 15, 415)], fill=(245, 158, 11, 180))

    # 3. Game Title: "PIXEL PORTER"
    f_title = get_font(68, bold=True)
    f_sub = get_font(26, bold=True)
    f_badge = get_font(18, bold=True)

    title_text = "PIXEL PORTER"
    # 3D Shadow
    for offset in range(8, 0, -1):
        draw.text((70 + offset, 110 + offset), title_text, font=f_title, fill=(15, 23, 42, 220))
    # Golden Title Fill with Bevel
    draw.text((70, 110), title_text, font=f_title, fill=(251, 191, 36))
    draw.text((68, 108), title_text, font=f_title, fill=(254, 240, 138, 180))

    # Subtitle Badge
    draw.rectangle([70, 195, 460, 240], fill=(30, 41, 59, 230), outline=(245, 158, 11), width=2)
    draw.text((85, 202), "RETRO SOKOBAN PUZZLE", font=f_sub, fill=(255, 255, 255))

    # Bullet Badges
    badges = [
        ("★ 50 BRAIN LEVELS", (245, 158, 11)),
        ("❄ 3 WAREHOUSE WORLDS", (56, 189, 248)),
        ("🦺 CUSTOM UNIFORMS & SKINS", (168, 85, 247)),
        ("💡 SMART HINTS • 100% OFFLINE", (52, 211, 153))
    ]
    by = 265
    for btext, bcol in badges:
        draw.rectangle([70, by, 76, by + 20], fill=bcol)
        draw.text((88, by), btext, font=f_badge, fill=(241, 245, 249))
        by += 30

    # 4. Hero Visual: Porter & Crates on the right side
    # Crates stack
    crate_x = 680
    for cx, cy, ccol in [(crate_x + 140, 230, (217, 119, 6)), (crate_x + 40, 260, (59, 130, 246)), (crate_x + 130, 110, (168, 85, 247))]:
        draw.rectangle([cx, cy, cx + 110, cy + 110], fill=ccol, outline=(255, 255, 255, 180), width=4)
        draw.line([(cx, cy), (cx + 110, cy + 110)], fill=(0, 0, 0, 60), width=6)
        draw.line([(cx, cy + 110), (cx + 110, cy)], fill=(0, 0, 0, 60), width=6)
        draw.rectangle([cx + 12, cy + 12, cx + 98, cy + 98], outline=(255, 255, 255, 120), width=2)

    # Porter Character (Facing left/front)
    px, py = 560, 220
    # Hard Hat
    draw.ellipse([px + 20, py, px + 95, py + 45], fill=(245, 158, 11), outline=(251, 191, 36), width=3)
    draw.rectangle([px + 10, py + 30, px + 105, py + 42], fill=(217, 119, 6))
    # Head
    draw.rectangle([px + 30, py + 42, px + 85, py + 85], fill=(254, 215, 170))
    # Friendly face
    draw.rectangle([px + 45, py + 55, px + 52, py + 66], fill=(15, 23, 42))
    draw.rectangle([px + 65, py + 55, px + 72, py + 66], fill=(15, 23, 42))
    draw.arc([px + 48, py + 65, px + 68, py + 78], 0, 180, fill=(225, 29, 72), width=3)
    # Uniform
    draw.rectangle([px + 25, py + 85, px + 90, py + 160], fill=(30, 58, 138))
    # Neon Vest
    draw.rectangle([px + 25, py + 85, px + 55, py + 145], fill=(249, 115, 22))
    draw.rectangle([px + 60, py + 85, px + 90, py + 145], fill=(249, 115, 22))
    draw.line([(px + 25, py + 110), (px + 90, py + 110)], fill=(254, 240, 138), width=5)
    # Thumbs up gesture
    draw.ellipse([px - 5, py + 105, px + 25, py + 130], fill=(254, 215, 170))
    draw.rectangle([px + 5, py + 92, px + 15, py + 112], fill=(254, 215, 170)) # Thumb

    # Goal Pad underneath
    draw.ellipse([px - 10, py + 150, px + 130, py + 185], outline=(52, 211, 153), width=3)

    # 5. Play Store Frame Edge
    draw.rectangle([0, 0, w - 1, h - 1], outline=(245, 158, 11, 200), width=4)

    out_path = os.path.join(ASSETS_DIR, "feature_graphic_1024x500.png")
    img.save(out_path, "PNG")
    art_path = os.path.join(ARTIFACTS_DIR, "feature_graphic_1024x500.png")
    img.save(art_path, "PNG")
    print("Feature graphic saved to:", out_path)


# ==============================================================================
# 3. 5 ASO PROMOTIONAL SCREENSHOTS (1080x1920)
# ==============================================================================
def render_promo_screenshots():
    print("Generating 5 ASO Promotional Screenshots (1080x1920)...")
    size = (1080, 1920)
    w, h = size

    promos = [
        {
            "filename": "promo_1_levels.png",
            "title": "50 CLEVER RETRO LEVELS",
            "subtitle": "Classic Sokoban Logic • No Pressure Timers • Pure Puzzle Zen",
            "accent": (245, 158, 11),
            "screen_type": "gameplay_classic"
        },
        {
            "filename": "promo_2_chapters.png",
            "title": "3 WAREHOUSE CHAPTERS",
            "subtitle": "Brick & Mortar • Cold Storage Cryo • High-Tech Neon Depot",
            "accent": (56, 189, 248),
            "screen_type": "chapters"
        },
        {
            "filename": "promo_3_locker.png",
            "title": "THE PORTER LOCKER",
            "subtitle": "Unlock Hard Hats, Safety Vests & Heavy-Duty Container Skins",
            "accent": (168, 85, 247),
            "screen_type": "locker"
        },
        {
            "filename": "promo_4_hints.png",
            "title": "SMART HINT ECONOMY",
            "subtitle": "Never Get Deadlocked • Instant Optimal Move Suggestions",
            "accent": (234, 179, 8),
            "screen_type": "hints"
        },
        {
            "filename": "promo_5_achievements.png",
            "title": "9 WAREHOUSE ACHIEVEMENTS",
            "subtitle": "Collect 150 Stars • Real-time Toasts • 100% Offline Play",
            "accent": (16, 185, 129),
            "screen_type": "achievements"
        }
    ]

    f_title = get_font(52, bold=True)
    f_sub = get_font(25, bold=False)
    f_ui_bold = get_font(32, bold=True)
    f_ui = get_font(22, bold=False)

    for idx, p in enumerate(promos):
        img = Image.new("RGBA", size, (10, 15, 28, 255))
        draw = ImageDraw.Draw(img)

        # 1. Background Grid & Radiant Gradient
        bg = create_radial_gradient(size, (25, 35, 55, 255), (8, 12, 22, 255))
        img.paste(bg, (0, 0))
        draw = ImageDraw.Draw(img)

        # 2. Top ASO Header Banner (High-Contrast for Play Store Glanceability)
        draw.rectangle([0, 0, w, 220], fill=(15, 23, 42, 240))
        draw.line([(0, 220), (w, 220)], fill=p["accent"], width=6)
        
        # Pill Category Tag
        pill_text = "OFFICIAL GOOGLE PLAY RELEASE"
        draw.rectangle([w//2 - 200, 30, w//2 + 200, 68], fill=p["accent"])
        f_pill = get_font(18, bold=True)
        draw.text((w//2 - 170, 38), pill_text, font=f_pill, fill=(15, 23, 42))

        # Main Title & Subtitle
        title_bbox = draw.textbbox((0, 0), p["title"], font=f_title)
        tw = title_bbox[2] - title_bbox[0]
        draw.text(((w - tw) // 2, 85), p["title"], font=f_title, fill=(255, 255, 255))

        sub_bbox = draw.textbbox((0, 0), p["subtitle"], font=f_sub)
        sw = sub_bbox[2] - sub_bbox[0]
        draw.text(((w - sw) // 2, 160), p["subtitle"], font=f_sub, fill=(148, 163, 184))

        # 3. Modern Smartphone Mockup Frame
        phone_x, phone_y = 110, 260
        phone_w, phone_h = 860, 1580
        # Shadow
        phone_shadow = Image.new("RGBA", size, (0,0,0,0))
        psdraw = ImageDraw.Draw(phone_shadow)
        psdraw.rounded_rectangle([phone_x - 10, phone_y - 5, phone_x + phone_w + 10, phone_y + phone_h + 15], radius=50, fill=(0, 0, 0, 160))
        phone_shadow = phone_shadow.filter(ImageFilter.GaussianBlur(25))
        img.paste(phone_shadow, (0, 0), phone_shadow)

        # Device Bezel
        draw.rounded_rectangle([phone_x, phone_y, phone_x + phone_w, phone_y + phone_h], radius=44, fill=(15, 23, 42), outline=(51, 65, 85), width=8)
        
        # Inner Screen Display
        screen_x, screen_y = phone_x + 16, phone_y + 16
        screen_w, screen_h = phone_w - 32, phone_h - 32
        draw.rounded_rectangle([screen_x, screen_y, screen_x + screen_w, screen_y + screen_h], radius=32, fill=(24, 32, 47))

        # Camera Punch Hole
        draw.ellipse([w//2 - 10, screen_y + 14, w//2 + 10, screen_y + 34], fill=(10, 15, 25))

        # 4. In-Screen UI Content Based on Screen Type
        if p["screen_type"] == "gameplay_classic":
            # Header Bar
            draw.rectangle([screen_x, screen_y + 50, screen_x + screen_w, screen_y + 150], fill=(30, 41, 59))
            draw.text((screen_x + 30, screen_y + 70), "LEVEL 08", font=f_ui_bold, fill=(255, 255, 255))
            draw.text((screen_x + 30, screen_y + 115), "Chapter 1: Brick & Mortar", font=f_ui, fill=(245, 158, 11))
            draw.text((screen_x + screen_w - 240, screen_y + 70), "MOVES: 14", font=f_ui_bold, fill=(148, 163, 184))
            draw.text((screen_x + screen_w - 240, screen_y + 115), "PUSHES: 3", font=f_ui, fill=(148, 163, 184))

            # Game Grid (10x8 warehouse)
            grid_ox = screen_x + 70
            grid_oy = screen_y + 240
            cell_s = 68
            for r in range(12):
                for c in range(10):
                    cx, cy = grid_ox + c * cell_s, grid_oy + r * cell_s
                    # Floor
                    draw.rectangle([cx, cy, cx + cell_s - 2, cy + cell_s - 2], fill=(35, 45, 65))
                    # Wall borders
                    if r == 0 or r == 11 or c == 0 or c == 9 or (r in [3, 4] and c == 4):
                        draw.rectangle([cx, cy, cx + cell_s - 2, cy + cell_s - 2], fill=(180, 83, 9), outline=(120, 53, 15), width=2)
            
            # Goal Pads
            for gr, gc in [(4, 7), (5, 7), (6, 7)]:
                gx, gy = grid_ox + gc * cell_s, grid_oy + gr * cell_s
                draw.rectangle([gx + 6, gy + 6, gx + cell_s - 8, gy + cell_s - 8], fill=(16, 185, 129, 160), outline=(52, 211, 153), width=3)
            
            # Crates
            for cr, cc, ctype in [(4, 7, "goal"), (5, 5, "normal"), (7, 4, "normal")]:
                cx, cy = grid_ox + cc * cell_s, grid_oy + cr * cell_s
                ccol = (16, 185, 129) if ctype == "goal" else (217, 119, 6)
                draw.rectangle([cx + 4, cy + 4, cx + cell_s - 6, cy + cell_s - 6], fill=ccol, outline=(255, 255, 255, 200), width=3)
                draw.line([(cx+4, cy+4), (cx+cell_s-6, cy+cell_s-6)], fill=(0,0,0,60), width=3)
                draw.line([(cx+4, cy+cell_s-6), (cx+cell_s-6, cy+4)], fill=(0,0,0,60), width=3)

            # Player
            pr, pc = 7, 3
            px, py = grid_ox + pc * cell_s, grid_oy + pr * cell_s
            draw.ellipse([px + 10, py + 8, px + cell_s - 10, py + cell_s - 25], fill=(245, 158, 11))
            draw.rectangle([px + 14, py + cell_s - 30, px + cell_s - 14, py + cell_s - 8], fill=(30, 58, 138))

            # Bottom Controls Overlay
            by = screen_y + screen_h - 220
            draw.rectangle([screen_x, by, screen_x + screen_w, screen_y + screen_h], fill=(15, 23, 42))
            draw.rounded_rectangle([screen_x + 40, by + 40, screen_x + 240, by + 120], radius=16, fill=(51, 65, 85))
            draw.text((screen_x + 85, by + 65), "↩ UNDO", font=f_ui_bold, fill=(255, 255, 255))
            draw.rounded_rectangle([screen_x + 280, by + 40, screen_x + 520, by + 120], radius=16, fill=(51, 65, 85))
            draw.text((screen_x + 320, by + 65), "💡 HINT (3)", font=f_ui_bold, fill=(250, 204, 21))
            draw.rounded_rectangle([screen_x + 560, by + 40, screen_x + 780, by + 120], radius=16, fill=(51, 65, 85))
            draw.text((screen_x + 610, by + 65), "↺ RESET", font=f_ui_bold, fill=(248, 113, 113))

        elif p["screen_type"] == "chapters":
            # 3 Chapter Showcase Panels
            cy = screen_y + 80
            chapters = [
                ("CHAPTER 1: BRICK & MORTAR", "Levels 1–15 • Warm Industrial Depot", (217, 119, 6), "★★★ 45/45 Stars"),
                ("CHAPTER 2: COLD STORAGE", "Levels 16–35 • Cryo Ice & Frozen Steel", (14, 165, 233), "★★★ 52/60 Stars"),
                ("CHAPTER 3: HIGH-TECH DEPOT", "Levels 36–50 • Neon Conveyors & Robotics", (168, 85, 247), "★★★ 38/45 Stars")
            ]
            for ctitle, cdesc, ccol, cstars in chapters:
                draw.rounded_rectangle([screen_x + 30, cy, screen_x + screen_w - 30, cy + 380], radius=24, fill=(30, 41, 59), outline=ccol, width=4)
                draw.rectangle([screen_x + 30, cy, screen_x + screen_w - 30, cy + 60], fill=ccol)
                draw.text((screen_x + 50, cy + 15), ctitle, font=f_ui_bold, fill=(255, 255, 255))
                draw.text((screen_x + 50, cy + 85), cdesc, font=f_ui, fill=(203, 213, 225))
                draw.text((screen_x + 50, cy + 125), cstars, font=f_ui_bold, fill=(250, 204, 21))

                # Mini level buttons row
                for bidx in range(6):
                    bx = screen_x + 50 + bidx * 115
                    by = cy + 180
                    draw.rounded_rectangle([bx, by, bx + 95, by + 100], radius=12, fill=(15, 23, 42), outline=ccol, width=2)
                    draw.text((bx + 35, by + 20), str(bidx + 1), font=f_ui_bold, fill=(255, 255, 255))
                    draw.text((bx + 20, by + 60), "★★★", font=get_font(16, bold=True), fill=(250, 204, 21))

                cy += 430

        elif p["screen_type"] == "locker":
            # The Porter Locker Modal Showcase
            draw.rectangle([screen_x, screen_y + 60, screen_x + screen_w, screen_y + 160], fill=(30, 41, 59))
            draw.text((screen_x + 40, screen_y + 75), "🦺 THE PORTER LOCKER", font=f_ui_bold, fill=(250, 204, 21))
            draw.text((screen_x + 40, screen_y + 120), "★ 78 / 150 Stars Collected", font=f_ui, fill=(148, 163, 184))

            # Tab Buttons
            draw.rounded_rectangle([screen_x + 40, screen_y + 180, screen_x + 380, screen_y + 240], radius=12, fill=(245, 158, 11))
            draw.text((screen_x + 130, screen_y + 195), "👕 OUTFITS", font=f_ui_bold, fill=(15, 23, 42))
            draw.rounded_rectangle([screen_x + 420, screen_y + 180, screen_x + 760, screen_y + 240], radius=12, fill=(51, 65, 85))
            draw.text((screen_x + 520, screen_y + 195), "📦 CRATES", font=f_ui_bold, fill=(255, 255, 255))

            # Cosmetics List
            ly = screen_y + 270
            items = [
                ("🧢", "Classic Blue Porter", "Default standard blue dungarees", "EQUIPPED", True, (34, 197, 94)),
                ("🦺", "Hi-Vis Safety Vest", "Neon reflective construction vest", "EQUIP", False, (245, 158, 11)),
                ("🧥", "Cryo Parka", "Heavy winter insulated jacket", "★ 60 Stars required", False, (148, 163, 184)),
                ("🤖", "Cyber Exosuit", "Advanced pneumatic warehouse frame", "★ 100 Stars required", False, (148, 163, 184)),
            ]
            for icon, iname, idesc, status, is_eq, scol in items:
                draw.rounded_rectangle([screen_x + 40, ly, screen_x + screen_w - 40, ly + 180], radius=16, fill=(30, 41, 59), outline=(51, 65, 85), width=2)
                draw.text((screen_x + 70, ly + 40), icon, font=get_font(48, bold=True), fill=(255, 255, 255))
                draw.text((screen_x + 160, ly + 35), iname, font=f_ui_bold, fill=(250, 204, 21) if is_eq else (255, 255, 255))
                draw.text((screen_x + 160, ly + 80), idesc, font=f_ui, fill=(148, 163, 184))
                # Action button
                draw.rounded_rectangle([screen_x + screen_w - 260, ly + 45, screen_x + screen_w - 70, ly + 115], radius=12, fill=scol)
                draw.text((screen_x + screen_w - 240, ly + 65), status, font=get_font(18, bold=True), fill=(15, 23, 42) if is_eq or status=="EQUIP" else (255,255,255))
                ly += 220

        elif p["screen_type"] == "hints":
            # Smart Hint Economy & Modal
            draw.rectangle([screen_x, screen_y + 50, screen_x + screen_w, screen_y + 150], fill=(30, 41, 59))
            draw.text((screen_x + 40, screen_y + 80), "STUCK ON A TRICKY LEVEL?", font=f_ui_bold, fill=(250, 204, 21))
            draw.text((screen_x + 40, screen_y + 120), "Smart A* Solver Guides Every Move", font=f_ui, fill=(148, 163, 184))

            # Rewarded Modal Dialog Mockup
            my = screen_y + 280
            draw.rounded_rectangle([screen_x + 50, my, screen_x + screen_w - 50, my + 640], radius=28, fill=(15, 23, 42), outline=(245, 158, 11), width=6)
            draw.text((screen_x + 180, my + 60), "💡 NEED A HINT? 💡", font=f_ui_bold, fill=(250, 204, 21))
            draw.text((screen_x + 120, my + 140), "Watch a brief sponsor clip to receive", font=f_ui, fill=(203, 213, 225))
            draw.text((screen_x + 180, my + 185), "+3 HINTS immediately!", font=f_ui_bold, fill=(52, 211, 153))

            # Reward Visual Icon
            draw.rectangle([screen_x + 280, my + 260, screen_x + screen_w - 280, my + 410], fill=(30, 41, 59), outline=(52, 211, 153), width=3)
            draw.text((screen_x + 320, my + 300), "🎁 +3 HINTS", font=f_ui_bold, fill=(250, 204, 21))

            # Buttons
            draw.rounded_rectangle([screen_x + 100, my + 460, screen_x + screen_w - 100, my + 540], radius=16, fill=(34, 197, 94))
            draw.text((screen_x + 180, my + 485), "▶ WATCH AD (+3 HINTS)", font=f_ui_bold, fill=(15, 23, 42))

            draw.rounded_rectangle([screen_x + 220, my + 560, screen_x + screen_w - 220, my + 615], radius=12, fill=(51, 65, 85))
            draw.text((screen_x + 320, my + 575), "NO THANKS", font=f_ui, fill=(255, 255, 255))

            # Bottom Feature Pills
            fy = my + 720
            draw.rounded_rectangle([screen_x + 50, fy, screen_x + screen_w - 50, fy + 240], radius=20, fill=(30, 41, 59))
            draw.text((screen_x + 80, fy + 30), "✔ 100% NON-INTRUSIVE MONETIZATION", font=f_ui_bold, fill=(52, 211, 153))
            draw.text((screen_x + 80, fy + 80), "✔ ZERO FORCED POPUP ADS DURING GAMEPLAY", font=f_ui_bold, fill=(52, 211, 153))
            draw.text((screen_x + 80, fy + 130), "✔ HINTS ONLY CONSUMED ON SOLVABLE BOARDS", font=f_ui_bold, fill=(52, 211, 153))
            draw.text((screen_x + 80, fy + 180), "✔ FULL OFFLINE ENJOYMENT ANYTIME", font=f_ui_bold, fill=(52, 211, 153))

        elif p["screen_type"] == "achievements":
            # Achievements Modal Showcase
            draw.rectangle([screen_x, screen_y + 50, screen_x + screen_w, screen_y + 150], fill=(30, 41, 59))
            draw.text((screen_x + 40, screen_y + 70), "🏆 WAREHOUSE ACHIEVEMENTS", font=f_ui_bold, fill=(250, 204, 21))
            draw.text((screen_x + 40, screen_y + 115), "🏆 6 / 9 Unlocked • Google Play Games Ready", font=f_ui, fill=(52, 211, 153))

            # Achievements Cards
            ay = screen_y + 180
            achievements_mock = [
                ("🏁", "First Shift", "Complete Level 1 in the warehouse", True),
                ("📦", "Cargo Master", "Complete Chapter 1: Brick & Mortar", True),
                ("❄", "Cold Storage", "Complete Chapter 2: Cold Storage", True),
                ("⭐", "Precision Starter", "Earn 3 stars on any 5 levels", True),
                ("🌟", "Precision Master", "Earn 3 stars on any 25 levels", True),
                ("🦺", "Stylin' Porter", "Equip any cosmetic skin from the Locker", True),
                ("⚙", "High-Tech Depot", "Complete all 50 warehouse levels", False),
            ]
            for aicon, atitle, adesc, aunlocked in achievements_mock:
                acol = (30, 41, 59)
                outline_col = (245, 158, 11) if aunlocked else (51, 65, 85)
                draw.rounded_rectangle([screen_x + 40, ay, screen_x + screen_w - 40, ay + 140], radius=16, fill=acol, outline=outline_col, width=2)
                draw.text((screen_x + 65, ay + 35), aicon if aunlocked else "🔒", font=get_font(38, bold=True), fill=(255, 255, 255))
                draw.text((screen_x + 140, ay + 25), atitle, font=f_ui_bold, fill=(250, 204, 21) if aunlocked else (148, 163, 184))
                draw.text((screen_x + 140, ay + 75), adesc, font=f_ui, fill=(203, 213, 225) if aunlocked else (100, 116, 139))
                # Checkmark or lock
                badge_text = "✓ UNLOCKED" if aunlocked else "LOCKED"
                badge_col = (34, 197, 94) if aunlocked else (100, 116, 139)
                draw.text((screen_x + screen_w - 220, ay + 45), badge_text, font=get_font(18, bold=True), fill=badge_col)
                ay += 175

        # Save promo image
        out_path = os.path.join(ASSETS_DIR, p["filename"])
        img.save(out_path, "PNG")
        art_path = os.path.join(ARTIFACTS_DIR, p["filename"])
        img.save(art_path, "PNG")
        print(f"Promo screenshot {idx+1}/5 saved to: {out_path}")

    print("All promotional screenshots rendered successfully!")


if __name__ == "__main__":
    render_store_icon()
    render_feature_graphic()
    render_promo_screenshots()
    print("\nDONE: All Play Store ASO visual marketing assets rendered!")

#!/usr/bin/env python3
"""
tools/render_loading_preview.py

Generates an accurate visual render of the minimal modern loading screen:
- Just one sleek, modern progress bar with matching rounded corners
- Ambient gold/amber status text with live percentage readout
- Clean minimal prompt
- No bulky card background or double borders
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ARTIFACT_DIR = "/home/snowz/.gemini/antigravity-ide/brain/585b805d-dc89-49ec-9d75-7dca930224d1"
SPLASH_IMG = "/home/snowz/godot/assets/splash.png"


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


def render_preview():
    base = Image.open(SPLASH_IMG).convert("RGBA")
    w, h = base.size  # 540x960

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Margin container bounds (anchors_preset 12, offset_top = -120 -> y=840..932)
    # margin_left = 48, margin_right = 48 -> x = 48..492 (width = 444)
    bar_x0 = 48
    bar_x1 = 492
    bar_w = bar_x1 - bar_x0  # 444

    # 1. StatusLabel
    f_status = get_font(12, bold=True)
    status_text = "LOADING 50 SOKOBAN LEVELS... 68%"
    s_bbox = f_status.getbbox(status_text)
    sw = s_bbox[2] - s_bbox[0]
    sx = (w - sw) // 2
    sy = 848

    # Soft shadow
    draw.text((sx, sy + 1), status_text, font=f_status, fill=(0, 0, 0, 240))
    # Warm gold lettering
    draw.text((sx, sy), status_text, font=f_status, fill=(245, 209, 89, 255))

    # 2. LoadingBar (Sleek, minimal, 10px high)
    bar_y0 = 872
    bar_h = 10
    bar_y1 = bar_y0 + bar_h
    bar_r = 5

    # Soft ambient glow behind the bar
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.rounded_rectangle([bar_x0 - 2, bar_y0 - 2, bar_x1 + 2, bar_y1 + 2], radius=bar_r + 2, fill=(245, 173, 35, 30))
    glow = glow.filter(ImageFilter.GaussianBlur(4))
    base.paste(glow, (0, 0), glow)

    # Groove background: deep translucent slate/obsidian with fine brass hairline outline
    draw.rounded_rectangle([bar_x0, bar_y0, bar_x1, bar_y1], radius=bar_r, fill=(10, 15, 26, 215))
    draw.rounded_rectangle([bar_x0, bar_y0, bar_x1, bar_y1], radius=bar_r, outline=(184, 138, 51, 165), width=1)

    # Progress fill (68%)
    progress_ratio = 0.68
    fill_w = max(int(bar_w * progress_ratio), 10)
    fill_x1 = bar_x0 + fill_w
    fill_r = 4

    # Vibrant clean golden fill
    draw.rounded_rectangle([bar_x0, bar_y0, fill_x1, bar_y1], radius=fill_r, fill=(245, 173, 35, 255))
    # Subtle top specular line
    draw.line([(bar_x0 + fill_r, bar_y0 + 1), (fill_x1 - fill_r, bar_y0 + 1)], fill=(255, 235, 160, 230), width=1)

    # 3. PromptLabel
    f_prompt = get_font(11, bold=False)
    prompt_text = "TAP ANYWHERE TO START"
    p_bbox = f_prompt.getbbox(prompt_text)
    pw = p_bbox[2] - p_bbox[0]
    px = (w - pw) // 2
    py = 894

    # Soft shadow & slate-blue text
    draw.text((px, py + 1), prompt_text, font=f_prompt, fill=(0, 0, 0, 220))
    draw.text((px, py), prompt_text, font=f_prompt, fill=(179, 199, 224, 190))

    base.paste(overlay, (0, 0), overlay)

    out_path = os.path.join(ARTIFACT_DIR, "loading_screen_minimal_preview.png")
    base.save(out_path, "PNG")
    print("Minimal modern loading screen preview saved to:", out_path)


if __name__ == "__main__":
    render_preview()

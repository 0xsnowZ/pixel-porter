#!/usr/bin/env python3
"""
tools/update_branding_assets.py

Processes the newly generated Pixel Sokoban: Warehouse Rush visual assets:
1. assets/logo.png (Transparent RGBA high-res emblem)
2. assets/splash.png (540x960 exact portrait splash/boot image)
3. icon.png & assets/store_icon_512.png (512x512 app icon)
4. assets/icon_192.png (192x192 app icon)
5. assets/adaptive_foreground_432.png & assets/adaptive_background_432.png (432x432 adaptive icons)
6. assets/feature_graphic_1024x500.png (1024x500 Google Play Store banner)
"""

import os
from PIL import Image, ImageFilter, ImageDraw

ARTIFACT_DIR = "/home/snowz/.gemini/antigravity-ide/brain/585b805d-dc89-49ec-9d75-7dca930224d1"
ASSETS_DIR = "/home/snowz/godot/assets"
ROOT_DIR = "/home/snowz/godot"

LOGO_SRC = os.path.join(ARTIFACT_DIR, "pixel_sokoban_logo_1792867902897.jpg")
SPLASH_SRC = os.path.join(ARTIFACT_DIR, "pixel_sokoban_splash_1792867925090.jpg")
BANNER_SRC = os.path.join(ARTIFACT_DIR, "pixel_sokoban_banner_1792867949961.jpg")


def make_transparent_logo():
    print("Processing transparent logo...")
    img = Image.open(LOGO_SRC).convert("RGBA")
    w, h = img.size

    # Flood fill from corners to find background mask
    # A pixel is considered background if it's connected to border and dark
    import numpy as np
    from collections import deque

    arr = np.array(img)
    # Brightness metric
    rgb = arr[:, :, :3]
    brightness = np.max(rgb, axis=2)

    # BFS from boundaries to mark background
    visited = np.zeros((h, w), dtype=bool)
    q = deque()

    # Add all edge pixels
    for x in range(w):
        if brightness[0, x] < 25:
            q.append((0, x))
            visited[0, x] = True
        if brightness[h - 1, x] < 25:
            q.append((h - 1, x))
            visited[h - 1, x] = True

    for y in range(h):
        if brightness[y, 0] < 25:
            q.append((y, 0))
            visited[y, 0] = True
        if brightness[y, w - 1] < 25:
            q.append((y, w - 1))
            visited[y, w - 1] = True

    while q:
        cy, cx = q.popleft()
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                if brightness[ny, nx] < 25:
                    visited[ny, nx] = True
                    q.append((ny, nx))

    # Set alpha
    alpha = arr[:, :, 3].copy()
    alpha[visited] = 0

    # Soft edge feathering near transition
    out_arr = arr.copy()
    out_arr[:, :, 3] = alpha
    logo_rgba = Image.fromarray(out_arr, mode="RGBA")

    # Crop to non-transparent bounding box with some padding
    bbox = logo_rgba.getbbox()
    if bbox:
        pad = 20
        x0 = max(0, bbox[0] - pad)
        y0 = max(0, bbox[1] - pad)
        x1 = min(w, bbox[2] + pad)
        y1 = min(h, bbox[3] + pad)
        logo_cropped = logo_rgba.crop((x0, y0, x1, y1))
    else:
        logo_cropped = logo_rgba

    # Save to assets/logo.png
    out_logo = os.path.join(ASSETS_DIR, "logo.png")
    logo_cropped.save(out_logo, "PNG")
    print(f"Saved {out_logo} ({logo_cropped.size})")
    return logo_cropped


def process_splash():
    print("Processing splash screen...")
    img = Image.open(SPLASH_SRC).convert("RGB")
    target_w, target_h = 540, 960

    # Resize to fit 540x960 cleanly with lanczos
    splash = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    out_splash = os.path.join(ASSETS_DIR, "splash.png")
    splash.save(out_splash, "PNG")
    print(f"Saved {out_splash} ({splash.size})")


def process_banner():
    print("Processing feature graphic banner...")
    img = Image.open(BANNER_SRC).convert("RGB")
    target_w, target_h = 1024, 500

    src_w, src_h = img.size
    scale = max(target_w / float(src_w), target_h / float(src_h))
    new_w = int(src_w * scale)
    new_h = int(src_h * scale)

    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    cropped = resized.crop((left, top, left + target_w, top + target_h))

    out_banner = os.path.join(ASSETS_DIR, "feature_graphic_1024x500.png")
    cropped.save(out_banner, "PNG")
    print(f"Saved {out_banner} ({cropped.size})")


def process_icons(logo_img):
    print("Processing app icons and adaptive icons...")
    # 512x512 Store icon & root icon.png
    # Create a handsome dark navy / slate backdrop with radial amber glow
    size = (512, 512)
    bg = Image.new("RGBA", size, (12, 17, 28, 255))
    draw = ImageDraw.Draw(bg)

    # Radial ambient glow in center
    for r in range(240, 40, -10):
        alpha = int(25 * (1.0 - (r / 240.0)))
        draw.ellipse([256 - r, 256 - r, 256 + r, 256 + r], fill=(245, 158, 11, alpha))

    # Scale logo to fit nicely in 420x420 center
    logo_fit = logo_img.copy()
    logo_fit.thumbnail((420, 420), Image.Resampling.LANCZOS)

    lw, lh = logo_fit.size
    pos = ((512 - lw) // 2, (512 - lh) // 2)

    # Drop shadow behind logo
    shadow = Image.new("RGBA", size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rectangle([pos[0] + 5, pos[1] + 10, pos[0] + lw - 5, pos[1] + lh + 5], fill=(0, 0, 0, 160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    bg.paste(shadow, (0, 0), shadow)

    # Paste logo
    bg.paste(logo_fit, pos, logo_fit)

    # 1. assets/store_icon_512.png & icon.png
    out_store = os.path.join(ASSETS_DIR, "store_icon_512.png")
    out_root_icon = os.path.join(ROOT_DIR, "icon.png")
    icon_512_rgb = bg.convert("RGB")
    icon_512_rgb.save(out_store, "PNG")
    icon_512_rgb.save(out_root_icon, "PNG")
    print("Saved store_icon_512.png and icon.png")

    # 2. assets/icon_192.png
    icon_192 = bg.resize((192, 192), Image.Resampling.LANCZOS).convert("RGB")
    out_192 = os.path.join(ASSETS_DIR, "icon_192.png")
    icon_192.save(out_192, "PNG")
    print("Saved icon_192.png")

    # 3. Adaptive icons (432x432)
    # Background: clean navy slate with radial glow
    bg_432 = Image.new("RGB", (432, 432), (15, 23, 42))
    bdraw = ImageDraw.Draw(bg_432)
    for r in range(200, 30, -10):
        bdraw.ellipse([216 - r, 216 - r, 216 + r, 216 + r], fill=(24 + int(r/10), 32 + int(r/8), 50 + int(r/6)))
    out_ad_bg = os.path.join(ASSETS_DIR, "adaptive_background_432.png")
    bg_432.save(out_ad_bg, "PNG")

    # Foreground: 432x432 with transparent margins, logo safe-centered within 260x260
    fg_432 = Image.new("RGBA", (432, 432), (0, 0, 0, 0))
    fg_logo = logo_img.copy()
    fg_logo.thumbnail((280, 280), Image.Resampling.LANCZOS)
    flw, flh = fg_logo.size
    fpos = ((432 - flw) // 2, (432 - flh) // 2)
    fg_432.paste(fg_logo, fpos, fg_logo)
    out_ad_fg = os.path.join(ASSETS_DIR, "adaptive_foreground_432.png")
    fg_432.save(out_ad_fg, "PNG")
    print("Saved adaptive_background_432.png and adaptive_foreground_432.png")


if __name__ == "__main__":
    logo = make_transparent_logo()
    process_splash()
    process_banner()
    process_icons(logo)
    print("\nAll Pixel Sokoban: Warehouse Rush assets processed successfully!")

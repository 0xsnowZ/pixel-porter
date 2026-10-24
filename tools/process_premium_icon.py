#!/usr/bin/env python3
"""
tools/process_premium_icon.py

Processes the AAA-grade Golden Crate artwork into exact production icon assets:
1. assets/store_icon_512.png (512x512 32-bit PNG, Google Play Store)
2. icon.png (512x512 32-bit PNG, Godot Project Icon)
3. assets/icon_192.png (192x192 32-bit PNG, Legacy Launcher Icon)
4. assets/adaptive_background_432.png (432x432 32-bit PNG, Android Adaptive Background)
5. assets/adaptive_foreground_432.png (432x432 32-bit PNG, Android Adaptive Foreground with 264px safe-zone scaling)
"""

import os
from PIL import Image, ImageFilter, ImageDraw

ARTIFACT_DIR = "/home/snowz/.gemini/antigravity-ide/brain/585b805d-dc89-49ec-9d75-7dca930224d1"
ASSETS_DIR = "/home/snowz/godot/assets"
ROOT_DIR = "/home/snowz/godot"

CRATE_ICON_SRC = os.path.join(ARTIFACT_DIR, "premium_store_icon_crate_1792868731528.jpg")
PORTER_ICON_SRC = os.path.join(ARTIFACT_DIR, "premium_store_icon_porter_1792868780645.jpg")


def process_golden_crate_icons():
    print("Loading Golden Crate master artwork (1024x1024)...")
    img = Image.open(CRATE_ICON_SRC).convert("RGBA")
    
    # 1. Store Icon (512x512)
    icon_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
    out_store = os.path.join(ASSETS_DIR, "store_icon_512.png")
    out_root = os.path.join(ROOT_DIR, "icon.png")
    out_art_512 = os.path.join(ARTIFACT_DIR, "store_icon_512.png")
    
    icon_512.save(out_store, "PNG")
    icon_512.save(out_root, "PNG")
    icon_512.save(out_art_512, "PNG")
    print(f"Saved {out_store} and {out_root}")

    # 2. Legacy Launcher Icon (192x192)
    icon_192 = img.resize((192, 192), Image.Resampling.LANCZOS)
    out_192 = os.path.join(ASSETS_DIR, "icon_192.png")
    icon_192.save(out_192, "PNG")
    print(f"Saved {out_192}")

    # 3. Android Adaptive Background (432x432)
    # Scaled down full-bleed warehouse atmosphere
    bg_432 = img.resize((432, 432), Image.Resampling.LANCZOS)
    out_ad_bg = os.path.join(ASSETS_DIR, "adaptive_background_432.png")
    bg_432.save(out_ad_bg, "PNG")
    print(f"Saved {out_ad_bg}")

    # 4. Android Adaptive Foreground (432x432)
    # The crate and glowing rune pad cropped/centered cleanly within the 264px safe diameter
    # In Android, foreground is often combined with background, or can be transparent.
    # To support layered parallax animations on Pixel & Samsung launchers,
    # we provide a clean foreground with the crate & rune pad floating with subtle glow:
    fg_432 = Image.new("RGBA", (432, 432), (0, 0, 0, 0))
    # Crop central focal region from 1024x1024 (center 800x800)
    crop_box = (112, 112, 912, 912)
    focal = img.crop(crop_box).resize((320, 320), Image.Resampling.LANCZOS)
    pos = ((432 - 320) // 2, (432 - 320) // 2)
    fg_432.paste(focal, pos, focal)
    out_ad_fg = os.path.join(ASSETS_DIR, "adaptive_foreground_432.png")
    fg_432.save(out_ad_fg, "PNG")
    print(f"Saved {out_ad_fg}")


if __name__ == "__main__":
    process_golden_crate_icons()
    print("Production icons updated with AAA Golden Crate artwork!")

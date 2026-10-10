#!/usr/bin/env python3
"""
tools/process_hq_assets.py

Processes the generated AAA-quality visual assets into exact Google Play Store specifications:
1. assets/store_icon_512.png (512x512 32-bit PNG)
2. assets/icon_192.png (192x192 Godot app icon)
3. assets/feature_graphic_1024x500.png (1024x500 24-bit PNG, Google Play exact specs)
4. assets/promo_1_levels.png (1080x1920 24-bit PNG)
5. assets/promo_2_chapters.png (1080x1920 24-bit PNG)
6. assets/promo_3_locker.png (1080x1920 24-bit PNG)
7. assets/promo_4_hints.png (1080x1920 24-bit PNG)
8. assets/promo_5_achievements.png (1080x1920 24-bit PNG)

Also updates artifact copies directly in the IDE artifacts directory.
"""

import os
from PIL import Image

ARTIFACTS_DIR = "/home/snowz/.gemini/antigravity-ide/brain/9a93013c-7615-47d7-ae14-3f8a6be1d265"
ASSETS_DIR = "/home/snowz/godot/assets"

RAW_ICON = os.path.join(ARTIFACTS_DIR, "store_icon_hq_1791658679958.jpg")
RAW_BANNER = os.path.join(ARTIFACTS_DIR, "feature_graphic_hq_1791658698669.jpg")
RAW_PROMO_GAMEPLAY = os.path.join(ARTIFACTS_DIR, "promo_gameplay_hq_1791658733386.jpg")
RAW_PROMO_LOCKER = os.path.join(ARTIFACTS_DIR, "promo_locker_hq_1791658752448.jpg")
RAW_PROMO_HINTS = os.path.join(ARTIFACTS_DIR, "promo_hints_hq_1791658777764.jpg")


def process_icon():
    print("Processing 512x512 Store Icon...")
    img = Image.open(RAW_ICON).convert("RGBA")
    icon_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
    
    out_512 = os.path.join(ASSETS_DIR, "store_icon_512.png")
    art_512 = os.path.join(ARTIFACTS_DIR, "store_icon_512.png")
    icon_512.save(out_512, "PNG")
    icon_512.save(art_512, "PNG")
    print("Saved store_icon_512.png:", out_512)

    icon_192 = img.resize((192, 192), Image.Resampling.LANCZOS)
    out_192 = os.path.join(ASSETS_DIR, "icon_192.png")
    icon_192.save(out_192, "PNG")
    print("Saved icon_192.png:", out_192)


def process_feature_graphic():
    print("Processing 1024x500 Feature Graphic...")
    img = Image.open(RAW_BANNER).convert("RGB")
    # Original is 1376x768. Target is 1024x500 (aspect ratio ~2.048 vs 1.792)
    # We fit by width, center crop height to 500 equivalent
    target_w, target_h = 1024, 500
    src_w, src_h = img.size
    
    # Calculate scale factor to cover target
    scale = max(target_w / float(src_w), target_h / float(src_h))
    new_w = int(src_w * scale)
    new_h = int(src_h * scale)
    
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Center crop
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    cropped = resized.crop((left, top, left + target_w, top + target_h))
    
    out_path = os.path.join(ASSETS_DIR, "feature_graphic_1024x500.png")
    art_path = os.path.join(ARTIFACTS_DIR, "feature_graphic_1024x500.png")
    cropped.save(out_path, "PNG")
    cropped.save(art_path, "PNG")
    print("Saved feature_graphic_1024x500.png:", out_path)


def process_promos():
    print("Processing 1080x1920 Promotional Screenshots...")
    target_w, target_h = 1080, 1920
    
    # Promo 1: Gameplay
    p1 = Image.open(RAW_PROMO_GAMEPLAY).convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)
    p1.save(os.path.join(ASSETS_DIR, "promo_1_levels.png"), "PNG")
    p1.save(os.path.join(ARTIFACTS_DIR, "promo_1_levels.png"), "PNG")

    # Promo 2: Chapters (re-framed from gameplay/feature graphic blend)
    p2 = Image.open(RAW_PROMO_GAMEPLAY).convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)
    p2.save(os.path.join(ASSETS_DIR, "promo_2_chapters.png"), "PNG")
    p2.save(os.path.join(ARTIFACTS_DIR, "promo_2_chapters.png"), "PNG")

    # Promo 3: Locker & Custom Skins
    p3 = Image.open(RAW_PROMO_LOCKER).convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)
    p3.save(os.path.join(ASSETS_DIR, "promo_3_locker.png"), "PNG")
    p3.save(os.path.join(ARTIFACTS_DIR, "promo_3_locker.png"), "PNG")

    # Promo 4: Hints & Solver
    p4 = Image.open(RAW_PROMO_HINTS).convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)
    p4.save(os.path.join(ASSETS_DIR, "promo_4_hints.png"), "PNG")
    p4.save(os.path.join(ARTIFACTS_DIR, "promo_4_hints.png"), "PNG")

    # Promo 5: Achievements & 100% Offline
    p5 = Image.open(RAW_PROMO_HINTS).convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)
    p5.save(os.path.join(ASSETS_DIR, "promo_5_achievements.png"), "PNG")
    p5.save(os.path.join(ARTIFACTS_DIR, "promo_5_achievements.png"), "PNG")
    print("Saved all 5 promotional screenshots!")


if __name__ == "__main__":
    process_icon()
    process_feature_graphic()
    process_promos()
    print("All enhanced store assets processed successfully!")

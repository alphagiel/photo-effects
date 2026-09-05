#!/usr/bin/env python3
"""
gif_maker.py - apply a photo effect and export as an animated GIF (or a static frame).

Usage:
    python3 gif_maker.py <input_image> [output_file] [--static] [--effect coin-shine]

Effects live one-per-file under effects/ and are collected into effects.EFFECTS.
"""

import sys
import os
import re
from PIL import Image

from effects import EFFECTS, FRAMES

FRAME_DURATION_MS = 45
STATIC_SIZE = 512   # single-frame PNG, no size pressure
GIF_SIZE = 384      # animated GIF: kept smaller to hit the file-size target below
GIF_COLORS = 64     # shared palette size for the GIF's color table
GIF_MAX_BYTES = 1_000_000

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_ROOT = os.path.join(SCRIPT_DIR, "generated-images")


def next_output_path(effect_name: str, ext: str) -> str:
    """generated-images/<effect_name>/<effect_name>-N.<ext>, N picking up after the highest existing one."""
    folder = os.path.join(OUTPUT_ROOT, effect_name)
    os.makedirs(folder, exist_ok=True)

    pattern = re.compile(rf"^{re.escape(effect_name)}-(\d+)\.{re.escape(ext)}$")
    existing = [int(m.group(1)) for f in os.listdir(folder) if (m := pattern.match(f))]
    n = max(existing, default=0) + 1

    return os.path.join(folder, f"{effect_name}-{n}.{ext}")


def save_optimized_gif(frames: list[Image.Image], out_path: str, max_bytes: int = GIF_MAX_BYTES):
    """Quantize all frames to one shared palette and save, shrinking the palette
    further if the result is still over max_bytes."""
    colors = GIF_COLORS
    while True:
        pal_frame = frames[len(frames) // 2].quantize(colors=colors, method=Image.MEDIANCUT)
        quantized = [
            f.quantize(colors=colors, palette=pal_frame, dither=Image.FLOYDSTEINBERG)
            for f in frames
        ]
        quantized[0].save(
            out_path,
            save_all=True,
            append_images=quantized[1:],
            duration=FRAME_DURATION_MS,
            loop=0,
            optimize=True,
        )
        size = os.path.getsize(out_path)
        if size <= max_bytes or colors <= 16:
            return size
        colors -= 16


def main():
    raw = sys.argv[1:]
    static = "--static" in raw

    effect_name = "coin-shine"
    if "--effect" in raw:
        idx = raw.index("--effect")
        effect_name = raw[idx + 1]
        del raw[idx:idx + 2]  # drop the flag and its value before parsing positionals

    args = [a for a in raw if not a.startswith("--")]

    if effect_name not in EFFECTS:
        print(f"Unknown effect '{effect_name}'. Available: {', '.join(EFFECTS)}")
        sys.exit(1)

    if len(args) < 1:
        print(f"Usage: python3 gif_maker.py <input_image> [output_file] [--static] [--effect {'|'.join(EFFECTS)}]")
        sys.exit(1)

    in_path = args[0]
    ext = "png" if static else "gif"
    out_path = args[1] if len(args) > 1 else next_output_path(effect_name, ext)

    base = Image.open(in_path)

    # crop to a centered square (matches how profile photos get used)
    w, h = base.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    base = base.crop((left, top, left + side, top + side))
    size = STATIC_SIZE if static else GIF_SIZE
    base = base.resize((size, size), Image.LANCZOS)

    frames = EFFECTS[effect_name](base)

    if static:
        # pick a frame where the glint is off to one side, not crossing the face
        pick = int(FRAMES * 0.42)
        frames[pick].save(out_path)
        print(f"Saved {out_path} (static frame {pick}/{FRAMES})")
    else:
        gif_size = save_optimized_gif(frames, out_path)
        print(f"Saved {out_path} ({len(frames)} frames, {gif_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()

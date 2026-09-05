#!/usr/bin/env python3
"""
gif_maker.py - apply a photo effect and export as an animated GIF (or a static frame).

Usage:
    python3 gif_maker.py <input_image> [output_file] [--static] [--effect coin-shine]
                          [--density 5-100] [--angle deg] [--speed 25-400]

Effects live one-per-file under effects/ and are collected into effects.EFFECTS.
Any --density/--angle/--speed flag left unset is asked for interactively instead
(skipped automatically when not running in a real terminal, e.g. in a script).
"""

import sys
import os
import re
import shlex
import inspect
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


def save_optimized_gif(frames: list[Image.Image], out_path: str, duration_ms: int, max_bytes: int = GIF_MAX_BYTES):
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
            duration=duration_ms,
            loop=0,
            optimize=True,
        )
        size = os.path.getsize(out_path)
        if size <= max_bytes or colors <= 16:
            return size
        colors -= 16


def take_flag_value(raw: list[str], name: str) -> str | None:
    """Pop --name and the value right after it out of raw, returning the value (or None if absent)."""
    if name not in raw:
        return None
    idx = raw.index(name)
    value = raw[idx + 1]
    del raw[idx:idx + 2]
    return value


def prompt_number(label: str, presets: tuple, default: float, lo: float, hi: float) -> float:
    """Ask the user for a number, offering presets but accepting any custom value in [lo, hi].
    Skipped (returns default) when not running in a real terminal, so scripts never hang."""
    if not sys.stdin.isatty():
        return default

    preset_str = "/".join(str(p) for p in presets)
    raw = input(f"{label} ({preset_str}, or type a custom value {lo:g}-{hi:g}) [default {default:g}]: ").strip()
    if raw == "":
        return default
    try:
        return max(lo, min(hi, float(raw.rstrip("%"))))
    except ValueError:
        print(f"Didn't understand '{raw}', using default {default:g}.")
        return default


def prompt_for_image_path() -> str:
    """Ask the user to drag a file into the terminal (or type a path), until a real file is given."""
    while True:
        raw = input("Drag your image into this window (or type its path), then press Enter: ").strip()
        if not raw:
            continue
        # shlex undoes both the quoting and the backslash-escaping a terminal adds when you drag a file in
        parts = shlex.split(raw)
        path = os.path.expanduser(parts[0]) if parts else ""
        if os.path.isfile(path):
            return path
        print(f"Can't find a file at '{path}' - try again.")


def prompt_for_effect() -> str:
    """Show a numbered menu of the registered effects and let the user pick one."""
    names = list(EFFECTS)
    print("\nWhich effect do you want?")
    for i, name in enumerate(names, 1):
        print(f"  {i}. {name}")
    while True:
        choice = input(f"Pick a number (1-{len(names)}) or type the name: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(names):
            return names[int(choice) - 1]
        if choice in EFFECTS:
            return choice
        print(f"Didn't recognize '{choice}' - try again.")


def main():
    raw = sys.argv[1:]
    static = "--static" in raw
    if static:
        raw.remove("--static")

    effect_flag = take_flag_value(raw, "--effect")
    density_flag = take_flag_value(raw, "--density")
    angle_flag = take_flag_value(raw, "--angle")
    speed_flag = take_flag_value(raw, "--speed")

    args = [a for a in raw if not a.startswith("--")]
    interactive = sys.stdin.isatty()

    if len(args) < 1 and not interactive:
        print(
            f"Usage: python3 gif_maker.py <input_image> [output_file] [--static] "
            f"[--effect {'|'.join(EFFECTS)}] [--density 5-100] [--angle deg] [--speed 25-400]"
        )
        sys.exit(1)

    in_path = args[0] if args else prompt_for_image_path()

    if effect_flag is not None:
        effect_name = effect_flag
    elif interactive:
        effect_name = prompt_for_effect()
    else:
        effect_name = "coin-shine"

    if effect_name not in EFFECTS:
        print(f"Unknown effect '{effect_name}'. Available: {', '.join(EFFECTS)}")
        sys.exit(1)

    ext = "png" if static else "gif"
    out_path = args[1] if len(args) > 1 else next_output_path(effect_name, ext)

    effect_fn = EFFECTS[effect_name]
    effect_params = inspect.signature(effect_fn).parameters

    # Only ask for the knobs this particular effect actually uses.
    kwargs = {}
    if "density" in effect_params:
        density_pct = float(density_flag) if density_flag is not None else prompt_number(
            "Density", presets=(25, 50, 75), default=50, lo=5, hi=100
        )
        kwargs["density"] = max(5, min(100, density_pct)) / 100
    if "angle" in effect_params:
        kwargs["angle"] = float(angle_flag) if angle_flag is not None else prompt_number(
            "Sweep angle (degrees)", presets=(15, 25, 40), default=25, lo=0, hi=90
        )

    speed_pct = float(speed_flag) if speed_flag is not None else (
        100.0 if static else prompt_number(
            "Playback speed % (100 = normal, higher = faster)", presets=(50, 100, 200), default=100, lo=25, hi=400
        )
    )
    duration_ms = round(FRAME_DURATION_MS * (100 / max(25, min(400, speed_pct))))

    base = Image.open(in_path)

    # crop to a centered square (matches how profile photos get used)
    w, h = base.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    base = base.crop((left, top, left + side, top + side))
    size = STATIC_SIZE if static else GIF_SIZE
    base = base.resize((size, size), Image.LANCZOS)

    frames = effect_fn(base, **kwargs)

    if static:
        # pick a frame where the glint is off to one side, not crossing the face
        pick = int(FRAMES * 0.42)
        frames[pick].save(out_path)
        print(f"Saved {out_path} (static frame {pick}/{FRAMES})")
    else:
        gif_size = save_optimized_gif(frames, out_path, duration_ms)
        print(f"Saved {out_path} ({len(frames)} frames, {gif_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()

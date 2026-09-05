import math
import random
from PIL import Image, ImageDraw, ImageChops, ImageFilter

from .common import FRAMES


def space_dust_feature(base: Image.Image, density: float = 1.0) -> list[Image.Image]:
    """Soft white/blue glowing dust drifting slowly, with parallax depth.

    density: 0.05-1.0 fraction of the tuned baseline particle count (1.0 = the default look).
    """
    NUM_PARTICLES = max(1, round(40 * density))
    WHITE_TINT = (255, 255, 255)
    BLUE_TINT = (170, 205, 255)
    SEED = 13  # fixed so particle layout is stable across runs of the same size

    base = base.convert("RGB")
    w, h = base.size
    rng = random.Random(SEED)

    def make_glow_glyph(size: int) -> Image.Image:
        s = size * 4
        glyph = Image.new("L", (s, s), 0)
        d = ImageDraw.Draw(glyph)
        r = s * 0.22
        d.ellipse([s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r], fill=255)
        glyph = glyph.filter(ImageFilter.GaussianBlur(radius=s * 0.14))
        return glyph.resize((size, size), Image.LANCZOS)

    particles = []
    for _ in range(NUM_PARTICLES):
        depth = rng.uniform(0.0, 1.0)  # 0 = far/background, 1 = near/foreground
        size = max(2, int(w * (0.012 + 0.035 * depth)))
        particles.append({
            "pos": (rng.uniform(0, w), rng.uniform(0, h)),
            "amp_x": w * (0.008 + 0.045 * depth),
            "amp_y": h * (0.008 + 0.045 * depth),
            "freq_x": rng.uniform(0.7, 1.3),
            "freq_y": rng.uniform(0.7, 1.3),
            "phase_x": rng.uniform(0, 2 * math.pi),
            "phase_y": rng.uniform(0, 2 * math.pi),
            "opacity": 0.25 + 0.65 * depth,
            "glyph": make_glow_glyph(size),
            "size": size,
            "tint": "blue" if rng.random() < 0.4 else "white",
        })

    frames = []
    for i in range(FRAMES):
        t = i / FRAMES
        mask_white = Image.new("L", (w, h), 0)
        mask_blue = Image.new("L", (w, h), 0)
        for p in particles:
            dx = p["amp_x"] * math.sin(2 * math.pi * p["freq_x"] * t + p["phase_x"])
            dy = p["amp_y"] * math.sin(2 * math.pi * p["freq_y"] * t + p["phase_y"])
            px = int(p["pos"][0] + dx)
            py = int(p["pos"][1] + dy)
            glyph = p["glyph"].point(lambda v, o=p["opacity"]: int(v * o))
            s = p["size"]
            mask = mask_blue if p["tint"] == "blue" else mask_white
            mask.paste(glyph, (px - s // 2, py - s // 2), glyph)

        lit = base
        white_highlight = Image.new("RGB", (w, h), WHITE_TINT)
        lit = ImageChops.screen(lit, Image.composite(white_highlight, Image.new("RGB", (w, h), (0, 0, 0)), mask_white))
        blue_highlight = Image.new("RGB", (w, h), BLUE_TINT)
        lit = ImageChops.screen(lit, Image.composite(blue_highlight, Image.new("RGB", (w, h), (0, 0, 0)), mask_blue))
        frames.append(lit)

    return frames

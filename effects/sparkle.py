import math
import random
from PIL import Image, ImageDraw, ImageChops, ImageFilter

from .common import FRAMES


def sparkle_feature(base: Image.Image) -> list[Image.Image]:
    """Small twinkling star-glints that pulse on and off at random spots."""
    NUM_SPARKLES = 10
    SPARKLE_COLOR = (255, 255, 255)
    SEED = 7  # fixed so sparkle positions are stable across runs of the same size

    base = base.convert("RGB")
    w, h = base.size
    rng = random.Random(SEED)

    def make_star_glyph(size: int) -> Image.Image:
        s = size * 4
        glyph = Image.new("L", (s, s), 0)
        d = ImageDraw.Draw(glyph)
        cx = cy = s // 2
        d.ellipse([cx - s * 0.12, cy - s * 0.12, cx + s * 0.12, cy + s * 0.12], fill=255)
        ray_w = max(2, s // 40)
        d.line([(cx, 0), (cx, s)], fill=255, width=ray_w)
        d.line([(0, cy), (s, cy)], fill=255, width=ray_w)
        glyph = glyph.filter(ImageFilter.GaussianBlur(radius=s * 0.03))
        return glyph.resize((size, size), Image.LANCZOS)

    sparkles = []
    for _ in range(NUM_SPARKLES):
        size = rng.randint(int(w * 0.06), int(w * 0.11))
        sparkles.append({
            "pos": (rng.randint(int(w * 0.1), int(w * 0.9)), rng.randint(int(h * 0.1), int(h * 0.9))),
            "phase": rng.uniform(0, 2 * math.pi),
            "speed": rng.uniform(1.5, 3.0),
            "glyph": make_star_glyph(size),
            "size": size,
        })

    frames = []
    for i in range(FRAMES):
        t = i / FRAMES
        overlay = Image.new("L", (w, h), 0)
        for sp in sparkles:
            raw = math.sin(2 * math.pi * sp["speed"] * t + sp["phase"])
            intensity = max(0.0, raw) ** 3  # sharpen into short twinkle bursts
            if intensity <= 0.01:
                continue
            glyph = sp["glyph"].point(lambda p, i=intensity: int(p * i))
            px, py = sp["pos"]
            s = sp["size"]
            overlay.paste(glyph, (px - s // 2, py - s // 2), glyph)

        highlight = Image.new("RGB", (w, h), SPARKLE_COLOR)
        lit = ImageChops.screen(base, Image.composite(highlight, Image.new("RGB", (w, h), (0, 0, 0)), overlay))
        frames.append(lit)

    return frames

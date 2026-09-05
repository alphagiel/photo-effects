import math
import random
from PIL import Image, ImageDraw, ImageChops

from .common import FRAMES


def sparkle_contoured_feature(base: Image.Image, density: float = 1.0) -> list[Image.Image]:
    """Small twinkling cartoon star-glints (black outline, pulsing white fill).

    density: 0.05-1.0 fraction of the tuned baseline sparkle count (1.0 = the default look).
    """
    NUM_SPARKLES = max(1, round(10 * density))
    SPARKLE_COLOR = (255, 255, 255)
    OUTLINE_COLOR = (0, 0, 0)
    SEED = 7  # fixed so sparkle positions are stable across runs of the same size

    base = base.convert("RGB")
    w, h = base.size
    rng = random.Random(SEED)

    def make_star_glyphs(size: int) -> tuple[Image.Image, Image.Image]:
        """Return (fill_mask, outline_mask) for a sharp 4-point sparkle star."""
        s = size * 4
        cx = cy = s / 2
        outer_r = s * 0.5
        inner_r = outer_r * 0.28
        points = []
        for k in range(8):
            angle = math.pi / 4 * k - math.pi / 2
            r = outer_r if k % 2 == 0 else inner_r
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))

        fill_img = Image.new("L", (s, s), 0)
        ImageDraw.Draw(fill_img).polygon(points, fill=255)

        outline_img = Image.new("L", (s, s), 0)
        stroke_w = max(2, s // 16)
        ImageDraw.Draw(outline_img).polygon(points, outline=255, width=stroke_w)

        fill_img = fill_img.resize((size, size), Image.LANCZOS)
        outline_img = outline_img.resize((size, size), Image.LANCZOS)
        return fill_img, outline_img

    sparkles = []
    for _ in range(NUM_SPARKLES):
        size = rng.randint(int(w * 0.06), int(w * 0.11))
        fill_glyph, outline_glyph = make_star_glyphs(size)
        sparkles.append({
            "pos": (rng.randint(int(w * 0.1), int(w * 0.9)), rng.randint(int(h * 0.1), int(h * 0.9))),
            "phase": rng.uniform(0, 2 * math.pi),
            "speed": rng.uniform(1.5, 3.0),
            "fill_glyph": fill_glyph,
            "outline_glyph": outline_glyph,
            "size": size,
        })

    outline_layer = Image.new("RGB", (w, h), OUTLINE_COLOR)

    frames = []
    for i in range(FRAMES):
        t = i / FRAMES
        fill_overlay = Image.new("L", (w, h), 0)
        outline_overlay = Image.new("L", (w, h), 0)
        for sp in sparkles:
            raw = math.sin(2 * math.pi * sp["speed"] * t + sp["phase"])
            intensity = max(0.0, raw) ** 3  # sharpen into short twinkle bursts
            if intensity <= 0.01:
                continue
            px, py = sp["pos"]
            s = sp["size"]
            fill_glyph = sp["fill_glyph"].point(lambda p, i=intensity: int(p * i))
            fill_overlay.paste(fill_glyph, (px - s // 2, py - s // 2), fill_glyph)
            outline_glyph = sp["outline_glyph"].point(lambda p, i=intensity: int(p * i))
            outline_overlay.paste(outline_glyph, (px - s // 2, py - s // 2), outline_glyph)

        highlight = Image.new("RGB", (w, h), SPARKLE_COLOR)
        lit = ImageChops.screen(base, Image.composite(highlight, Image.new("RGB", (w, h), (0, 0, 0)), fill_overlay))
        frame = Image.composite(outline_layer, lit, outline_overlay)
        frames.append(frame)

    return frames

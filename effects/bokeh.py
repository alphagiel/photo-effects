import math
import random
from PIL import Image, ImageDraw, ImageChops, ImageFilter

from .common import FRAMES


def bokeh_feature(base: Image.Image, density: float = 1.0) -> list[Image.Image]:
    """Soft, blurred circles of light drifting across the image, like out-of-focus camera bokeh.

    density: 0.05-1.0 fraction of the tuned baseline orb count (1.0 = the default look).
    """
    NUM_ORBS = max(1, round(5 * density))
    SEED = 11  # fixed so orb positions/colors are stable across runs of the same size
    COLORS = [
        (255, 250, 235),  # warm white
        (255, 214, 170),  # soft gold
        (255, 200, 220),  # soft pink
        (200, 225, 255),  # pale blue
    ]

    base = base.convert("RGB")
    w, h = base.size
    rng = random.Random(SEED)

    def make_orb_glyph(radius: int) -> Image.Image:
        # oversample then blur for a soft, camera-bokeh falloff (not a hard-edged circle)
        s = radius * 6
        glyph = Image.new("L", (s, s), 0)
        d = ImageDraw.Draw(glyph)
        pad = s * 0.15
        d.ellipse([pad, pad, s - pad, s - pad], fill=255)
        glyph = glyph.filter(ImageFilter.GaussianBlur(radius=s * 0.09))
        return glyph.resize((radius * 2, radius * 2), Image.LANCZOS)

    # spread orbs across roughly separate regions so they read as distinct circles
    # instead of one continuous haze once several overlap
    cols, rows = 3, 2
    cells = [(c, r) for r in range(rows) for c in range(cols)]
    rng.shuffle(cells)

    orbs = []
    for k in range(NUM_ORBS):
        cell_c, cell_r = cells[k % len(cells)]
        cx = (cell_c + 0.5) / cols * w + rng.uniform(-0.08, 0.08) * w
        cy = (cell_r + 0.5) / rows * h + rng.uniform(-0.08, 0.08) * h

        radius = rng.randint(int(w * 0.045), int(w * 0.08))
        angle = rng.uniform(0, 2 * math.pi)
        speed = rng.uniform(0.03, 0.07) * w  # total drift distance over the loop, in pixels
        orbs.append({
            "start": (cx, cy),
            "drift": (math.cos(angle) * speed, math.sin(angle) * speed),
            "radius": radius,
            "glyph": make_orb_glyph(radius),
            "color": rng.choice(COLORS),
            "base_opacity": rng.uniform(0.6, 0.9),
            "twinkle_phase": rng.uniform(0, 2 * math.pi),
        })

    frames = []
    for i in range(FRAMES):
        t = i / FRAMES
        overlay = Image.new("RGB", (w, h), (0, 0, 0))
        for orb in orbs:
            sx, sy = orb["start"]
            dx, dy = orb["drift"]
            # loop the drift smoothly (sine sweep out and back) so the gif tiles seamlessly
            sweep = math.sin(2 * math.pi * t)
            px = int(sx + dx * sweep)
            py = int(sy + dy * sweep)

            twinkle = 0.85 + 0.15 * math.sin(2 * math.pi * t * 2 + orb["twinkle_phase"])
            opacity = orb["base_opacity"] * twinkle

            r = orb["radius"]
            glyph = orb["glyph"].point(lambda p, o=opacity: int(p * o))
            colored = Image.new("RGB", glyph.size, orb["color"])
            overlay.paste(colored, (px - r, py - r), glyph)

        frames.append(ImageChops.screen(base, overlay))

    return frames

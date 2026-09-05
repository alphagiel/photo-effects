import math
from PIL import Image, ImageDraw, ImageChops, ImageFilter

from .common import FRAMES


def coin_shine_feature(base: Image.Image) -> list[Image.Image]:
    """Diagonal coin-shine/glimmer sweep across the image."""
    BAND_ANGLE_DEG = 25       # angle of the shine streak
    BAND_WIDTH_RATIO = 0.35   # width of the bright streak relative to image size
    SHINE_COLOR = (255, 250, 210)  # warm gold-white
    MAX_INTENSITY = 0.55      # cap how bright the glint gets (0-1), avoids blowing out the face

    base = base.convert("RGB")
    w, h = base.size

    # Oversized canvas so the rotated band can travel fully across the image
    diag = int(math.hypot(w, h))
    big = diag * 2
    band_w = max(20, int(diag * BAND_WIDTH_RATIO))

    # Vertical gradient band: dark -> bright -> dark
    gradient = Image.new("L", (band_w, big), 0)
    gdraw = ImageDraw.Draw(gradient)
    half = band_w / 2
    for x in range(band_w):
        d = abs(x - half) / half
        val = int(255 * MAX_INTENSITY * max(0.0, 1.0 - d) ** 1.5)
        gdraw.line([(x, 0), (x, big)], fill=val)

    # Paste the gradient band into a big square canvas, then rotate to get the diagonal streak
    band_canvas = Image.new("L", (big, big), 0)
    band_canvas.paste(gradient, (big // 2 - band_w // 2, 0))
    band_canvas = band_canvas.rotate(BAND_ANGLE_DEG, resample=Image.BICUBIC, expand=False)
    band_canvas = band_canvas.filter(ImageFilter.GaussianBlur(radius=diag * 0.02))

    frames = []
    travel = big - w
    for i in range(FRAMES):
        t = i / FRAMES
        offset_x = int(travel * t)
        offset_y = (big - h) // 2
        mask = band_canvas.crop((offset_x, offset_y, offset_x + w, offset_y + h))

        highlight = Image.new("RGB", (w, h), SHINE_COLOR)
        lit = ImageChops.screen(base, Image.composite(highlight, Image.new("RGB", (w, h), (0, 0, 0)), mask))

        frames.append(lit)

    return frames

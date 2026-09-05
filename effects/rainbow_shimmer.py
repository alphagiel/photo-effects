import math
from PIL import Image, ImageDraw, ImageFilter, ImageChops

from .common import FRAMES


def rainbow_shimmer_feature(base: Image.Image) -> list[Image.Image]:
    """Diagonal shimmer band that sweeps across the image cycling through the rainbow."""
    BAND_ANGLE_DEG = 25       # angle of the shimmer streak
    BAND_WIDTH_RATIO = 0.22   # width of the bright streak relative to image size
    SATURATION = 220          # 0-255, how vivid the rainbow colors are
    MAX_INTENSITY = 0.45      # cap how bright the shimmer gets (0-1), avoids blowing out the face

    base = base.convert("RGB")
    w, h = base.size

    # Oversized canvas so the rotated band can travel fully across the image
    diag = int(math.hypot(w, h))
    big = diag * 2
    band_w = max(20, int(diag * BAND_WIDTH_RATIO))

    # Build the band directly in HSV: hue sweeps across the band's width (the rainbow),
    # value (brightness) fades out at the band's edges (dark -> bright -> dark), so once
    # converted to RGB the edges are pure black and composite cleanly via screen blend.
    band_hsv = Image.new("HSV", (band_w, big), (0, 0, 0))
    hdraw = ImageDraw.Draw(band_hsv)
    edge_fade = band_w * 0.15  # only the outer 15% tapers to black; the rest stays fully lit
    for x in range(band_w):
        hue = int(255 * (x / band_w))
        if x < edge_fade:
            fade = x / edge_fade
        elif x > band_w - edge_fade:
            fade = (band_w - x) / edge_fade
        else:
            fade = 1.0
        val = int(255 * MAX_INTENSITY * fade)
        hdraw.line([(x, 0), (x, big)], fill=(hue, SATURATION, val))
    band_rgb = band_hsv.convert("RGB")

    # Paste into a big square canvas, then rotate to get the diagonal streak
    band_canvas = Image.new("RGB", (big, big), (0, 0, 0))
    band_canvas.paste(band_rgb, (big // 2 - band_w // 2, 0))
    band_canvas = band_canvas.rotate(BAND_ANGLE_DEG, resample=Image.BICUBIC, expand=False)
    band_canvas = band_canvas.filter(ImageFilter.GaussianBlur(radius=diag * 0.015))

    frames = []
    travel = big - w
    for i in range(FRAMES):
        t = i / FRAMES
        offset_x = int(travel * t)
        offset_y = (big - h) // 2
        band = band_canvas.crop((offset_x, offset_y, offset_x + w, offset_y + h))

        lit = ImageChops.screen(base, band)
        frames.append(lit)

    return frames

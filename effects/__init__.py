"""
Effect registry. Each effect is its own module with a function of shape
    def some_feature(base: Image.Image) -> list[Image.Image]

To add a new gif maker:
    1. Create effects/my_effect.py with a `my_effect_feature(base)` function.
    2. Import it below and add it to EFFECTS under whatever --effect name you want.
"""

from .common import FRAMES
from .coin_shine import coin_shine_feature
from .sparkle import sparkle_feature
from .sparkle_contoured import sparkle_contoured_feature
from .rainbow_shimmer import rainbow_shimmer_feature
from .bokeh import bokeh_feature
from .space_dust import space_dust_feature

EFFECTS = {
    "coin-shine": coin_shine_feature,
    "sparkle": sparkle_feature,
    "sparkle-contoured": sparkle_contoured_feature,
    "rainbow-shimmer": rainbow_shimmer_feature,
    "bokeh": bokeh_feature,
    "space-dust": space_dust_feature,
}

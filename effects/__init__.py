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

EFFECTS = {
    "coin-shine": coin_shine_feature,
    "sparkle": sparkle_feature,
}

# photo-effects

Turn any photo into a shimmering, sparkling, animated GIF — free, local, no subscription, no watermark.

Made because paying for "add a shine to my photo" felt ridiculous. This does it in a couple seconds on your own machine.

## Effects

| Coin Shine | Sparkle | Sparkle (Contoured) | Rainbow Shimmer |
|:---:|:---:|:---:|:---:|
| ![coin shine](docs/samples/coin-shine.gif) | ![sparkle](docs/samples/sparkle.gif) | ![sparkle contoured](docs/samples/sparkle-contoured.gif) | ![rainbow shimmer](docs/samples/rainbow-shimmer.gif) |

## Install

Requires Python 3.10+ and [Pillow](https://pillow.readthedocs.io/).

```
git clone git@github.com:alphagiel/photo-effects.git
cd photo-effects
pip install pillow
```

## Usage

```
python3 gif_maker.py <your-photo.jpg> --effect coin-shine
```

Output is saved to `generated-images/<effect>/<effect>-N.gif`, numbered so the latest is always the highest N.

Options:

| Flag | What it does |
|---|---|
| `--effect <name>` | Which effect to apply: `coin-shine`, `sparkle`, `sparkle-contoured`, `rainbow-shimmer` |
| `--static` | Save a single flattering frame as a `.png` instead of an animated `.gif` (useful anywhere animated images aren't supported, like most profile photo slots) |

Example:

```
python3 gif_maker.py photo.jpg --effect sparkle --static
```

## Adding a new effect

Effects live one-per-file in `effects/`. Each is just a function:

```python
def my_effect_feature(base: Image.Image) -> list[Image.Image]:
    ...  # return a list of frames
```

Drop it in `effects/`, import it and add it to `EFFECTS` in `effects/__init__.py`, and it's immediately usable via `--effect my-effect`.

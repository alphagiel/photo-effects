# photo-effects

Turn any photo into a shimmering, sparkling, animated GIF — free, local, no subscription, no watermark.

Made because paying for "add a shine to my photo" felt ridiculous. This does it in a couple seconds on your own machine.

## Effects

| Coin Shine | Sparkle | Sparkle (Contoured) | Rainbow Shimmer |
|:---:|:---:|:---:|:---:|
| ![coin shine](docs/samples/coin-shine.gif) | ![sparkle](docs/samples/sparkle.gif) | ![sparkle contoured](docs/samples/sparkle-contoured.gif) | ![rainbow shimmer](docs/samples/rainbow-shimmer.gif) |

| Bokeh | Space Dust |
|:---:|:---:|
| ![bokeh](docs/samples/bokeh.gif) | ![space dust](docs/samples/space-dust.gif) |

## Install

Requires Python 3.10+ and [Pillow](https://pillow.readthedocs.io/).

```
git clone git@github.com:alphagiel/photo-effects.git
cd photo-effects
pip install pillow
```

## Usage

**Guided setup** — just run it with no arguments:

```
python3 gif_maker.py
```

It'll ask you to drag your image into the terminal (or type its path), show you a numbered list of effects to pick from, then ask for whatever settings that effect uses (density/angle/speed) — with presets to pick from or type your own value.

**Or skip straight to it** with flags, for scripting or quick reruns:

```
python3 gif_maker.py <your-photo.jpg> --effect coin-shine
```

Output is saved to `generated-images/<effect>/<effect>-N.gif`, numbered so the latest is always the highest N.

Options:

| Flag | What it does |
|---|---|
| `--effect <name>` | Which effect to apply: `coin-shine`, `sparkle`, `sparkle-contoured`, `rainbow-shimmer`, `bokeh`, `space-dust` |
| `--static` | Save a single flattering frame as a `.png` instead of an animated `.gif` (useful anywhere animated images aren't supported, like most profile photo slots) |
| `--density 5-100` | How many sparkles/dust particles/orbs to render, as a % of the tuned default. Only applies to `sparkle`, `sparkle-contoured`, `bokeh`, `space-dust`. |
| `--angle <degrees>` | The sweep angle of the shimmer band. Only applies to `coin-shine`, `rainbow-shimmer`. |
| `--speed 25-400` | Playback speed as a %, 100 = normal, higher = faster. Applies to all animated effects (ignored with `--static`). |

If you leave `--density`/`--angle`/`--speed` off, and the effect you picked actually uses that knob, you'll get asked for it interactively (with a few presets to pick from, or type your own value) — unless you're piping input or running non-interactively, in which case it just uses a sensible default so scripts never hang.

Example:

```
python3 gif_maker.py photo.jpg --effect sparkle --static
python3 gif_maker.py photo.jpg --effect space-dust --density 75 --speed 150
```

## Adding a new effect

Effects live one-per-file in `effects/`. Each is just a function:

```python
def my_effect_feature(base: Image.Image) -> list[Image.Image]:
    ...  # return a list of frames
```

Drop it in `effects/`, import it and add it to `EFFECTS` in `effects/__init__.py`, and it's immediately usable via `--effect my-effect`.

To make it tunable via `--density` or `--angle` (and get the interactive prompt for free), just add a matching keyword argument with a default:

```python
def my_effect_feature(base: Image.Image, density: float = 1.0) -> list[Image.Image]:
    ...  # density arrives as a 0.05-1.0 fraction, already resolved from the flag/prompt
```

`gif_maker.py` detects which of `density`/`angle` an effect's function accepts and only asks about the ones it actually uses.

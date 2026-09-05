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

## How it works, step by step

Running `python3 gif_maker.py` with no arguments walks you through the whole thing:

1. **It asks for your photo.** Drag the image file straight into the terminal window (it'll paste in the path automatically) or just type the path yourself.
2. **It shows you a numbered list of effects.** Type the number, or type the effect's name directly.
3. **It asks for whatever settings that effect actually uses.** A sparkle-type effect asks for density (how many pieces) and speed (how fast it plays); a shine/shimmer effect asks for angle and speed instead. Each question shows a few presets plus a default — hit Enter to accept the default, type a preset number, or type any custom value in the allowed range.
4. **It generates 24 frames and saves the result** to `generated-images/<effect>/<effect>-N.gif`, auto-numbered so the newest file is always the highest N.

Here's what that actually looks like in a terminal:

```
$ python3 gif_maker.py
Drag your image into this window (or type its path), then press Enter: /Users/alphagiel/Desktop/sample-photo.jpeg

Which effect do you want?
  1. coin-shine
  2. sparkle
  3. sparkle-contoured
  4. rainbow-shimmer
  5. bokeh
  6. space-dust
Pick a number (1-6) or type the name: 5
Density (25/50/75, or type a custom value 5-100) [default 50]: 100
Playback speed % (100 = normal, higher = faster) (50/100/200, or type a custom value 25-400) [default 100]: 55
Saved /Users/alphagiel/Desktop/gif-maker/generated-images/bokeh/bokeh-5.gif (24 frames, 871 KB)
```

Already know exactly what you want? Skip the whole conversation with flags in one line:

```
$ python3 gif_maker.py ~/Desktop/sample-photo.jpeg --effect sparkle-contoured --density 20 --speed 90
Saved /Users/alphagiel/Desktop/gif-maker/generated-images/sparkle-contoured/sparkle-contoured-6.gif (24 frames, 216 KB)
```

Any flag you leave out still gets asked about interactively (as long as you're running it in a real terminal) — you can mix and match, e.g. pass `--effect` but let it prompt you for density.

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

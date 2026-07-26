"""Prism Path — royal-symbol identity tints (J/Q/K/A gain a slight cast of a gem's colour).

The four white-crystal royals read too alike at board size; each takes a SELECTIVE overlay
of one gem's identity hue (derived live from the H textures, so it stays true to the art):
    J (L2) <- H1 fire    Q (L3) <- H3 nature    K (L4) <- H2 water    A (L5) <- H4 arcane

Quality rules (why this is a script, not a flat overlay):
  * only the near-neutral LIGHT crystal body tints (lum>0.45, sat<0.3, smooth-stepped) —
    dark outlines stay ink-crisp, existing rainbow facet accents keep their colours;
  * colourise at each pixel's own shading level, pulled slightly below pure white
    (a luminance-matched colourise vanishes on ~95%-white pixels);
  * STRENGTH is the single tuning knob (0.45 locked — 0.35 read too faint in-game;
    0.28 was ambiguous at the royals' 69px render size).
  * IMPORTANT: the script tints IN PLACE — `git checkout` the L*.png originals before
    re-running at a different strength, or the tint compounds.

BAKED AT THE ASSET LEVEL by design: the game code is untouched (no runtime tinting), so
board, paytable and any other consumer of L2-L5.png stay consistent automatically.

Run (needs numpy+pillow):  python tools/tint_royals.py
Re-run after any change to the royal or gem source art. Originals recoverable via git.
"""

import colorsys
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SYM = os.path.join(HERE, "..", "static", "assets", "symbols")

STRENGTH = 0.45
TINT_SAT = 0.55
# royal -> the gem whose identity hue it borrows
PAIRING = {"L2": "H1", "L3": "H3", "L4": "H2", "L5": "H4"}


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def dominant_hue(gem_path):
    """Circular-median hue of the gem's saturated pixels (its identity colour)."""
    a = np.array(Image.open(gem_path).convert("RGBA")).astype(float) / 255
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    mx, mn = a[..., :3].max(-1), a[..., :3].min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    mask = (al > 0.9) & (sat > 0.45) & (mx > 0.35)
    ys, xs = np.where(mask)
    hs = [colorsys.rgb_to_hls(r[y, x], g[y, x], b[y, x])[0] for y, x in zip(ys[::7], xs[::7])]
    ang = np.array(hs) * 2 * np.pi
    return (np.arctan2(np.sin(ang).mean(), np.cos(ang).mean()) / (2 * np.pi)) % 1


def tint(img_arr, hue01, strength):
    a = img_arr.astype(float) / 255
    al = a[..., 3]
    mx, mn = a[..., :3].max(-1), a[..., :3].min(-1)
    lum = (mx + mn) / 2
    satpx = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    w = smoothstep(0.45, 0.65, lum) * (1 - smoothstep(0.30, 0.55, satpx)) * (al > 0)
    lut = np.array([colorsys.hls_to_rgb(hue01, min(l / 255 * 0.86, 0.84), TINT_SAT) for l in range(256)])
    pal = lut[np.clip((lum * 255).astype(int), 0, 255)]
    k = (strength * w)[..., None]
    out = a.copy()
    out[..., :3] = a[..., :3] * (1 - k) + pal * k
    return (out * 255).astype(np.uint8)


if __name__ == "__main__":
    for royal, gem in PAIRING.items():
        hue = dominant_hue(os.path.join(SYM, f"{gem}.png"))
        p = os.path.join(SYM, f"{royal}.png")
        src = np.array(Image.open(p).convert("RGBA"))
        Image.fromarray(tint(src, hue, STRENGTH)).save(p)
        print(f"{royal} <- {gem} hue {hue * 360:.0f}deg @ {STRENGTH:.0%}")
    print("ROYAL TINTS BAKED")

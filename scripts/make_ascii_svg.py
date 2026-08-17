"""Turn `source-prepped.png` into a self-typing ASCII portrait SVG.

Each row is wrapped in a horizontal clip that wipes left-to-right with a small
block cursor riding the wipe edge, staggered top to bottom. It prints once and
freezes -- no looping. SMIL lives inside the SVG, so GitHub plays it.

    python scripts/make_ascii_svg.py   # writes avi-ascii.svg
"""

import argparse
import os
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense)
#        ^ leading space clears the background to nothing

CHAR_W = 6.0            # monospace advance at FONT_SIZE
LINE_H = 11.0
FONT_SIZE = 10.0
PAD_X = 16.0
PAD_Y = 16.0

BG = "#0d1117"
FG = "#c9d1d9"
CURSOR = "#39d353"

STAGGER = 0.055         # seconds between row starts
ROW_DUR = 0.34          # seconds for one row to wipe in


def to_grid(img: Image.Image, cols: int, max_rows: int) -> list[str]:
    aspect = CHAR_W / LINE_H
    rows = max(1, round(img.height / img.width * cols * aspect))
    rows = min(rows, max_rows)
    small = img.convert("L").resize((cols, rows), Image.LANCZOS)
    px = np.asarray(small, dtype=np.float32)

    # Stretch to the full 0..255 range so the ramp gets used end to end.
    lo, hi = np.percentile(px, 1.0), np.percentile(px, 99.0)
    if hi > lo:
        px = np.clip((px - lo) * (255.0 / (hi - lo)), 0, 255)

    idx = ((255.0 - px) / 256.0 * len(RAMP)).astype(int)
    idx = np.clip(idx, 0, len(RAMP) - 1)
    return ["".join(RAMP[i] for i in row) for row in idx]


def build_svg(lines: list[str], static: bool = False) -> str:
    cols = max(len(line) for line in lines)
    width = PAD_X * 2 + cols * CHAR_W
    height = PAD_Y * 2 + len(lines) * LINE_H

    defs, body = [], []
    for i, raw in enumerate(lines):
        stripped = raw.rstrip()
        if not stripped.strip():
            continue
        left = len(stripped) - len(stripped.lstrip())
        seg = stripped[left:]
        x0 = PAD_X + left * CHAR_W
        seg_w = len(seg) * CHAR_W
        y = PAD_Y + i * LINE_H
        begin = round(i * STAGGER, 3)
        end = round(begin + ROW_DUR, 3)

        if static:
            body.append(
                f'<text x="{x0:.1f}" y="{y + FONT_SIZE * 0.8:.1f}" '
                f'textLength="{seg_w:.1f}" lengthAdjust="spacing" xml:space="preserve">'
                f"{escape(seg)}</text>"
            )
            continue

        defs.append(
            # The rect starts full-width so a renderer that ignores SMIL shows
            # the finished portrait instead of a blank panel; `from` takes over
            # as soon as the animation runs.
            f'<clipPath id="w{i}"><rect x="{x0:.1f}" y="{y - 2:.1f}" '
            f'width="{seg_w:.1f}" height="{LINE_H + 3:.1f}">'
            f'<animate attributeName="width" from="0" to="{seg_w:.1f}" '
            f'begin="{begin}s" dur="{ROW_DUR}s" fill="freeze"/></rect></clipPath>'
        )
        body.append(
            f'<g clip-path="url(#w{i})"><text x="{x0:.1f}" y="{y + FONT_SIZE * 0.8:.1f}" '
            f'textLength="{seg_w:.1f}" lengthAdjust="spacing" xml:space="preserve">'
            f"{escape(seg)}</text></g>"
        )
        body.append(
            f'<rect x="{x0:.1f}" y="{y:.1f}" width="{CHAR_W:.1f}" height="{LINE_H - 1:.1f}" '
            f'fill="{CURSOR}" opacity="0">'
            f'<set attributeName="opacity" to="0.9" begin="{begin}s" fill="freeze"/>'
            f'<animate attributeName="x" from="{x0:.1f}" to="{x0 + seg_w:.1f}" '
            f'begin="{begin}s" dur="{ROW_DUR}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{end}s" fill="freeze"/></rect>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-label="ASCII portrait">'
        f"<defs>{''.join(defs)}</defs>"
        f'<rect width="{width:.0f}" height="{height:.0f}" rx="10" fill="{BG}"/>'
        f'<g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, '
        f'&quot;DejaVu Sans Mono&quot;, monospace" font-size="{FONT_SIZE}" fill="{FG}">'
        f"{''.join(body)}</g></svg>"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", default="source-prepped.png")
    ap.add_argument("-o", "--out", default="avi-ascii.svg")
    ap.add_argument("--cols", type=int, default=100)
    ap.add_argument("--max-rows", type=int, default=62)
    args = ap.parse_args()

    src = ROOT / args.input if not Path(args.input).is_absolute() else Path(args.input)
    dst = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)

    lines = to_grid(Image.open(src), args.cols, args.max_rows)
    static = os.environ.get("STATIC") == "1"
    dst.write_text(build_svg(lines, static), encoding="utf-8")
    print(f"wrote {dst}  ({args.cols} cols x {len(lines)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

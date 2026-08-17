"""Compose the portrait and the info card into one side-by-side SVG.

Two separate <img> tags wrap onto two rows as soon as the reader's viewport is
narrower than their combined width, and a <table> would keep them on one row
only at the cost of GitHub's <td> borders. Nesting both into a single SVG makes
the pair one image: it can never wrap, and it scales down instead of stacking.

Animations survive -- a nested <svg> keeps its own viewBox, and the SMIL and CSS
inside each panel still run.

    python scripts/compose_whoami.py   # writes whoami.svg
"""

import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TARGET_W = 860          # matches the heatmap so all edges line up
GAP = 12
PANELS = [("avi-ascii.svg", 370), ("info-card.svg", 490)]   # file, layout weight


def split_svg(path: Path) -> tuple[float, float, str]:
    """Return (viewBox width, viewBox height, everything inside the root tag)."""
    text = path.read_text(encoding="utf-8")
    root = re.match(r"<svg\b[^>]*>", text)
    if not root:
        raise SystemExit(f"{path.name}: no root <svg> tag")
    view_box = re.search(r'viewBox="([^"]+)"', root.group(0))
    if not view_box:
        raise SystemExit(f"{path.name}: root <svg> has no viewBox")
    _, _, vw, vh = (float(v) for v in view_box.group(1).replace(",", " ").split())
    inner = text[root.end():]
    return vw, vh, inner[:inner.rfind("</svg>")]


def main() -> int:
    panels = []
    for name, weight in PANELS:
        path = ROOT / name
        if not path.exists():
            raise SystemExit(f"{name} missing -- generate it first")
        vw, vh, inner = split_svg(path)
        panels.append({"vw": vw, "vh": vh, "inner": inner, "weight": weight})

    usable = TARGET_W - GAP * (len(panels) - 1)
    total_weight = sum(p["weight"] for p in panels)
    for panel in panels:
        panel["w"] = usable * panel["weight"] / total_weight
        panel["h"] = panel["vh"] / panel["vw"] * panel["w"]

    height = math.ceil(max(p["h"] for p in panels))

    body, x = [], 0.0
    for panel in panels:
        body.append(
            f'<svg x="{x:.2f}" y="0" width="{panel["w"]:.2f}" height="{panel["h"]:.2f}" '
            f'viewBox="0 0 {panel["vw"]:g} {panel["vh"]:g}" overflow="visible">'
            f'{panel["inner"]}</svg>'
        )
        x += panel["w"] + GAP

    out = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{TARGET_W}" height="{height}" '
        f'viewBox="0 0 {TARGET_W} {height}" role="img" '
        f'aria-label="ASCII portrait and info card">{"".join(body)}</svg>'
    )
    dst = ROOT / "whoami.svg"
    dst.write_text(out, encoding="utf-8")
    print(f"wrote {dst}  ({TARGET_W}x{height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

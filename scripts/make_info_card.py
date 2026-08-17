"""Hand-author a neofetch-looking info card SVG.

Title bar, then colored key/value rows. Keep the content here and not in the
contribution graph -- the graph already covers the GitHub stats, so the card is
for the story numbers can't tell.

    python scripts/make_info_card.py     # writes info-card.svg
    STATIC=1 python scripts/make_info_card.py   # frozen frame, no animation
"""

import os
import re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent

# Rendered widths the README uses for the two side-by-side columns.
ASCII_COL_W = 370
CARD_COL_W = 490

# ---------------------------------------------------------------- EDIT ME ----
USER = "arta"
HOST = "jenesyx"
ROWS = [
    ("Now",        "Building artabidkhori.com + my own startup + Agentic OS"),
    ("Prev",       "Front-end work, UI design, small product builds"),
    ("Stack",      "React · Next.js · JavaScript · TypeScript · Node · Sass · Solidity · C / C#"),
    ("Highlights", "Design-to-code handoff, smart contracts, data-heavy UIs"),
    ("Learning",   "Everything, but mostly Ai and Data"),
    ("Reach",      "@jenesyx · artabidkhori.com"),
]
# ------------------------------------------------------------------------------

W = 700
PAD = 30
BAR_H = 38
FONT = 15
LINE_H = 24
MAX_LINE_H = 32     # cap so a tall card does not turn into double-spacing
BLOCK_GAP = 12
WRAP = 46          # characters per value line before wrapping

BG = "#0d1117"
BAR = "#161b22"
STROKE = "#21262d"
KEY = "#39d353"
VAL = "#c9d1d9"
DIM = "#8b949e"
ACCENT = "#58a6ff"

SWATCH = ["#161b22", "#0e4429", "#006d32", "#26a641",
          "#39d353", "#69f0a0", "#58a6ff", "#c9d1d9"]

MONO = ('ui-monospace, SFMono-Regular, Menlo, Consolas, '
        '&quot;DejaVu Sans Mono&quot;, monospace')


def wrap(text: str, width: int) -> list[str]:
    out, line = [], ""
    for word in text.split(" "):
        candidate = f"{line} {word}".strip()
        if len(candidate) > width and line:
            out.append(line)
            line = word
        else:
            line = candidate
    if line:
        out.append(line)
    return out


def build(target_h: float | None = None) -> str:
    static = os.environ.get("STATIC") == "1"
    key_w = max(len(k) for k, _ in ROWS) + 2

    # Lay the body out first so the panel height follows the content.
    items: list[tuple[str, str, str]] = []   # (key, value, kind)
    items.append(("", f"{USER}@{HOST}", "host"))
    items.append(("", "-" * (len(USER) + len(HOST) + 1), "rule"))
    for key, value in ROWS:
        for i, chunk in enumerate(wrap(value, WRAP)):
            items.append((key if i == 0 else "", chunk, "row"))

    body_top = BAR_H + BLOCK_GAP + PAD / 2
    chrome = body_top + BLOCK_GAP + 40 + PAD / 2
    line_h = LINE_H
    height = int(chrome + len(items) * LINE_H)
    if target_h and target_h > height:
        # Spend the slack on leading first, then leave the rest as bottom air.
        line_h = min(MAX_LINE_H, (target_h - chrome) / len(items))
        height = int(target_h)

    parts = [
        f'<rect width="{W}" height="{height}" rx="10" fill="{BG}"/>',
        f'<path d="M0 10a10 10 0 0 1 10-10h{W - 20}a10 10 0 0 1 10 10v{BAR_H - 10}H0z" fill="{BAR}"/>',
        f'<line x1="0" y1="{BAR_H}" x2="{W}" y2="{BAR_H}" stroke="{STROKE}"/>',
        f'<circle cx="24" cy="{BAR_H / 2}" r="6" fill="#ff5f56"/>',
        f'<circle cx="46" cy="{BAR_H / 2}" r="6" fill="#ffbd2e"/>',
        f'<circle cx="68" cy="{BAR_H / 2}" r="6" fill="#27c93f"/>',
        f'<text x="{W / 2}" y="{BAR_H / 2 + 5}" text-anchor="middle" font-size="13" '
        f'fill="{DIM}">{escape(USER)}@{escape(HOST)}: ~ — neofetch</text>',
    ]

    for i, (key, value, kind) in enumerate(items):
        y = body_top + i * line_h + FONT
        delay = "" if static else f' style="animation-delay:{0.09 * i + 0.15:.2f}s"'
        cls = "" if static else ' class="ln"'
        if kind == "host":
            parts.append(
                f'<text{cls}{delay} x="{PAD}" y="{y:.1f}" fill="{KEY}" '
                f'font-weight="700">{escape(value)}</text>'
            )
        elif kind == "rule":
            parts.append(
                f'<text{cls}{delay} x="{PAD}" y="{y:.1f}" fill="{DIM}">{escape(value)}</text>'
            )
        else:
            label = f"{key}:".ljust(key_w) if key else " " * key_w
            parts.append(
                f'<text{cls}{delay} x="{PAD}" y="{y:.1f}" xml:space="preserve">'
                f'<tspan fill="{KEY}" font-weight="700">{escape(label)}</tspan>'
                f'<tspan fill="{VAL if key else DIM}">{escape(value)}</tspan></text>'
            )

    sw_y = height - PAD - 12
    for i, color in enumerate(SWATCH):
        delay = "" if static else f' style="animation-delay:{0.09 * len(items) + 0.05 * i:.2f}s"'
        cls = "" if static else ' class="ln"'
        parts.append(
            f'<rect{cls}{delay} x="{PAD + i * 26}" y="{sw_y}" width="20" height="20" '
            f'rx="4" fill="{color}" stroke="{STROKE}"/>'
        )
    parts.append(
        f'<text x="{W - PAD}" y="{sw_y + 15}" text-anchor="end" font-size="12" '
        f'fill="{ACCENT}">./whoami --verbose</text>'
    )

    style = "" if static else (
        # animation-fill-mode:both (not forwards) hides the line during its
        # delay, and leaves it fully visible where animations never run.
        "<style>"
        "@keyframes in{from{opacity:0;transform:translateX(-14px)}"
        "to{opacity:1;transform:translateX(0)}}"
        ".ln{animation:in .42s ease-out both}"
        "@media (prefers-reduced-motion:reduce){.ln{animation:none}}"
        "</style>"
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}" role="img" aria-label="Profile info card">'
        f"{style}"
        f'<g font-family="{MONO}" font-size="{FONT}">{"".join(parts)}</g></svg>'
    )


def match_portrait_height() -> float | None:
    """Height that makes the card render as tall as the portrait beside it."""
    portrait = ROOT / "avi-ascii.svg"
    if not portrait.exists():
        return None
    head = portrait.read_text(encoding="utf-8")[:400]
    w = re.search(r'\bwidth="([\d.]+)"', head)
    h = re.search(r'\bheight="([\d.]+)"', head)
    if not (w and h):
        return None
    rendered = float(h.group(1)) / float(w.group(1)) * ASCII_COL_W
    return rendered / CARD_COL_W * W


def main() -> int:
    dst = ROOT / "info-card.svg"
    dst.write_text(build(match_portrait_height()), encoding="utf-8")
    print(f"wrote {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

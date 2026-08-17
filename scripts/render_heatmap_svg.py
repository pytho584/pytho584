"""Render data/contributions.json as the classic 53x7 calendar of rounded boxes.

Reveals once with a diagonal, line-after-line slide-down (CSS keyframes that
play on load, then freeze -- no looping glow), plus a Less->More legend and a
stats footer. Writes `contrib-heatmap.svg`.

    python scripts/render_heatmap_svg.py
"""

import json
import os
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent

PALETTE = ["#161b22", "#0e4429", "#006d32",
           "#26a641", "#39d353", "#69f0a0"]
#          none -> brightest (level 5 is a neon top end)

CELL = 12
GAP = 3
PITCH = CELL + GAP
PAD_L = 44
PAD_R = 24
BAR_H = 38
MONTH_Y = 60
GRID_T = 68
GRID_H = 7 * PITCH - GAP

BG = "#0d1117"
BAR = "#161b22"
STROKE = "#21262d"
DIM = "#8b949e"
VAL = "#c9d1d9"
KEY = "#39d353"

MONO = ('ui-monospace, SFMono-Regular, Menlo, Consolas, '
        '&quot;DejaVu Sans Mono&quot;, monospace')
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAYS = {1: "Mon", 3: "Wed", 5: "Fri"}


def col_row(day: date, origin: date) -> tuple[int, int]:
    row = (day.weekday() + 1) % 7          # Sunday-first, like GitHub
    return (day - origin).days // 7, row


def top_level_cutoff(days: list[dict]) -> int:
    """Counts at or above this get the neon level-5 colour."""
    hot = sorted(d["count"] for d in days if d["count"] > 0)
    if len(hot) < 20:
        return 10 ** 9
    return max(hot[int(len(hot) * 0.97)], 8)


def build(payload: dict, static: bool) -> str:
    days = payload["days"]
    stats = payload["stats"]

    first = date.fromisoformat(days[0]["date"])
    origin = first - timedelta(days=(first.weekday() + 1) % 7)
    weeks = col_row(date.fromisoformat(days[-1]["date"]), origin)[0] + 1

    grid_w = weeks * PITCH - GAP
    width = PAD_L + grid_w + PAD_R
    legend_y = GRID_T + GRID_H + 28
    footer_y = legend_y + 30
    height = footer_y + 22

    cutoff = top_level_cutoff(days)
    parts = [
        f'<rect width="{width}" height="{height}" rx="10" fill="{BG}"/>',
        f'<path d="M0 10a10 10 0 0 1 10-10h{width - 20}a10 10 0 0 1 10 10v{BAR_H - 10}H0z" fill="{BAR}"/>',
        f'<line x1="0" y1="{BAR_H}" x2="{width}" y2="{BAR_H}" stroke="{STROKE}"/>',
        f'<circle cx="24" cy="{BAR_H // 2}" r="6" fill="#ff5f56"/>',
        f'<circle cx="46" cy="{BAR_H // 2}" r="6" fill="#ffbd2e"/>',
        f'<circle cx="68" cy="{BAR_H // 2}" r="6" fill="#27c93f"/>',
        f'<text x="{width // 2}" y="{BAR_H // 2 + 5}" text-anchor="middle" font-size="13" '
        f'fill="{DIM}">{escape(payload["username"])} — contributions, last 12 months</text>',
    ]

    for row, label in WEEKDAYS.items():
        y = GRID_T + row * PITCH + CELL - 2
        parts.append(
            f'<text x="{PAD_L - 8}" y="{y}" text-anchor="end" font-size="10" '
            f'fill="{DIM}">{label}</text>'
        )

    last_month, last_col = None, -3
    for week in range(weeks):
        day = origin + timedelta(days=week * 7)
        if day.month != last_month and week - last_col >= 3:
            parts.append(
                f'<text x="{PAD_L + week * PITCH}" y="{MONTH_Y}" font-size="10" '
                f'fill="{DIM}">{MONTHS[day.month - 1]}</text>'
            )
            last_month, last_col = day.month, week
        elif day.month != last_month:
            last_month = day.month

    for entry in days:
        day = date.fromisoformat(entry["date"])
        week, row = col_row(day, origin)
        level = entry["level"]
        if level >= 4 and entry["count"] >= cutoff:
            level = 5
        x = PAD_L + week * PITCH
        y = GRID_T + row * PITCH
        delay = "" if static else f' style="animation-delay:{week * 0.017 + row * 0.045:.3f}s"'
        cls = "" if static else ' class="c"'
        plural = "" if entry["count"] == 1 else "s"
        parts.append(
            f'<rect{cls}{delay} x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{PALETTE[level]}" stroke="{STROKE}" stroke-width="0.5">'
            f'<title>{entry["count"]} contribution{plural} on {entry["date"]}</title></rect>'
        )

    legend_w = 6 * 17 + 74
    lx = width - PAD_R - legend_w
    parts.append(f'<text x="{lx}" y="{legend_y + 10}" font-size="11" fill="{DIM}">Less</text>')
    for i, color in enumerate(PALETTE):
        parts.append(
            f'<rect x="{lx + 34 + i * 17}" y="{legend_y}" width="{CELL}" height="{CELL}" '
            f'rx="2.5" fill="{color}" stroke="{STROKE}" stroke-width="0.5"/>'
        )
    parts.append(
        f'<text x="{lx + legend_w}" y="{legend_y + 10}" text-anchor="end" font-size="11" '
        f'fill="{DIM}">More</text>'
    )

    parts.append(
        f'<text x="{PAD_L}" y="{legend_y + 10}" font-size="13" fill="{VAL}">'
        f'<tspan fill="{KEY}" font-weight="700">{payload["total"]:,}</tspan>'
        f' contributions in the last year</text>'
    )
    best = stats["best_day"]
    footer = (
        f'current streak {stats["current_streak"]}d  ·  '
        f'longest {stats["longest_streak"]}d  ·  '
        f'best day {best["count"]} on {best["date"]}  ·  '
        f'{stats["daily_average"]}/day'
    )
    parts.append(
        f'<text x="{PAD_L}" y="{footer_y + 4}" font-size="11" fill="{DIM}">{escape(footer)}</text>'
    )

    style = "" if static else (
        # animation-fill-mode:both (not forwards) hides the cell during its
        # delay, and leaves the grid fully drawn where animations never run.
        "<style>"
        "@keyframes drop{from{opacity:0;transform:translateY(-9px)}"
        "to{opacity:1;transform:translateY(0)}}"
        ".c{animation:drop .5s ease-out both}"
        "@media (prefers-reduced-motion:reduce){.c{animation:none}}"
        "</style>"
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="{payload["total"]} contributions in the last year">'
        f"{style}"
        f'<g font-family="{MONO}">{"".join(parts)}</g></svg>'
    )


def main() -> int:
    src = ROOT / "data" / "contributions.json"
    if not src.exists():
        raise SystemExit("data/contributions.json missing -- run fetch_contributions.py first")
    payload = json.loads(src.read_text(encoding="utf-8"))
    dst = ROOT / "contrib-heatmap.svg"
    dst.write_text(build(payload, static=os.environ.get("STATIC") == "1"), encoding="utf-8")
    print(f"wrote {dst}  ({payload['total']} contributions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Scrape the public contribution calendar -- no token, no GraphQL.

GitHub serves the calendar as public HTML at
https://github.com/users/<username>/contributions -- the same fragment the
profile page itself uses. Writes `data/contributions.json` with the raw days
plus derived stats.

    python scripts/fetch_contributions.py
"""

import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
USERNAME = os.environ.get("GH_USERNAME", "Jenesyx")
URL = "https://github.com/users/{user}/contributions"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; profile-art/1.0; +https://github.com/{u})".format(u=USERNAME),
    "Accept": "text/html",
    "X-Requested-With": "XMLHttpRequest",
}
COUNT_RE = re.compile(r"^\s*(No|\d[\d,]*)\s+contribution")


def parse_count(text: str) -> int | None:
    m = COUNT_RE.match(text or "")
    if not m:
        return None
    token = m.group(1)
    return 0 if token == "No" else int(token.replace(",", ""))


def fetch_days(username: str) -> list[dict]:
    resp = requests.get(URL.format(user=username), headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Counts moved out of the <td> into sibling <tool-tip for="..."> elements.
    tips: dict[str, int] = {}
    for tip in soup.find_all("tool-tip"):
        target = tip.get("for")
        count = parse_count(tip.get_text(" ", strip=True))
        if target and count is not None:
            tips[target] = count

    today = date.today()
    days: list[dict] = []
    for cell in soup.select("td.ContributionCalendar-day"):
        iso = cell.get("data-date")
        if not iso:
            continue
        if date.fromisoformat(iso) > today:
            continue  # calendar pads out the current week
        count = tips.get(cell.get("id") or "")
        if count is None and cell.get("data-count") is not None:
            count = int(cell["data-count"])
        if count is None:
            sr = cell.find("span", class_="sr-only")
            count = parse_count(sr.get_text(" ", strip=True)) if sr else None
        days.append({
            "date": iso,
            "count": int(count or 0),
            "level": int(cell.get("data-level") or 0),
        })

    if not days:
        raise SystemExit("no day cells parsed -- GitHub markup may have changed")
    days.sort(key=lambda d: d["date"])
    return days


def streaks(days: list[dict]) -> tuple[int, int, dict]:
    longest = run = 0
    best = {"date": None, "count": 0}
    for day in days:
        run = run + 1 if day["count"] > 0 else 0
        longest = max(longest, run)
        if day["count"] > best["count"]:
            best = {"date": day["date"], "count": day["count"]}

    current = 0
    tail = list(reversed(days))
    # An empty today does not break the streak -- the day is not over yet.
    if tail and tail[0]["count"] == 0:
        tail = tail[1:]
    for day in tail:
        if day["count"] == 0:
            break
        current += 1
    return current, longest, best


def main() -> int:
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME
    days = fetch_days(username)
    current, longest, best = streaks(days)

    monthly: dict[str, int] = defaultdict(int)
    for day in days:
        monthly[day["date"][:7]] += day["count"]

    total = sum(d["count"] for d in days)
    active = sum(1 for d in days if d["count"] > 0)
    payload = {
        "username": username,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "range": {"from": days[0]["date"], "to": days[-1]["date"]},
        "total": total,
        "days": days,
        "stats": {
            "current_streak": current,
            "longest_streak": longest,
            "best_day": best,
            "active_days": active,
            "daily_average": round(total / max(1, len(days)), 2),
            "monthly": dict(sorted(monthly.items())),
        },
    }

    out = ROOT / "data" / "contributions.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out}  ({total} contributions over {len(days)} days)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

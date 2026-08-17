"""Generate the Ember Command profile art from GitHub's public REST API.

No third-party stats service and no Python packages are required.

    python scripts/generate.py          # live GitHub data
    python scripts/generate.py --demo   # deterministic preview data
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
CONFIG = ROOT / "config.json"

BG = "#090708"
SHELL = "#171012"
CORE = "#0f0b0c"
HAIR = "#4b2524"
RED = "#ff4d3d"
ORANGE = "#ff8a1f"
GOLD = "#ffc857"
CREAM = "#fff4e6"
MUTED = "#bda7a2"

DEMO = {
    "public_repos": 86,
    "followers": 34,
    "following": 18,
    "stars": 119,
    "languages": [["TypeScript", 36], ["JavaScript", 28], ["Python", 17], ["CSS", 11], ["Other", 8]],
    "repos": [
        {"name": "Zeropoint-website", "description": "A sharp digital home for an ambitious product team.", "language": "TypeScript", "stargazers_count": 42, "forks_count": 8},
        {"name": "Jenesyx-Website", "description": "Personal portfolio, experiments and selected client work.", "language": "JavaScript", "stargazers_count": 31, "forks_count": 5},
        {"name": "TodoList", "description": "A focused task system with a clean interaction model.", "language": "TypeScript", "stargazers_count": 27, "forks_count": 4},
        {"name": "404Error-page", "description": "A playful, responsive not-found page concept.", "language": "CSS", "stargazers_count": 19, "forks_count": 3},
    ],
}


def load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def request_json(url: str) -> object:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "ember-command-profile"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.load(response)


def live_data(username: str, featured: list[str]) -> dict:
    user = request_json(f"https://api.github.com/users/{username}")
    repos = request_json(f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated")
    if not isinstance(user, dict) or not isinstance(repos, list):
        raise RuntimeError("Unexpected response from GitHub")

    original = [repo for repo in repos if not repo.get("fork")]
    by_name = {repo.get("name", "").lower(): repo for repo in original}
    chosen = [by_name[name.lower()] for name in featured if name.lower() in by_name]
    chosen_names = {repo.get("name") for repo in chosen}
    for repo in sorted(original, key=lambda item: (item.get("stargazers_count", 0), item.get("updated_at", "")), reverse=True):
        if repo.get("name") not in chosen_names and len(chosen) < 4:
            chosen.append(repo)

    language_counts: dict[str, int] = {}
    for repo in original:
        language = repo.get("language")
        if language:
            language_counts[language] = language_counts.get(language, 0) + 1
    languages = sorted(language_counts.items(), key=lambda item: item[1], reverse=True)[:5]

    return {
        "public_repos": user.get("public_repos", len(repos)),
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "stars": sum(repo.get("stargazers_count", 0) for repo in original),
        "languages": languages,
        "repos": chosen[:4],
    }


def clip(value: object, length: int) -> str:
    text = " ".join(str(value or "").split())
    return text if len(text) <= length else text[: length - 1].rstrip() + "…"


def hero_svg(config: dict, stats: dict) -> str:
    skills = "".join(
        f'<g transform="translate({42 + (index % 3) * 162} {248 + (index // 3) * 34})">'
        f'<rect width="146" height="24" rx="12" fill="#211315" stroke="#66302b"/>'
        f'<text x="73" y="16" text-anchor="middle" class="tag">{escape(skill)}</text></g>'
        for index, skill in enumerate(config["skills"][:6])
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="330" viewBox="0 0 900 330" role="img" aria-label="Profile banner for {escape(config['name'])}">
<defs>
  <radialGradient id="flare" cx="78%" cy="42%" r="54%"><stop offset="0" stop-color="{RED}" stop-opacity=".32"/><stop offset=".46" stop-color="{ORANGE}" stop-opacity=".1"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
  <linearGradient id="rim" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{RED}"/><stop offset=".52" stop-color="{ORANGE}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient>
  <filter id="glow"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <style>.display{{font:700 42px 'Trebuchet MS',sans-serif;fill:{CREAM};letter-spacing:-1.2px}}.label{{font:700 10px 'Trebuchet MS',sans-serif;fill:{ORANGE};letter-spacing:2px}}.body{{font:14px 'Trebuchet MS',sans-serif;fill:{MUTED}}}.tag{{font:700 11px 'Trebuchet MS',sans-serif;fill:{CREAM};}}.num{{font:700 38px 'Trebuchet MS',sans-serif;fill:{CREAM};}}.tiny{{font:10px 'Trebuchet MS',sans-serif;fill:{MUTED};letter-spacing:1.2px}}@keyframes drift{{50%{{transform:rotate(7deg)}}}}@keyframes rise{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}.orbit{{transform-origin:730px 156px;animation:drift 7s cubic-bezier(.32,.72,0,1) infinite}}.intro{{animation:rise .9s cubic-bezier(.32,.72,0,1) both}}@media(prefers-reduced-motion:reduce){{.orbit,.intro{{animation:none}}}}</style>
</defs>
<rect width="900" height="330" rx="26" fill="{SHELL}"/><rect x="7" y="7" width="886" height="316" rx="21" fill="{CORE}" stroke="{HAIR}"/><rect x="7" y="7" width="886" height="316" rx="21" fill="url(#flare)"/>
<path d="M29 41h330" stroke="url(#rim)" stroke-width="2"/><circle cx="29" cy="41" r="4" fill="{RED}"/><text x="42" y="69" class="label">EMBER COMMAND / PROFILE 01</text>
<g class="intro"><text x="42" y="123" class="display">{escape(config['name'])}</text><text x="42" y="152" class="body">{escape(config['role'])}</text><text x="42" y="178" class="body">{escape(config['location'])}</text><text x="42" y="212" class="label">CURRENT VECTOR</text><text x="42" y="234" class="body">{escape(config['focus'])}</text>{skills}</g>
<g class="orbit"><circle cx="730" cy="156" r="108" fill="none" stroke="#5d2925"/><circle cx="730" cy="156" r="82" fill="none" stroke="#351919" stroke-dasharray="3 8"/><path d="M635 107a108 108 0 0 1 188 104" fill="none" stroke="url(#rim)" stroke-width="3" stroke-linecap="round"/><circle cx="635" cy="107" r="6" fill="{RED}" filter="url(#glow)"/><circle cx="823" cy="211" r="5" fill="{GOLD}"/></g>
<text x="730" y="146" text-anchor="middle" class="num">{stats['stars']}</text><text x="730" y="168" text-anchor="middle" class="tiny">TOTAL STARS</text><text x="730" y="193" text-anchor="middle" class="label">{stats['public_repos']} REPOSITORIES</text>
<text x="858" y="318" text-anchor="end" class="tiny">STATUS / {escape(clip(config['status'], 52)).upper()}</text>
</svg>'''


def signal_svg(config: dict, stats: dict) -> str:
    metrics = [("REPOSITORIES", stats["public_repos"]), ("TOTAL STARS", stats["stars"]), ("FOLLOWERS", stats["followers"]), ("FOLLOWING", stats["following"])]
    metric_nodes = []
    for index, (label, value) in enumerate(metrics):
        x = 31 + index * 212
        metric_nodes.append(f'<g transform="translate({x} 65)" class="reveal" style="animation-delay:{index * .09:.2f}s"><rect width="195" height="91" rx="15" fill="#140e0f" stroke="#4d2523"/><text x="16" y="26" class="label">{label}</text><text x="16" y="65" class="metric">{value}</text><path d="M132 67h45" stroke="#41201e" stroke-width="5" stroke-linecap="round"/><path d="M132 67h{12 + min(33, int(value) % 34)}" stroke="{[RED, ORANGE, GOLD, '#ff6b50'][index]}" stroke-width="5" stroke-linecap="round"/></g>')

    total = max(1, sum(count for _, count in stats["languages"]))
    lang_nodes = []
    for index, (language, count) in enumerate(stats["languages"][:5]):
        y = 218 + index * 36
        width = max(18, int(278 * count / total))
        color = [RED, ORANGE, GOLD, "#ff6b50", "#d94836"][index]
        lang_nodes.append(f'<text x="50" y="{y}" class="body strong">{escape(language)}</text><text x="164" y="{y}" class="mono">{round(count / total * 100)}%</text><rect x="210" y="{y - 11}" width="278" height="8" rx="4" fill="#30191a"/><rect x="210" y="{y - 11}" width="{width}" height="8" rx="4" fill="{color}" class="bar" style="animation-delay:{index * .08:.2f}s"/>')

    repo_nodes = []
    for index, repo in enumerate(stats["repos"][:4]):
        col, row = index % 2, index // 2
        x, y = 523 + col * 172, 205 + row * 111
        repo_nodes.append(f'<g transform="translate({x} {y})" class="reveal" style="animation-delay:{.2 + index * .08:.2f}s"><rect width="157" height="95" rx="13" fill="#140e0f" stroke="#4d2523"/><circle cx="18" cy="19" r="4" fill="{ORANGE if index % 2 else RED}"/><text x="30" y="23" class="repo">{escape(clip(repo.get("name"), 17))}</text><text x="15" y="48" class="desc">{escape(clip(repo.get("description") or "No description yet", 23))}</text><text x="15" y="77" class="mono">★ {repo.get('stargazers_count', 0)}  ·  {escape(repo.get('language') or 'Mixed')}</text></g>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="445" viewBox="0 0 900 445" role="img" aria-label="GitHub signal dashboard for {escape(config['username'])}">
<defs><linearGradient id="line"><stop stop-color="{RED}"/><stop offset=".5" stop-color="{ORANGE}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient><style>.title{{font:700 25px 'Trebuchet MS',sans-serif;fill:{CREAM};}}.label{{font:700 9px 'Trebuchet MS',sans-serif;fill:{ORANGE};letter-spacing:1.5px}}.metric{{font:700 31px 'Trebuchet MS',sans-serif;fill:{CREAM};}}.body{{font:12px 'Trebuchet MS',sans-serif;fill:{MUTED};}}.strong{{font-weight:700;fill:{CREAM};}}.mono{{font:10px ui-monospace,Consolas,monospace;fill:{MUTED};}}.repo{{font:700 10px 'Trebuchet MS',sans-serif;fill:{CREAM};}}.desc{{font:9px 'Trebuchet MS',sans-serif;fill:{MUTED};}}@keyframes reveal{{from{{opacity:0}}to{{opacity:1}}}}@keyframes grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}.reveal{{animation:reveal .7s cubic-bezier(.32,.72,0,1) both}}.bar{{transform-origin:left;animation:grow .8s cubic-bezier(.32,.72,0,1) both}}@media(prefers-reduced-motion:reduce){{.reveal,.bar{{animation:none}}}}</style></defs>
<rect width="900" height="445" rx="26" fill="{SHELL}"/><rect x="7" y="7" width="886" height="431" rx="21" fill="{CORE}" stroke="{HAIR}"/><path d="M29 42h842" stroke="url(#line)"/><text x="31" y="39" class="label">LIVE TELEMETRY / @{escape(config['username'].upper())}</text>{''.join(metric_nodes)}
<text x="31" y="190" class="title">Language ignition</text><text x="523" y="190" class="title">Selected transmissions</text>{''.join(lang_nodes)}{''.join(repo_nodes)}
<text x="31" y="427" class="mono">Generated from GitHub public data · no external stats service</text><text x="869" y="427" text-anchor="end" class="label">SYSTEM NOMINAL</text>
</svg>'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="use deterministic preview data")
    args = parser.parse_args()
    config = load_config()
    username = os.environ.get("GH_USERNAME") or os.environ.get("GITHUB_REPOSITORY_OWNER") or config["username"]
    config["username"] = username
    if args.demo:
        stats = DEMO
    else:
        try:
            stats = live_data(username, config.get("featured_repos", []))
        except (urllib.error.URLError, RuntimeError) as exc:
            raise SystemExit(f"GitHub data request failed: {exc}. Use --demo for an offline preview.")
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "hero.svg").write_text(hero_svg(config, stats), encoding="utf-8")
    (ASSETS / "signal.svg").write_text(signal_svg(config, stats), encoding="utf-8")
    print(f"Generated Ember Command assets for @{username}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

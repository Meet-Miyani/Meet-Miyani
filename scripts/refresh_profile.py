#!/usr/bin/env python3
"""Fetch live profile data and regenerate every animated SVG + README blocks.

    python scripts/refresh_profile.py            # live (used by GitHub Actions)
    python scripts/refresh_profile.py --sample   # offline preview with last-known values

Env:
    GITHUB_TOKEN   the default Actions token; only used to avoid REST rate limits.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import profile_svgs as kit  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
README_PATH = ROOT / "README.md"
ASSETS = ROOT / "assets"

GITHUB_USERNAME = "Meet-Miyani"
STACKOVERFLOW_USER_ID = "20559937"
MEDIUM_FEED_URL = "https://meet-miyani.medium.com/feed"

PLAY_APPS = [
    {"name": "RingFit", "package": "avinya.tech.ringfit"},
    {"name": "ViewTube", "package": "avinya.tech.yt"},
    {"name": "QR Code Generator", "package": "avinya.tech.qrcode"},
    {"name": "CricScore", "package": "avinya.tech.cricscore"},
]
for _app in PLAY_APPS:
    _app["url"] = f"https://play.google.com/store/apps/details?id={_app['package']}"

# Last-known values, used by --sample and as a per-source fallback if a fetch fails.
FALLBACK = {
    "github": {"followers": 22, "public_repos": 8, "total_stars": 345, "compose_skill_stars": 305,
               "eventics_stars": 0, "admob_cmp_stars": 35, "skilllint_stars": 1, "languages": {"Kotlin": 6, "Java": 1, "Python": 1}},
    "stackoverflow": {"reputation": 99, "bronze_badges": 6},
    "medium": {"story_count": 9, "items": [
        {"title": "How to Add AdMob to a Compose Multiplatform App on Android and iOS",
         "link": "https://meet-miyani.medium.com/admob-compose-multiplatform-android-ios-guide-a46a8be696a7",
         "date": "2026"},
    ]},
    "play": {"apps": [dict(a, installs=i) for a, i in zip(PLAY_APPS, ["500K+", "100K+", "1K+", "5K+"])]},
}


# ───────────────────────── fetching ─────────────────────────

def run_curl(url: str, *, headers: dict[str, str] | None = None, data: str | None = None) -> str:
    cmd = ["curl", "-fsSL", "--max-time", "30"]
    for key, value in (headers or {}).items():
        cmd.extend(["-H", f"{key}: {value}"])
    if data is not None:
        cmd.extend(["-X", "POST", "--data", data])
    cmd.append(url)
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def fetch_json(url: str, **kw) -> object:
    return json.loads(run_curl(url, **kw))


def gh_headers() -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def compact_number(value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}".rstrip("0").rstrip(".") + "M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}".rstrip("0").rstrip(".") + "K"
    return str(value)


def parse_install_floor(value: str) -> int:
    cleaned = value.strip().replace(",", "").replace("+", "")
    mult = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}.get(cleaned[-1:], 1)
    if mult > 1:
        cleaned = cleaned[:-1]
    return int(float(cleaned) * mult)


def fetch_github() -> dict:
    h = gh_headers()
    user = fetch_json(f"https://api.github.com/users/{GITHUB_USERNAME}", headers=h)
    repos = fetch_json(f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100", headers=h)
    by_name = {r["name"]: r for r in repos if isinstance(r, dict)}
    languages: dict[str, int] = {}
    for r in by_name.values():
        if r.get("fork") or not r.get("language"):
            continue
        languages[r["language"]] = languages.get(r["language"], 0) + 1
    return {
        "followers": int(user.get("followers", 0)),
        "public_repos": int(user.get("public_repos", 0)),
        "total_stars": sum(int(r.get("stargazers_count", 0)) for r in by_name.values()),
        "compose_skill_stars": int(by_name.get("compose-skill", {}).get("stargazers_count", 0)),
        "eventics_stars": int(by_name.get("Eventics", {}).get("stargazers_count", 0)),
        "admob_cmp_stars": int(by_name.get("admob-compose-multiplatform", {}).get("stargazers_count", 0)),
        "skilllint_stars": int(by_name.get("agent-skill-validator", {}).get("stargazers_count", 0)),
        "languages": languages,
    }


def fetch_stackoverflow() -> dict:
    payload = fetch_json(f"https://api.stackexchange.com/2.3/users/{STACKOVERFLOW_USER_ID}?site=stackoverflow")
    user = payload["items"][0]
    return {"reputation": int(user.get("reputation", 0)),
            "bronze_badges": int(user.get("badge_counts", {}).get("bronze", 0))}


def fetch_medium() -> dict:
    channel = ET.fromstring(run_curl(MEDIUM_FEED_URL)).find("channel")
    items = []
    for it in channel.findall("item"):
        link = it.findtext("link", "").strip().split("?")[0]
        pub = it.findtext("pubDate", "").strip()
        try:
            date = dt.datetime.strptime(pub[:16], "%a, %d %b %Y").strftime("%b %Y")
        except ValueError:
            date = ""
        items.append({"title": it.findtext("title", "").strip(), "link": link, "date": date})
    return {"story_count": len(items), "items": items}


def fetch_play() -> dict:
    apps = []
    for app in PLAY_APPS:
        page = run_curl(f"{app['url']}&hl=en_US&gl=US")
        match = re.search(r">([0-9][0-9,\.]*[KMB]?\+)<", page)
        if not match:
            raise ValueError(f"Install count not found for {app['name']}")
        apps.append({**app, "installs": match.group(1)})
    return {"apps": apps}


def gather(sample: bool) -> dict:
    data: dict = {}
    sources = {
        "github": fetch_github, "stackoverflow": fetch_stackoverflow,
        "medium": fetch_medium, "play": fetch_play,
    }
    for key, fn in sources.items():
        if sample:
            data[key] = FALLBACK.get(key)
            continue
        try:
            data[key] = fn()
        except Exception as exc:  # keep the profile rendering even if one source is down
            print(f"warn: {key} fetch failed ({exc}); using fallback", file=sys.stderr)
            data[key] = FALLBACK.get(key)
    floor = sum(parse_install_floor(a["installs"]) for a in data["play"]["apps"])
    data["play"]["total_installs_floor"] = floor
    data["play"]["total_installs_display"] = f"{compact_number(floor)}+"
    data["updated"] = dt.datetime.now(dt.timezone.utc).strftime("%b %d, %Y")
    return data


# ───────────────────────── content ─────────────────────────

PROFILE = {
    "name": "Meet Miyani",
    "role": "Senior Android & Compose Multiplatform Developer",
    "location": "Surat, India · UTC+5:30",
    "availability": "Open to remote roles",
    "keywords": ["Kotlin", "Compose Multiplatform", "Jetpack Compose", "Android + iOS"],
    "now": "Android @ Haat Delivery",
}

EXPERIENCE = [
    {"when": "2023 — now", "org": "Haat Delivery", "title": "Android Developer, remote (Israel)",
     "note": "Now building Haat Partner+ in Compose Multiplatform.\nEarlier: one shared library across 3 apps, and ~90% fewer OOM crashes in the Driver app."},
    {"when": "2022 — 2023", "org": "Freelance", "title": "Android Developer",
     "note": "BLE/IoT and medical-device integrations, media apps — 10+ client projects end to end."},
    {"when": "2021 — 2022", "org": "Vasundhara Infotech", "title": "Android Developer, Surat",
     "note": "R&D on Canvas, GLSL shaders and on-device ML for creative and video-editing apps."},
]

GH = "https://github.com/Meet-Miyani"


def stars(n: int) -> str:
    return f"{n} ★" if n >= 5 else ""


def oss_items(data: dict) -> list[dict]:
    """Open source, framed the way it was built: a recurring problem, then the tool that removes it."""
    gh = data["github"]
    return [
        {"name": "Compose Kit", "url": f"{GH}/compose-skill", "meta": stars(gh["compose_skill_stars"]),
         "site": ("compose.avinya.dev", "https://compose.avinya.dev"),
         "desc": "Seven agent skills that make Claude Code, Codex, Cursor, Copilot and Gemini write better Jetpack Compose "
                 "and Compose Multiplatform code. Tested across 126 agentic runs on seven models, with two blind graders per item."},
        {"name": "AdMob CMP", "url": f"{GH}/admob-compose-multiplatform", "meta": stars(gh.get("admob_cmp_stars", 0)),
         "site": ("ads.avinya.dev", "https://ads.avinya.dev"),
         "desc": "A Compose Multiplatform AdMob SDK for Android and iOS. Banner, interstitial, rewarded, app-open and native ads "
                 "from one `commonMain` API, with UMP consent built in. Published on Maven Central."},
        {"name": "SkillLint", "url": f"{GH}/agent-skill-validator", "meta": stars(gh.get("skilllint_stars", 0)), "site": None,
         "desc": "A validator for AI agent skills that runs entirely in the browser: structure, links, token budget and security checks."},
        {"name": "Eventics", "url": f"{GH}/Eventics", "meta": stars(gh.get("eventics_stars", 0)), "site": None,
         "desc": "An Android event-logging library. KSP turns typed event classes into generated analytics payload code."},
    ]


def app_items(data: dict) -> list[dict]:
    by_name = {a["name"]: a for a in data["play"]["apps"]}
    play = lambda name: f"{by_name[name]['installs']} installs"  # noqa: E731
    return [
        {"name": "ViewTube", "url": by_name["ViewTube"]["url"], "meta": play("ViewTube"), "short": "Android and iOS from one Kotlin codebase.",
         "desc": "A video player for Android and iOS from one Kotlin codebase, built with Compose Multiplatform. Media3 on Android "
                 "and AVPlayer on iOS sit behind a single Kotlin API. It runs on AdMob CMP and is built with Compose Kit."},
        {"name": "RingFit", "url": by_name["RingFit"]["url"], "meta": play("RingFit"), "short": "Ring sizing with a custom ruler built on Canvas.",
         "desc": "A ring-size measurement app for Android with a custom ruler built on Canvas."},
        {"name": "QR Code Generator", "url": by_name["QR Code Generator"]["url"], "meta": play("QR Code Generator"),
         "short": "Customizable QR codes: colors, eyes, patterns, gradients.",
         "desc": "Customizable QR codes drawn on Canvas: colors, eyes, patterns and gradients."},
        {"name": "CricScore", "url": by_name["CricScore"]["url"], "meta": play("CricScore"), "short": "Live cricket scores, series and scorecards.",
         "desc": "Live cricket scores, series and scorecards with MotionLayout animations and Paging 3."},
    ]


def render_list(items: list[dict]) -> str:
    rows = []
    for item in items:
        meta = f" `{item['meta']}`" if item["meta"] else ""
        site = f" · [{item['site'][0]}]({item['site'][1]})" if item.get("site") else ""
        rows.append(f"- **[{item['name']}]({item['url']})**{meta}{site}<br>{item['desc']}")
    return "\n".join(rows)


def figures(data: dict) -> list[tuple[str, str]]:
    return [
        (data["play"]["total_installs_display"], "installs across\nmy Play Store apps"),
        ("~90%", "fewer OOM crashes after\nthe Haat Driver-app rework"),
        (f"{data['github']['compose_skill_stars']}", "stars on Compose Kit,\nmy agent skills for Compose"),
        ("2", "platforms from one codebase:\nViewTube on Android and iOS"),
    ]


def write_assets(data: dict) -> list[Path]:
    out = ASSETS / "svg"
    out.mkdir(parents=True, exist_ok=True)
    data = {**data, "profile": PROFILE, "experience": EXPERIENCE, "figures": figures(data)}
    written = []
    for theme, tokens in kit.THEMES.items():
        files = {
            "header": kit.build_header(data, tokens),
            "figures": kit.build_figures(data, tokens),
            "experience": kit.build_experience(data, tokens),
        }
        for name, svg in files.items():
            path = out / f"{name}-{theme}.svg"
            path.write_text(svg, encoding="utf-8")
            written.append(path)
    return written


def replace_marker_block(text: str, marker: str, replacement: str) -> str:
    pattern = re.compile(rf"<!-- {re.escape(marker)}:start -->.*?<!-- {re.escape(marker)}:end -->", re.DOTALL)
    updated, count = pattern.subn(lambda _: f"<!-- {marker}:start -->\n{replacement}\n<!-- {marker}:end -->", text)
    if count != 1:
        raise ValueError(f"Marker block not found exactly once: {marker}")
    return updated


def render_writing(data: dict) -> str:
    md = data["medium"]
    so = data["stackoverflow"]
    rows = []
    for item in md["items"][:4]:
        date = f" · {html.escape(item['date'])}" if item.get("date") else ""
        rows.append(f"- [{html.escape(item['title'])}]({item['link']}){date}")
    rows.append("")
    rows.append(
        f"<sub>{md['story_count']} stories on <a href=\"https://meet-miyani.medium.com/\">Medium</a> · "
        f"3 Kotlin deep-dives on <a href=\"https://bugfender.com/author/meet-miyani/\">Bugfender</a> · "
        f"{so['reputation']} rep on <a href=\"https://stackoverflow.com/users/{STACKOVERFLOW_USER_ID}/meet-miyani\">Stack Overflow</a></sub>"
    )
    return "\n".join(rows)


def refresh_readme(data: dict) -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    readme = replace_marker_block(readme, "dynamic-writing", render_writing(data))
    readme = replace_marker_block(readme, "dynamic-oss", render_list(oss_items(data)))
    readme = replace_marker_block(readme, "dynamic-apps", render_list(app_items(data)))
    readme = replace_marker_block(readme, "dynamic-updated", f"<sub>Numbers refresh daily · last run {data['updated']}</sub>")
    README_PATH.write_text(readme, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true", help="offline preview with last-known values")
    parser.add_argument("--no-readme", action="store_true")
    args = parser.parse_args()
    data = gather(args.sample)
    for p in write_assets(data):
        print("wrote", p.relative_to(ROOT))
    if not args.no_readme:
        refresh_readme(data)


if __name__ == "__main__":
    main()

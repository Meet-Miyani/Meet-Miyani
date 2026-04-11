#!/usr/bin/env python3

from __future__ import annotations

import datetime as dt
import html
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from generate_profile_banner import build_svg


ROOT = Path(__file__).resolve().parents[1]
README_PATH = ROOT / "README.md"
BANNER_PATH = ROOT / "assets" / "profile-banner.svg"

GITHUB_USERNAME = "Meet-Miyani"
STACKOVERFLOW_USER_ID = "20559937"
MEDIUM_FEED_URL = "https://meet-miyani.medium.com/feed"
PLAY_DEVELOPER_URL = "https://play.google.com/store/apps/dev?id=7045442356661226869"

PLAY_APPS = [
    {
        "name": "RingFit",
        "package": "avinya.tech.ringfit",
        "url": "https://play.google.com/store/apps/details?id=avinya.tech.ringfit",
    },
    {
        "name": "ViewTube",
        "package": "avinya.tech.yt",
        "url": "https://play.google.com/store/apps/details?id=avinya.tech.yt",
    },
    {
        "name": "QR Code Generator",
        "package": "avinya.tech.qrcode",
        "url": "https://play.google.com/store/apps/details?id=avinya.tech.qrcode",
    },
    {
        "name": "CricScore",
        "package": "avinya.tech.cricscore",
        "url": "https://play.google.com/store/apps/details?id=avinya.tech.cricscore",
    },
]


def run_curl(url: str, *, headers: dict[str, str] | None = None) -> str:
    cmd = ["curl", "-fsSL"]
    for key, value in (headers or {}).items():
        cmd.extend(["-H", f"{key}: {value}"])
    cmd.append(url)
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return result.stdout


def fetch_json(url: str, *, headers: dict[str, str] | None = None) -> object:
    return json.loads(run_curl(url, headers=headers))


def compact_number(value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}".rstrip("0").rstrip(".") + "M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}".rstrip("0").rstrip(".") + "K"
    return str(value)


def parse_install_floor(value: str) -> int:
    cleaned = value.strip().replace(",", "").replace("+", "")
    multiplier = 1
    if cleaned.endswith("K"):
        multiplier = 1_000
        cleaned = cleaned[:-1]
    elif cleaned.endswith("M"):
        multiplier = 1_000_000
        cleaned = cleaned[:-1]
    elif cleaned.endswith("B"):
        multiplier = 1_000_000_000
        cleaned = cleaned[:-1]
    return int(float(cleaned) * multiplier)


def fetch_github_metrics() -> dict[str, object]:
    headers = {"Accept": "application/vnd.github+json"}
    token = subprocess.os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    user = fetch_json(f"https://api.github.com/users/{GITHUB_USERNAME}", headers=headers)
    repos = fetch_json(
        f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100",
        headers=headers,
    )

    if not isinstance(user, dict) or not isinstance(repos, list):
        raise ValueError("Unexpected GitHub API response")

    repo_map = {
        repo["name"]: repo
        for repo in repos
        if isinstance(repo, dict) and "name" in repo
    }
    total_stars = sum(int(repo.get("stargazers_count", 0)) for repo in repo_map.values())

    return {
        "followers": int(user.get("followers", 0)),
        "public_repos": int(user.get("public_repos", 0)),
        "total_stars": total_stars,
        "compose_skill_stars": int(repo_map.get("compose-skill", {}).get("stargazers_count", 0)),
        "eventics_stars": int(repo_map.get("Eventics", {}).get("stargazers_count", 0)),
    }


def fetch_stackoverflow_metrics() -> dict[str, int]:
    payload = fetch_json(
        f"https://api.stackexchange.com/2.3/users/{STACKOVERFLOW_USER_ID}?site=stackoverflow"
    )
    if not isinstance(payload, dict) or not payload.get("items"):
        raise ValueError("Unexpected Stack Overflow response")
    user = payload["items"][0]
    badge_counts = user.get("badge_counts", {})
    return {
        "reputation": int(user.get("reputation", 0)),
        "bronze_badges": int(badge_counts.get("bronze", 0)),
    }


def fetch_medium_metrics() -> dict[str, str | int]:
    xml_text = run_curl(MEDIUM_FEED_URL)
    root = ET.fromstring(xml_text)
    channel = root.find("channel")
    if channel is None:
        raise ValueError("Medium RSS channel not found")

    items = channel.findall("item")
    latest = items[0] if items else None
    latest_title = latest.findtext("title", "").strip() if latest is not None else ""
    latest_link = latest.findtext("link", "").strip() if latest is not None else ""
    return {
        "story_count": len(items),
        "latest_title": latest_title,
        "latest_link": latest_link,
    }


def fetch_play_store_metrics() -> dict[str, object]:
    apps: list[dict[str, object]] = []
    total_floor = 0

    for app in PLAY_APPS:
        url = f"https://play.google.com/store/apps/details?id={app['package']}&hl=en_US&gl=US"
        html_text = run_curl(url)
        matches = re.findall(r">([0-9][0-9,\.]*[KMB]?\+)<", html_text)
        if not matches:
            raise ValueError(f"Install count not found for {app['name']}")
        installs = matches[0]
        total_floor += parse_install_floor(installs)
        apps.append({**app, "installs": installs})

    return {
        "apps": apps,
        "total_installs_floor": total_floor,
        "total_installs_display": f"{compact_number(total_floor)}+",
    }


def replace_marker_block(text: str, marker: str, replacement: str) -> str:
    pattern = re.compile(
        rf"<!-- {re.escape(marker)}:start -->.*?<!-- {re.escape(marker)}:end -->",
        re.DOTALL,
    )
    block = f"<!-- {marker}:start -->\n{replacement}\n<!-- {marker}:end -->"
    updated, count = pattern.subn(block, text)
    if count != 1:
        raise ValueError(f"Marker block not found exactly once: {marker}")
    return updated


def render_live_metrics(data: dict[str, object], updated_label: str) -> str:
    github = data["github"]
    medium = data["medium"]
    play = data["play"]

    return f"""<table>
  <tr>
    <td align="center"><strong>{github['followers']}</strong><br/><sub>GitHub followers</sub></td>
    <td align="center"><strong>{github['total_stars']}</strong><br/><sub>Repo stars</sub></td>
    <td align="center"><strong>{github['public_repos']}</strong><br/><sub>Public repos</sub></td>
    <td align="center"><strong>{medium['story_count']}</strong><br/><sub>Medium stories</sub></td>
    <td align="center"><strong>{play['total_installs_display']}</strong><br/><sub>Play Store installs</sub></td>
  </tr>
</table>
<p align="center"><sub>Refreshed {updated_label} UTC · auto-updated daily via GitHub Actions</sub></p>"""


def render_selected_work(data: dict[str, object]) -> str:
    github = data["github"]
    apps_by_name = {app["name"]: app for app in data["play"]["apps"]}

    return f"""<table>
  <tr>
    <td valign="top" width="50%">
      <strong><a href="https://github.com/Meet-Miyani/compose-skill">compose-skill</a></strong> · <code>{github['compose_skill_stars']} ★</code><br/><br/>
      Reference skill for AI coding agents working in Jetpack Compose and Compose Multiplatform. Covers MVI, Navigation 3, Koin/Hilt, Ktor, data layers, Paging 3, animations, performance, testing, and CMP cross-platform patterns.
    </td>
    <td valign="top" width="50%">
      <strong><a href="https://github.com/Meet-Miyani/Eventics">Eventics</a></strong><br/><br/>
      KSP-powered Android event logging library. Define typed event classes with annotations, get generated analytics payload code — no manual wiring.
    </td>
  </tr>
  <tr>
    <td valign="top" width="50%">
      <strong><a href="https://play.google.com/store/apps/details?id=avinya.tech.ringfit">RingFit</a></strong> · <code>{apps_by_name['RingFit']['installs']} installs</code><br/><br/>
      Ring size measurement app with a custom canvas-drawn ruler. Built solo, published independently.
    </td>
    <td valign="top" width="50%">
      <strong><a href="https://play.google.com/store/apps/details?id=avinya.tech.yt">ViewTube</a></strong> · <code>{apps_by_name['ViewTube']['installs']} installs</code><br/><br/>
      Video player built on VLC for broad format support — YouTube-like UI, offline playback, subtitles, and memory-efficient Shorts-style scrolling.
    </td>
  </tr>
</table>
<p><sub>Also on Play Store: <a href="https://play.google.com/store/apps/details?id=avinya.tech.qrcode">QR Code Generator</a> (<code>{apps_by_name['QR Code Generator']['installs']}</code>) · <a href="https://play.google.com/store/apps/details?id=avinya.tech.cricscore">CricScore</a> (<code>{apps_by_name['CricScore']['installs']}</code>)</sub></p>"""


def render_public_footprint(data: dict[str, object]) -> str:
    medium = data["medium"]
    latest_title = html.escape(str(medium["latest_title"]))
    latest_link = str(medium["latest_link"])

    return f"""- [Medium](https://meet-miyani.medium.com/) · `{medium['story_count']}` stories published. Latest: [{latest_title}]({latest_link}).
- [Bugfender](https://bugfender.com/author/meet-miyani/) · 3 articles — Kotlin extension functions, Kotlin vs Java, Kotlin arrays."""


def refresh_readme(data: dict[str, object], updated_label: str) -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    readme = replace_marker_block(readme, "dynamic-live-metrics", render_live_metrics(data, updated_label))
    readme = replace_marker_block(readme, "dynamic-selected-work", render_selected_work(data))
    readme = replace_marker_block(readme, "dynamic-public-footprint", render_public_footprint(data))
    README_PATH.write_text(readme, encoding="utf-8")


def refresh_banner(data: dict[str, object], updated_label: str) -> None:
    github = data["github"]
    svg = build_svg(
        followers=int(github["followers"]),
        total_stars=int(github["total_stars"]),
        public_repos=int(github["public_repos"]),
        updated_label=updated_label,
    )
    BANNER_PATH.parent.mkdir(parents=True, exist_ok=True)
    BANNER_PATH.write_text(svg, encoding="utf-8")


def main() -> None:
    updated_label = dt.datetime.now(dt.timezone.utc).strftime("%b %d, %Y")
    data = {
        "github": fetch_github_metrics(),
        "stackoverflow": fetch_stackoverflow_metrics(),
        "medium": fetch_medium_metrics(),
        "play": fetch_play_store_metrics(),
    }
    refresh_readme(data, updated_label)
    refresh_banner(data, updated_label)


if __name__ == "__main__":
    main()

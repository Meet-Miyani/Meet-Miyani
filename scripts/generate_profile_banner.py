#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import json
import ssl
import urllib.request
from pathlib import Path


def compact_number(value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M".rstrip("0").rstrip(".")
    if value >= 1_000:
        return f"{value / 1_000:.1f}K".rstrip("0").rstrip(".")
    return str(value)


def fetch_json(url: str, token: str | None) -> object:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, context=context, timeout=20) as response:
        return json.load(response)


def fetch_metrics(username: str, token: str | None) -> dict[str, int]:
    user = fetch_json(f"https://api.github.com/users/{username}", token)
    repos = fetch_json(f"https://api.github.com/users/{username}/repos?per_page=100", token)
    if not isinstance(user, dict) or not isinstance(repos, list):
        raise ValueError("Unexpected GitHub API response")
    return {
        "followers": int(user.get("followers", 0)),
        "public_repos": int(user.get("public_repos", 0)),
        "total_stars": sum(int(r.get("stargazers_count", 0)) for r in repos if isinstance(r, dict)),
    }


def build_svg(
    *,
    followers: int,
    total_stars: int,
    public_repos: int,
    story_count: int,
    total_installs_display: str,
    updated_label: str,
) -> str:
    fol = compact_number(followers)
    sta = compact_number(total_stars)
    rep = compact_number(public_repos)
    stories = compact_number(story_count)
    installs = total_installs_display

    f = "'Segoe UI','SF Pro Text','Helvetica Neue',Arial,sans-serif"
    fd = "'Segoe UI','SF Pro Display','Helvetica Neue',Arial,sans-serif"

    return f"""<svg width="1280" height="420" viewBox="0 0 1280 420" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1280" y2="420" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#07111D"/>
      <stop offset="100%" stop-color="#0B1829"/>
    </linearGradient>
    <linearGradient id="strip" x1="0" y1="0" x2="1280" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#2EE6A6"/>
      <stop offset="50%" stop-color="#48A8FF"/>
      <stop offset="100%" stop-color="#F5A623"/>
    </linearGradient>
    <linearGradient id="nameGrad" x1="0" y1="0" x2="420" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#F3FAFF"/>
      <stop offset="100%" stop-color="#A6C8E6"/>
    </linearGradient>
    <radialGradient id="glowL" cx="0" cy="1" r="1">
      <stop offset="0%" stop-color="#2EE6A6" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="#2EE6A6" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowR" cx="1" cy="0" r="1">
      <stop offset="0%" stop-color="#48A8FF" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="#48A8FF" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <rect width="1280" height="420" rx="24" fill="url(#bg)"/>
  <rect width="1280" height="420" rx="24" fill="url(#glowL)"/>
  <rect width="1280" height="420" rx="24" fill="url(#glowR)"/>
  <rect x="1" y="1" width="1278" height="418" rx="23" stroke="#15324F" stroke-width="1.5" fill="none"/>
  <rect x="0" y="0" width="1280" height="4" rx="2" fill="url(#strip)"/>

  <rect x="56" y="48" width="86" height="30" rx="15" fill="#0E2338" stroke="#1A3859"/>
  <circle cx="71" cy="63" r="3.5" fill="#2EE6A6"/>
  <text x="80" y="68" fill="#9CC4DE" font-family="{f}" font-size="13" font-weight="600">Kotlin</text>

  <rect x="152" y="48" width="102" height="30" rx="15" fill="#0E2338" stroke="#1A3859"/>
  <circle cx="167" cy="63" r="3.5" fill="#48A8FF"/>
  <text x="176" y="68" fill="#9CC4DE" font-family="{f}" font-size="13" font-weight="600">Android</text>

  <rect x="264" y="48" width="176" height="30" rx="15" fill="#0E2338" stroke="#1A3859"/>
  <circle cx="279" cy="63" r="3.5" fill="#F5A623"/>
  <text x="288" y="68" fill="#9CC4DE" font-family="{f}" font-size="13" font-weight="600">Compose Multiplatform</text>

  <text x="56" y="138" fill="url(#nameGrad)" font-family="{fd}" font-size="52" font-weight="700" letter-spacing="-1">Meet Miyani</text>
  <text x="56" y="178" fill="#5C86AA" font-family="{f}" font-size="22" font-weight="500">Senior Android Developer</text>

  <text x="56" y="220" fill="#D5E7F6" font-family="{fd}" font-size="26" font-weight="650">Android systems, codegen, and apps that ship.</text>
  <text x="56" y="248" fill="#5C86AA" font-family="{f}" font-size="15.5">The interesting work starts after launch: foundations, contracts, UI architecture, and the hard edge cases.</text>

  <circle cx="62" cy="290" r="4" fill="#2EE6A6"/>
  <text x="76" y="295" fill="#C9DDEC" font-family="{f}" font-size="15">Production Android across 3 apps plus a shared backbone library.</text>
  <circle cx="62" cy="322" r="4" fill="#48A8FF"/>
  <text x="76" y="327" fill="#C9DDEC" font-family="{f}" font-size="15">Open-source Compose and KSP work with public writing and reusable tooling.</text>
  <circle cx="62" cy="354" r="4" fill="#F5A623"/>
  <text x="76" y="359" fill="#C9DDEC" font-family="{f}" font-size="15">Indie Play Store apps shipped solo, including media and utility products at scale.</text>

  <text x="56" y="388" fill="#355677" font-family="{f}" font-size="12">github.com/Meet-Miyani   ·   meet-miyani.medium.com   ·   miyanimeet02@gmail.com</text>

  <rect x="734" y="46" width="490" height="328" rx="22" fill="#0D1F33" stroke="#183653"/>
  <text x="766" y="84" fill="#E8F3FC" font-family="{fd}" font-size="18" font-weight="650">Public signal</text>
  <text x="766" y="104" fill="#527A9D" font-family="{f}" font-size="12.5">Auto-refreshed from GitHub, Medium, and Play Store data.</text>

  <rect x="766" y="128" width="208" height="92" rx="16" fill="#112740" stroke="#1A3A5B"/>
  <rect x="782" y="144" width="34" height="4" rx="2" fill="#2EE6A6"/>
  <text x="782" y="176" fill="#F3FAFF" font-family="{fd}" font-size="34" font-weight="700">{fol}</text>
  <text x="782" y="198" fill="#5B83A7" font-family="{f}" font-size="13">GitHub followers</text>

  <rect x="986" y="128" width="208" height="92" rx="16" fill="#112740" stroke="#1A3A5B"/>
  <rect x="1002" y="144" width="34" height="4" rx="2" fill="#48A8FF"/>
  <text x="1002" y="176" fill="#F3FAFF" font-family="{fd}" font-size="34" font-weight="700">{sta}</text>
  <text x="1002" y="198" fill="#5B83A7" font-family="{f}" font-size="13">Repo stars</text>

  <rect x="766" y="236" width="208" height="92" rx="16" fill="#112740" stroke="#1A3A5B"/>
  <rect x="782" y="252" width="34" height="4" rx="2" fill="#F5A623"/>
  <text x="782" y="284" fill="#F3FAFF" font-family="{fd}" font-size="34" font-weight="700">{installs}</text>
  <text x="782" y="306" fill="#5B83A7" font-family="{f}" font-size="13">Play Store installs</text>

  <rect x="986" y="236" width="208" height="92" rx="16" fill="#112740" stroke="#1A3A5B"/>
  <rect x="1002" y="252" width="34" height="4" rx="2" fill="#9B8FFF"/>
  <text x="1002" y="284" fill="#F3FAFF" font-family="{fd}" font-size="34" font-weight="700">{stories}</text>
  <text x="1002" y="306" fill="#5B83A7" font-family="{f}" font-size="13">Medium stories</text>

  <text x="766" y="354" fill="#6B90B0" font-family="{f}" font-size="12.5">Also shipping across {rep} public repos. Updated {updated_label}.</text>

  <g opacity="0.12">
    <circle cx="1224" cy="42" r="74" stroke="#48A8FF" stroke-width="1.5" fill="none"/>
    <circle cx="1224" cy="42" r="50" stroke="#48A8FF" stroke-width="1.5" fill="none"/>
    <circle cx="1224" cy="42" r="26" stroke="#2EE6A6" stroke-width="1.5" fill="none"/>
  </g>
</svg>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate GitHub profile banner SVG")
    parser.add_argument("--username", default="Meet-Miyani")
    parser.add_argument("--token", default=None)
    parser.add_argument("--followers", type=int)
    parser.add_argument("--stars", type=int)
    parser.add_argument("--repos", type=int)
    parser.add_argument("--stories", type=int, default=0)
    parser.add_argument("--installs", default="0")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "assets" / "profile-banner.svg",
    )
    args = parser.parse_args()

    if args.followers is None or args.stars is None or args.repos is None:
        metrics = fetch_metrics(args.username, args.token)
        followers = metrics["followers"]
        stars = metrics["total_stars"]
        repos = metrics["public_repos"]
    else:
        followers = args.followers
        stars = args.stars
        repos = args.repos

    svg = build_svg(
        followers=followers,
        total_stars=stars,
        public_repos=repos,
        story_count=args.stories,
        total_installs_display=args.installs,
        updated_label=dt.datetime.now(dt.timezone.utc).strftime("%b %d, %Y"),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()

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
        "total_stars": sum(int(repo.get("stargazers_count", 0)) for repo in repos if isinstance(repo, dict)),
    }


def build_svg(*, followers: int, total_stars: int, public_repos: int, updated_label: str) -> str:
    followers_text = compact_number(followers)
    stars_text = compact_number(total_stars)
    repos_text = compact_number(public_repos)

    sans = "'Segoe UI','SF Pro Text','Helvetica Neue',Arial,sans-serif"
    sans_d = "'Segoe UI','SF Pro Display','Helvetica Neue',Arial,sans-serif"

    return f"""<svg width="1280" height="420" viewBox="0 0 1280 420" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="1280" y2="420" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#06101E"/><stop offset="55%" stop-color="#091828"/><stop offset="100%" stop-color="#0C1E38"/>
    </linearGradient>
    <linearGradient id="topBar" x1="0" y1="0" x2="1280" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#00D9A3"/><stop offset="50%" stop-color="#4D9FFF"/><stop offset="100%" stop-color="#A78BFA"/>
    </linearGradient>
    <linearGradient id="divGrad" x1="700" y1="24" x2="700" y2="396" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#00D9A3" stop-opacity="0"/><stop offset="28%" stop-color="#00D9A3" stop-opacity="0.4"/>
      <stop offset="72%" stop-color="#4D9FFF" stop-opacity="0.3"/><stop offset="100%" stop-color="#4D9FFF" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="nameGrad" x1="48" y1="0" x2="380" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#EAF6FF"/><stop offset="100%" stop-color="#A8CCEB"/>
    </linearGradient>
    <pattern id="dotGrid" x="0" y="0" width="30" height="30" patternUnits="userSpaceOnUse">
      <circle cx="0.5" cy="0.5" r="0.75" fill="#1E3D60" opacity="0.45"/>
    </pattern>
    <radialGradient id="glowTL" cx="0.1" cy="0.9" r="0.55">
      <stop offset="0%" stop-color="#00D9A3" stop-opacity="0.07"/><stop offset="100%" stop-color="#00D9A3" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowBR" cx="0.95" cy="0.1" r="0.5">
      <stop offset="0%" stop-color="#4D9FFF" stop-opacity="0.09"/><stop offset="100%" stop-color="#4D9FFF" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <rect width="1280" height="420" rx="20" fill="url(#bgGrad)"/>
  <rect width="1280" height="420" rx="20" fill="url(#dotGrid)"/>
  <rect width="1280" height="420" rx="20" fill="url(#glowTL)"/>
  <rect width="1280" height="420" rx="20" fill="url(#glowBR)"/>
  <rect x="0" y="0" width="1280" height="3" rx="1.5" fill="url(#topBar)"/>
  <rect x="0.75" y="0.75" width="1278.5" height="418.5" rx="20" stroke="#152E4A" stroke-width="1.5" fill="none"/>
  <line x1="700" y1="24" x2="700" y2="396" stroke="url(#divGrad)" stroke-width="1"/>

  <!-- LEFT COLUMN -->
  <rect x="48"  y="52" width="90"  height="30" rx="15" fill="#0A1D34" stroke="#163254" stroke-width="1"/>
  <circle cx="64"  cy="67" r="3.5" fill="#00D9A3"/>
  <text x="73"  y="72" fill="#A6C6E6" font-family="{sans}" font-size="13" font-weight="600">Kotlin</text>

  <rect x="148" y="52" width="104" height="30" rx="15" fill="#0A1D34" stroke="#163254" stroke-width="1"/>
  <circle cx="164" cy="67" r="3.5" fill="#4D9FFF"/>
  <text x="173" y="72" fill="#A6C6E6" font-family="{sans}" font-size="13" font-weight="600">Android</text>

  <rect x="262" y="52" width="150" height="30" rx="15" fill="#0A1D34" stroke="#163254" stroke-width="1"/>
  <circle cx="278" cy="67" r="3.5" fill="#A78BFA"/>
  <text x="287" y="72" fill="#A6C6E6" font-family="{sans}" font-size="13" font-weight="600">Open to Remote</text>

  <text x="48" y="148" fill="url(#nameGrad)" font-family="{sans_d}" font-size="48" font-weight="700" letter-spacing="-0.5">Meet Miyani</text>
  <text x="48" y="185" fill="#5292C0" font-family="{sans}" font-size="20" font-weight="500" letter-spacing="0.25">Senior Android Developer</text>
  <rect x="48" y="195" width="178" height="1.5" rx="0.75" fill="#163254"/>

  <text x="48" y="223" fill="#638AB0" font-family="{sans}" font-size="15">Architecture modernization · KSP codegen · Compose Multiplatform</text>
  <text x="48" y="245" fill="#638AB0" font-family="{sans}" font-size="15">Shared library design · CI/CD via GitHub Actions · Technical writing</text>
  <text x="48" y="264" fill="#436082" font-family="{sans}" font-size="13.5">Surat, India  ·  7 published articles  ·  Play Store developer</text>

  <rect x="48"  y="296" width="102" height="50" rx="11" fill="#0A1D34" stroke="#163254" stroke-width="1"/>
  <text x="99"  y="316" text-anchor="middle" fill="#00D9A3" font-family="{sans_d}" font-size="19" font-weight="700">5+</text>
  <text x="99"  y="334" text-anchor="middle" fill="#3A5A78" font-family="{sans}" font-size="11">years exp.</text>

  <rect x="160" y="296" width="144" height="50" rx="11" fill="#0A1D34" stroke="#163254" stroke-width="1"/>
  <text x="232" y="316" text-anchor="middle" fill="#4D9FFF" font-family="{sans_d}" font-size="19" font-weight="700">500K+</text>
  <text x="232" y="334" text-anchor="middle" fill="#3A5A78" font-family="{sans}" font-size="11">Play Store DLs</text>

  <rect x="314" y="296" width="122" height="50" rx="11" fill="#0A1D34" stroke="#163254" stroke-width="1"/>
  <text x="375" y="316" text-anchor="middle" fill="#A78BFA" font-family="{sans_d}" font-size="19" font-weight="700">3 apps</text>
  <text x="375" y="334" text-anchor="middle" fill="#3A5A78" font-family="{sans}" font-size="11">in production</text>

  <rect x="446" y="296" width="140" height="50" rx="11" fill="#0A1D34" stroke="#163254" stroke-width="1"/>
  <text x="516" y="316" text-anchor="middle" fill="#F59E0B" font-family="{sans_d}" font-size="19" font-weight="700">7 articles</text>
  <text x="516" y="334" text-anchor="middle" fill="#3A5A78" font-family="{sans}" font-size="11">Medium · Bugfender</text>

  <text x="48" y="382" fill="#2A4A64" font-family="{sans}" font-size="11.5">Surat, India  ·  miyanimeet02@gmail.com  ·  github.com/Meet-Miyani  ·  meet-miyani.medium.com</text>

  <!-- RIGHT COLUMN -->
  <text x="724" y="70" fill="#D4EEF8" font-family="{sans_d}" font-size="17" font-weight="700">GitHub Activity</text>
  <rect x="724" y="76" width="44" height="2" rx="1" fill="#00D9A3"/>
  <text x="724" y="96" fill="#3A5A78" font-family="{sans}" font-size="12">Live signals · Updated {updated_label}</text>

  <rect x="720"  y="112" width="160" height="122" rx="15" fill="#0A1D34" stroke="#163254" stroke-width="1"/>
  <rect x="720"  y="112" width="160" height="3"   rx="1.5" fill="#00D9A3"/>
  <text x="800"  y="163" text-anchor="middle" fill="#E6F4FF" font-family="{sans_d}" font-size="36" font-weight="700">{followers_text}</text>
  <text x="800"  y="187" text-anchor="middle" fill="#3A5A78" font-family="{sans}" font-size="13">Followers</text>
  <text x="800"  y="206" text-anchor="middle" fill="#00D9A3" font-family="{sans}" font-size="10.5" opacity="0.55">github.com</text>

  <rect x="896"  y="112" width="160" height="122" rx="15" fill="#0A1D34" stroke="#163254" stroke-width="1"/>
  <rect x="896"  y="112" width="160" height="3"   rx="1.5" fill="#F59E0B"/>
  <text x="976"  y="163" text-anchor="middle" fill="#E6F4FF" font-family="{sans_d}" font-size="36" font-weight="700">{stars_text}</text>
  <text x="976"  y="187" text-anchor="middle" fill="#3A5A78" font-family="{sans}" font-size="13">Stars</text>
  <text x="976"  y="206" text-anchor="middle" fill="#F59E0B" font-family="{sans}" font-size="10.5" opacity="0.55">across repos</text>

  <rect x="1072" y="112" width="160" height="122" rx="15" fill="#0A1D34" stroke="#163254" stroke-width="1"/>
  <rect x="1072" y="112" width="160" height="3"   rx="1.5" fill="#4D9FFF"/>
  <text x="1152" y="163" text-anchor="middle" fill="#E6F4FF" font-family="{sans_d}" font-size="36" font-weight="700">{repos_text}</text>
  <text x="1152" y="187" text-anchor="middle" fill="#3A5A78" font-family="{sans}" font-size="13">Public repos</text>
  <text x="1152" y="206" text-anchor="middle" fill="#4D9FFF" font-family="{sans}" font-size="10.5" opacity="0.55">github.com</text>

  <!-- Wide highlight: KSP -->
  <rect x="720" y="252" width="512" height="52" rx="11" fill="#0A1D34" stroke="#163254" stroke-width="1"/>
  <rect x="720" y="252" width="4"   height="52" rx="2"  fill="#00D9A3"/>
  <text x="740" y="274" fill="#D4EEF8" font-family="{sans_d}" font-size="14" font-weight="700">KSP · annotation-driven codegen</text>
  <text x="740" y="293" fill="#3A5A78" font-family="{sans}" font-size="12.5">auto-generated analytics events + type-safe notification payload parsers</text>

  <!-- Small: Compose Multiplatform -->
  <rect x="720" y="316" width="249" height="50" rx="11" fill="#0A1D34" stroke="#163254" stroke-width="1"/>
  <rect x="720" y="316" width="4"   height="50" rx="2"  fill="#4D9FFF"/>
  <text x="740" y="337" fill="#D4EEF8" font-family="{sans_d}" font-size="13.5" font-weight="700">Compose Multiplatform</text>
  <text x="740" y="355" fill="#3A5A78" font-family="{sans}" font-size="12">Android · iOS · Windows · Linux · macOS</text>

  <!-- Small: Play Store -->
  <rect x="983" y="316" width="249" height="50" rx="11" fill="#0A1D34" stroke="#163254" stroke-width="1"/>
  <rect x="983" y="316" width="4"   height="50" rx="2"  fill="#A78BFA"/>
  <text x="1003" y="337" fill="#D4EEF8" font-family="{sans_d}" font-size="13.5" font-weight="700">600K+ Play Store installs</text>
  <text x="1003" y="355" fill="#3A5A78" font-family="{sans}" font-size="12">4 published apps · independent</text>

  <!-- Decorative arcs -->
  <g opacity="0.10">
    <circle cx="1255" cy="30" r="70" stroke="#4D9FFF" stroke-width="1" fill="none"/>
    <circle cx="1255" cy="30" r="48" stroke="#4D9FFF" stroke-width="1" fill="none"/>
    <circle cx="1255" cy="30" r="26" stroke="#00D9A3" stroke-width="1" fill="none"/>
  </g>
</svg>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the GitHub profile banner SVG.")
    parser.add_argument("--username", default="Meet-Miyani")
    parser.add_argument("--output", default="assets/profile-banner.svg")
    parser.add_argument("--followers", type=int)
    parser.add_argument("--stars", type=int)
    parser.add_argument("--repos", type=int)
    parser.add_argument("--token")
    args = parser.parse_args()

    if args.followers is None or args.stars is None or args.repos is None:
        metrics = fetch_metrics(args.username, args.token)
        followers = metrics["followers"] if args.followers is None else args.followers
        stars = metrics["total_stars"] if args.stars is None else args.stars
        repos = metrics["public_repos"] if args.repos is None else args.repos
    else:
        followers = args.followers
        stars = args.stars
        repos = args.repos

    updated_label = dt.datetime.now(dt.timezone.utc).strftime("%b %d, %Y")
    svg = build_svg(
        followers=followers,
        total_stars=stars,
        public_repos=repos,
        updated_label=updated_label,
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()

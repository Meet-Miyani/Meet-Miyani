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


def build_svg(*, followers: int, total_stars: int, public_repos: int, updated_label: str) -> str:
    fol = compact_number(followers)
    sta = compact_number(total_stars)
    rep = compact_number(public_repos)

    # Font stacks — no external resources needed
    f = "'Segoe UI','SF Pro Text','Helvetica Neue',Arial,sans-serif"
    fd = "'Segoe UI','SF Pro Display','Helvetica Neue',Arial,sans-serif"

    # Validated geometry (see pre-flight script)
    # LEFT:  safe x=56–660
    # RIGHT: safe x=720–1232
    # Badge positions: B1 x=56 w=110 | B2 x=176 w=133 | B3 x=319 w=127 | B4 x=456 w=158
    # Metric cards: x=720,884,1048 each w=154
    # Wide card: x=720 w=512
    # Small cards: x=720 w=245 | x=977 w=245

    return f"""<svg width="1280" height="420" viewBox="0 0 1280 420" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Deep navy base -->
    <linearGradient id="bg" x1="0" y1="0" x2="1280" y2="420" gradientUnits="userSpaceOnUse">
      <stop offset="0%"   stop-color="#060D1A"/>
      <stop offset="100%" stop-color="#0A1525"/>
    </linearGradient>

    <!-- Top rainbow strip -->
    <linearGradient id="strip" x1="0" y1="0" x2="1280" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%"   stop-color="#00D9A3"/>
      <stop offset="48%"  stop-color="#3B9EFF"/>
      <stop offset="100%" stop-color="#9B8FFF"/>
    </linearGradient>

    <!-- Name text gradient -->
    <linearGradient id="nameGrad" x1="56" y1="0" x2="420" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%"   stop-color="#F0F8FF"/>
      <stop offset="100%" stop-color="#A4C8E8"/>
    </linearGradient>

    <!-- Column divider — fades at both ends -->
    <linearGradient id="divLine" x1="703" y1="28" x2="703" y2="392" gradientUnits="userSpaceOnUse">
      <stop offset="0%"   stop-color="#00D9A3" stop-opacity="0"/>
      <stop offset="25%"  stop-color="#1B4A6B" stop-opacity="0.7"/>
      <stop offset="75%"  stop-color="#1B4A6B" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="#1B4A6B" stop-opacity="0"/>
    </linearGradient>

    <!-- Subtle glow in bottom-left corner -->
    <radialGradient id="glowL" cx="0" cy="1" r="0.7">
      <stop offset="0%"   stop-color="#00D9A3" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="#00D9A3" stop-opacity="0"/>
    </radialGradient>

    <!-- Subtle glow top-right -->
    <radialGradient id="glowR" cx="1" cy="0" r="0.6">
      <stop offset="0%"   stop-color="#3B9EFF" stop-opacity="0.10"/>
      <stop offset="100%" stop-color="#3B9EFF" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- ── BACKGROUND ── -->
  <rect width="1280" height="420" rx="20" fill="url(#bg)"/>
  <rect width="1280" height="420" rx="20" fill="url(#glowL)"/>
  <rect width="1280" height="420" rx="20" fill="url(#glowR)"/>

  <!-- Hairline border -->
  <rect x="1" y="1" width="1278" height="418" rx="20"
        stroke="#14304D" stroke-width="1.5" fill="none"/>

  <!-- Rainbow accent strip (3 px) -->
  <rect x="0" y="0" width="1280" height="3" rx="1.5" fill="url(#strip)"/>

  <!-- Column divider -->
  <line x1="703" y1="28" x2="703" y2="392" stroke="url(#divLine)" stroke-width="1"/>


  <!-- ═══════════════════════════════════════════
       LEFT COLUMN   (x safe: 56 – 660)
       ═══════════════════════════════════════════ -->

  <!-- 3 skill pills  (y_top=52, h=28, rx=14) -->
  <rect x="56"  y="52" width="84"  height="28" rx="14" fill="#0B1E34" stroke="#183252" stroke-width="1"/>
  <circle cx="70"  cy="66" r="3.5" fill="#00D9A3"/>
  <text x="79"  y="71" fill="#8BBDD8" font-family="{f}" font-size="13" font-weight="600">Kotlin</text>

  <rect x="150" y="52" width="100" height="28" rx="14" fill="#0B1E34" stroke="#183252" stroke-width="1"/>
  <circle cx="164" cy="66" r="3.5" fill="#3B9EFF"/>
  <text x="173" y="71" fill="#8BBDD8" font-family="{f}" font-size="13" font-weight="600">Android</text>

  <rect x="260" y="52" width="148" height="28" rx="14" fill="#0B1E34" stroke="#183252" stroke-width="1"/>
  <circle cx="274" cy="66" r="3.5" fill="#9B8FFF"/>
  <text x="283" y="71" fill="#8BBDD8" font-family="{f}" font-size="13" font-weight="600">Open to Remote</text>

  <!-- Name  (baseline y=142, 50px bold) -->
  <text x="56" y="142"
        fill="url(#nameGrad)"
        font-family="{fd}"
        font-size="50" font-weight="700"
        letter-spacing="-1">Meet Miyani</text>

  <!-- Title  (baseline y=183) -->
  <text x="56" y="183"
        fill="#3E6E96"
        font-family="{f}"
        font-size="21" font-weight="500"
        letter-spacing="0.3">Senior Android Developer</text>

  <!-- Thin rule under title -->
  <rect x="56" y="194" width="180" height="1.5" rx="0.75" fill="#152E48"/>

  <!-- Description lines — each a standalone <text>, no tspan stacking -->
  <text x="56" y="218" fill="#3E6E96" font-family="{f}" font-size="15">Architecture modernization · KSP codegen · Compose Multiplatform</text>
  <text x="56" y="238" fill="#3E6E96" font-family="{f}" font-size="15">Shared library design · CI/CD · Technical writing</text>
  <text x="56" y="256" fill="#1E3A58" font-family="{f}" font-size="13">Surat, India  ·  miyanimeet02@gmail.com</text>

  <!-- ── 4 stat badges  (y_top=278, h=46, rx=11) ──
       Validated widths: B1=110 B2=133 B3=127 B4=158
       x positions:      56    176    319    456
       Right edge: 456+158=614 ≤ 660 ✓ -->

  <!-- B1: 5+ years -->
  <rect x="56"  y="278" width="110" height="46" rx="11" fill="#0B1E34" stroke="#183252" stroke-width="1"/>
  <text x="111" y="298" text-anchor="middle" fill="#00D9A3" font-family="{fd}" font-size="19" font-weight="700">5+</text>
  <text x="111" y="316" text-anchor="middle" fill="#2A4A68" font-family="{f}"  font-size="11">years exp.</text>

  <!-- B2: 500K+ downloads -->
  <rect x="176" y="278" width="133" height="46" rx="11" fill="#0B1E34" stroke="#183252" stroke-width="1"/>
  <text x="242" y="298" text-anchor="middle" fill="#3B9EFF" font-family="{fd}" font-size="19" font-weight="700">500K+</text>
  <text x="242" y="316" text-anchor="middle" fill="#2A4A68" font-family="{f}"  font-size="11">Play Store DLs</text>

  <!-- B3: 3 apps -->
  <rect x="319" y="278" width="127" height="46" rx="11" fill="#0B1E34" stroke="#183252" stroke-width="1"/>
  <text x="382" y="298" text-anchor="middle" fill="#9B8FFF" font-family="{fd}" font-size="19" font-weight="700">3 apps</text>
  <text x="382" y="316" text-anchor="middle" fill="#2A4A68" font-family="{f}"  font-size="11">in production</text>

  <!-- B4: 7 articles -->
  <rect x="456" y="278" width="158" height="46" rx="11" fill="#0B1E34" stroke="#183252" stroke-width="1"/>
  <text x="535" y="298" text-anchor="middle" fill="#F5A623" font-family="{fd}" font-size="19" font-weight="700">7 articles</text>
  <text x="535" y="316" text-anchor="middle" fill="#2A4A68" font-family="{f}"  font-size="10.5">Medium · Bugfender</text>

  <!-- Footer contact (baseline y=382) -->
  <text x="56" y="382" fill="#1A3452" font-family="{f}" font-size="11.5">
    miyanimeet02@gmail.com  ·  github.com/Meet-Miyani  ·  meet-miyani.medium.com
  </text>


  <!-- ═══════════════════════════════════════════
       RIGHT COLUMN  (x safe: 720 – 1232)
       ═══════════════════════════════════════════ -->

  <!-- Column header (baseline y=58) -->
  <text x="724" y="58" fill="#1A3452" font-family="{f}" font-size="11">GitHub activity · Updated {updated_label}</text>
  <!-- Teal accent line -->
  <rect x="724" y="64" width="38" height="1.5" rx="0.75" fill="#00D9A3"/>

  <!-- ── 3 metric cards  (y_top=76, h=128)
       x: 720, 884, 1048 — each w=154, right edge 1202 ≤ 1232 ✓ -->

  <!-- Followers card -->
  <rect x="720"  y="76" width="154" height="128" rx="14" fill="#0B1E34" stroke="#183252" stroke-width="1"/>
  <rect x="720"  y="76" width="154" height="3"   rx="1.5" fill="#00D9A3"/>
  <text x="797"  y="128" text-anchor="middle" fill="#EAF4FF" font-family="{fd}" font-size="36" font-weight="700">{fol}</text>
  <text x="797"  y="152" text-anchor="middle" fill="#2A4A68" font-family="{f}"  font-size="13">Followers</text>
  <text x="797"  y="170" text-anchor="middle" fill="#00D9A3" font-family="{f}"  font-size="10.5" opacity="0.6">github.com</text>

  <!-- Stars card -->
  <rect x="884"  y="76" width="154" height="128" rx="14" fill="#0B1E34" stroke="#183252" stroke-width="1"/>
  <rect x="884"  y="76" width="154" height="3"   rx="1.5" fill="#F5A623"/>
  <text x="961"  y="128" text-anchor="middle" fill="#EAF4FF" font-family="{fd}" font-size="36" font-weight="700">{sta}</text>
  <text x="961"  y="152" text-anchor="middle" fill="#2A4A68" font-family="{f}"  font-size="13">Stars</text>
  <text x="961"  y="170" text-anchor="middle" fill="#F5A623" font-family="{f}"  font-size="10.5" opacity="0.6">across repos</text>

  <!-- Public repos card -->
  <rect x="1048" y="76" width="154" height="128" rx="14" fill="#0B1E34" stroke="#183252" stroke-width="1"/>
  <rect x="1048" y="76" width="154" height="3"   rx="1.5" fill="#3B9EFF"/>
  <text x="1125" y="128" text-anchor="middle" fill="#EAF4FF" font-family="{fd}" font-size="36" font-weight="700">{rep}</text>
  <text x="1125" y="152" text-anchor="middle" fill="#2A4A68" font-family="{f}"  font-size="13">Public repos</text>
  <text x="1125" y="170" text-anchor="middle" fill="#3B9EFF" font-family="{f}"  font-size="10.5" opacity="0.6">github.com</text>

  <!-- ── Wide KSP highlight card  (y_top=218, h=52, right=1232 ✓) -->
  <rect x="720" y="218" width="512" height="52" rx="10" fill="#0B1E34" stroke="#183252" stroke-width="1"/>
  <rect x="720" y="218" width="4"   height="52" rx="2"  fill="#00D9A3"/>
  <text x="740" y="240" fill="#C8E0F4" font-family="{fd}" font-size="14" font-weight="700">KSP · annotation-driven codegen</text>
  <text x="740" y="259" fill="#2A4A68" font-family="{f}"  font-size="12">auto-generated analytics payloads · type-safe notification parsing</text>

  <!-- ── Two smaller highlight cards  (y_top=282, h=52)
       x=720 w=245 | x=977 w=245 — right edge 1222 ≤ 1232 ✓ -->

  <!-- Compose Multiplatform -->
  <rect x="720" y="282" width="245" height="52" rx="10" fill="#0B1E34" stroke="#183252" stroke-width="1"/>
  <rect x="720" y="282" width="4"   height="52" rx="2"  fill="#3B9EFF"/>
  <text x="740" y="304" fill="#C8E0F4" font-family="{fd}" font-size="13.5" font-weight="700">Compose Multiplatform</text>
  <text x="740" y="322" fill="#2A4A68" font-family="{f}"  font-size="12">5 targets — Android, iOS, desktop</text>

  <!-- Play Store -->
  <rect x="977" y="282" width="245" height="52" rx="10" fill="#0B1E34" stroke="#183252" stroke-width="1"/>
  <rect x="977" y="282" width="4"   height="52" rx="2"  fill="#9B8FFF"/>
  <text x="997" y="304" fill="#C8E0F4" font-family="{fd}" font-size="13.5" font-weight="700">600K+ Play Store installs</text>
  <text x="997" y="322" fill="#2A4A68" font-family="{f}"  font-size="12">4 indie apps · built solo</text>

  <!-- ── Decorative rings — top-right corner, 8% opacity ── -->
  <g opacity="0.08">
    <circle cx="1262" cy="28" r="72" stroke="#3B9EFF" stroke-width="1.5" fill="none"/>
    <circle cx="1262" cy="28" r="50" stroke="#3B9EFF" stroke-width="1.5" fill="none"/>
    <circle cx="1262" cy="28" r="28" stroke="#00D9A3" stroke-width="1.5" fill="none"/>
  </g>

  <!-- Right footer (aligned with left footer at y=382) -->
  <text x="724" y="382" fill="#1A3452" font-family="{f}" font-size="11.5">
    open to remote  ·  android · kotlin · ksp · compose
  </text>
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
        stars     = metrics["total_stars"] if args.stars is None else args.stars
        repos     = metrics["public_repos"] if args.repos is None else args.repos
    else:
        followers = args.followers
        stars     = args.stars
        repos     = args.repos

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

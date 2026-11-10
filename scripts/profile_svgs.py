#!/usr/bin/env python3
"""Minimal, typographic SVGs for the GitHub profile README.

Principles
- Graphics only: anything a visitor or a search engine should be able to read
  (name, prose, project list, links) lives in the README as real text. SVG is
  used for the identity header, the figures strip and the timeline diagram, and
  each one carries descriptive alt text.
- Native: GitHub's own system font stacks and Primer colour tokens, transparent
  backgrounds, light + dark variants (served via <picture>), so the graphics
  read as part of the page rather than pasted-on banners.
- Quiet motion: hairlines draw and text settles in once on load. The only loop
  is a slow "breathing" status dot. Everything respects prefers-reduced-motion,
  and every element's resting style is its final state.
- 960-wide viewBoxes: at GitHub's ~830px column, 16px text renders at ~14px,
  close to the README's own body copy.
"""

from __future__ import annotations

import html

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

THEMES = {
    "light": {"fg": "#1F2328", "muted": "#59636E", "subtle": "#818B98", "line": "#D1D9E0", "accent": "#1A7F37"},
    "dark": {"fg": "#F0F6FC", "muted": "#9198A1", "subtle": "#656C76", "line": "#3D444D", "accent": "#3FB950"},
}

W = 960
EASE = "cubic-bezier(.2,.7,.2,1)"

BASE_CSS = f"""
text {{ font-family: {SANS}; }}
.num {{ font-variant-numeric: tabular-nums; }}
.mono {{ font-family: {MONO}; }}
.in {{ animation: in .7s {EASE} both; }}
@keyframes in {{ from {{ opacity: 0; transform: translateY(6px); }} }}
.draw {{ transform-box: fill-box; transform-origin: left; animation: draw 1.1s {EASE} both; }}
@keyframes draw {{ from {{ transform: scaleX(0); }} }}
.breathe {{ transform-box: fill-box; transform-origin: center; animation: breathe 3.2s ease-in-out infinite; opacity: 0; }}
@keyframes breathe {{ 0%, 100% {{ opacity: 0; transform: scale(1); }} 50% {{ opacity: .35; transform: scale(2.4); }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def doc(height: int, body: str, title: str, css: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" '
        f'fill="none" role="img" aria-label="{esc(title)}"><title>{esc(title)}</title>'
        f"<style>{BASE_CSS}{css}</style>{body}</svg>\n"
    )


def d(seconds: float) -> str:
    return f'style="animation-delay:{seconds:.2f}s"'


# ───────────────────────── header ─────────────────────────

def build_header(data: dict, t: dict) -> str:
    p = data["profile"]
    body = f"""
<text class="in" {d(0)} x="0" y="58" font-size="46" font-weight="600" letter-spacing="-1.2" fill="{t['fg']}">{esc(p['name'])}</text>
<text class="in" {d(.12)} x="1" y="96" font-size="21" fill="{t['muted']}">{esc(p['role'])}</text>

<text class="mono in" {d(.2)} x="{W}" y="34" text-anchor="end" font-size="13" letter-spacing=".4" fill="{t['subtle']}">{esc(p['location'].upper())}</text>
<g class="in" {d(.28)}>
  <circle class="breathe" cx="{W - 4}" cy="58" r="4" fill="{t['accent']}"/>
  <circle cx="{W - 4}" cy="58" r="4" fill="{t['accent']}"/>
  <text x="{W - 18}" y="63" text-anchor="end" font-size="15" fill="{t['fg']}">{esc(p['availability'])}</text>
</g>

<text class="mono in" {d(.4)} x="0" y="140" font-size="13" letter-spacing=".2" fill="{t['muted']}">{esc(' · '.join(p['keywords']))}</text>
<text class="mono in" {d(.48)} x="{W}" y="140" text-anchor="end" font-size="13" letter-spacing=".2" fill="{t['muted']}">{esc(p['now'])}</text>
"""
    return doc(152, body, f"{p['name']} — {p['role']}")


# ───────────────────────── figures ─────────────────────────

def build_figures(data: dict, t: dict) -> str:
    figures = data["figures"]
    col = W / len(figures)
    parts = []
    for i, (value, label) in enumerate(figures):
        x = i * col
        lines = label.split("\n")
        parts.append(
            f'<clipPath id="f{i}"><rect x="{x}" y="0" width="{col}" height="62"/></clipPath>'
            f'<g clip-path="url(#f{i})"><text class="rise num" {d(.1 + i * .09)} x="{x}" y="50" font-size="44" '
            f'font-weight="300" letter-spacing="-1" fill="{t["fg"]}">{esc(value)}</text></g>'
            + "".join(
                f'<text class="in" {d(.35 + i * .09)} x="{x + 1}" y="{86 + k * 20}" font-size="14.5" fill="{t["muted"]}">{esc(line)}</text>'
                for k, line in enumerate(lines)
            )
        )
    css = f".rise {{ animation: rise .9s {EASE} both; }} @keyframes rise {{ from {{ transform: translateY(58px); }} }}"
    title = "; ".join(f"{v} {label.replace(chr(10), ' ')}" for v, label in figures)
    return doc(118, "".join(parts), title, css)


# ───────────────────────── experience ─────────────────────────

def build_experience(data: dict, t: dict) -> str:
    jobs = data["experience"]
    top, lx = 22, 158
    ys, y = [], top
    for job in jobs:
        ys.append(y)
        y += 56 + 22 * len(job["note"].split("\n"))
    h = y - 30
    parts = [
        f'<rect class="down" {d(.1)} x="{lx - .5}" y="{top}" width="1" height="{ys[-1] - top}" fill="{t["line"]}"/>'
    ]
    for i, (job, y) in enumerate(zip(jobs, ys)):
        if i == 0:
            dot = (
                f'<circle class="breathe" cx="{lx}" cy="{y}" r="4.5" fill="{t["accent"]}"/>'
                f'<circle cx="{lx}" cy="{y}" r="4.5" fill="{t["accent"]}"/>'
            )
        else:
            dot = f'<circle cx="{lx}" cy="{y}" r="4" fill="{t["subtle"]}"/>'
        notes = "".join(
            f'<text x="{lx + 26}" y="{y + 32 + k * 22}" font-size="15" fill="{t["muted"]}">{esc(line)}</text>'
            for k, line in enumerate(job["note"].split("\n"))
        )
        parts.append(f"""
<g class="in" {d(.15 + i * .12)}>
  <text class="mono" x="0" y="{y + 5}" font-size="13" fill="{t['subtle']}">{esc(job['when'])}</text>
  {dot}
  <text x="{lx + 26}" y="{y + 6}" font-size="17" font-weight="600" fill="{t['fg']}">{esc(job['org'])}<tspan font-weight="400" fill="{t['muted']}">  ·  {esc(job['title'])}</tspan></text>
  {notes}
</g>""")
    css = (
        f".down {{ transform-box: fill-box; transform-origin: top; animation: down 1.2s {EASE} both; }}"
        " @keyframes down { from { transform: scaleY(0); } }"
    )
    title = "Experience: " + "; ".join(f"{j['org']}, {j['title']} ({j['when']})" for j in jobs)
    return doc(h, "".join(parts), title, css)


# ───────────────────────── signature graphics ─────────────────────────
# Line-art pieces in the same language as the rest: hairlines, mono labels,
# one accent. Loops are slow and small; resting state is always legible.
# Each sits above a real-text list in the README that carries the links.

def _label(x: float, y: float, text: str, t: dict, anchor: str = "start") -> str:
    return (
        f'<text class="mono" x="{x}" y="{y}" text-anchor="{anchor}" font-size="11" letter-spacing="1.2" '
        f'fill="{t["subtle"]}">{esc(text)}</text>'
    )


# Compose Kit v6 test: rubric items passed out of 39, without the kit vs with v6.1.
# Source: compose-skill/evals-v2/results-v6 (score-output.txt, ADDONS.md).
KIT_RESULTS = [
    ("Gemini 3.8 Flash", 22, 34, False),
    ("GPT-6-Luna", 28, 37, False),
    ("DeepSeek V4.1 Flash", 32, 38, True),
    ("DeepSeek V4 Pro", 29, 34, True),
    ("GPT-6-Sol", 30, 34, False),
    ("Sonnet 5.5", 31, 34, False),
    ("Muse Spark 1.3", 27, 29, False),
]
KIT_ITEMS = 39


def build_kit(data: dict, t: dict) -> str:
    """Compose Kit, with its measured lift per model as a dumbbell chart (one hue, two shades)."""
    kit = data["kit"]
    row, top = 33, 96
    H = top + row * len(KIT_RESULTS) + 62
    x0, x1, lo, hi = 560, 868, 50, 100
    sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)  # noqa: E731
    bottom = top + row * len(KIT_RESULTS) - 12

    grid = "".join(
        f'<rect x="{sx(v) - .5}" y="{top - 22}" width="1" height="{bottom - top + 28}" fill="{t["line"]}"/>'
        f'<text class="mono" x="{sx(v)}" y="{bottom + 28}" text-anchor="middle" font-size="11" fill="{t["subtle"]}">{v}%</text>'
        for v in (50, 75, 100)
    )
    rows, css = [], []
    for i, (model, before, after, addon) in enumerate(KIT_RESULTS):
        y = top + i * row
        b, a = 100 * before / KIT_ITEMS, 100 * after / KIT_ITEMS
        xb, xa = sx(b), sx(a)
        delay = .35 + i * .09
        css.append(f"@keyframes go{i} {{ from {{ transform: translateX({xb - xa:.1f}px); }} }} .go{i} {{ animation: go{i} 1.1s {EASE} {delay:.2f}s both; }}")
        rows.append(f"""
<g class="in" {d(delay - .2)}>
  <text x="{x0 - 22}" y="{y + 5}" text-anchor="end" font-size="14.5" fill="{t['fg']}">{esc(model)}{'<tspan fill="' + t['subtle'] + '"> †</tspan>' if addon else ''}</text>
  <circle cx="{xb:.1f}" cy="{y}" r="4.5" stroke="{t['muted']}" stroke-width="1.5"/>
</g>
<rect class="draw" {d(delay)} x="{xb + 6:.1f}" y="{y - 1}" width="{max(xa - xb - 12, 0):.1f}" height="2" rx="1" fill="{t['subtle']}"/>
<circle class="go{i}" cx="{xa:.1f}" cy="{y}" r="5.5" fill="{t['fg']}"/>
<text class="mono in" {d(delay + .8)} x="{W}" y="{y + 4.5}" text-anchor="end" font-size="12.5" fill="{t['fg']}">+{a - b:.1f}</text>""")

    facts = [("126", "agentic runs in real agent CLIs"), ("2", "blind graders must agree on every item"), ("7", "models tested, none scored lower with the kit")]
    fact_svg = "".join(
        f'<g class="in" {d(.5 + k * .1)}><rect x="0" y="{222 + k * 40}" width="318" height="1" fill="{t["line"]}"/>'
        f'<text class="mono num" x="0" y="{248 + k * 40}" font-size="14" font-weight="600" fill="{t["fg"]}">{n}</text>'
        f'<text x="44" y="{248 + k * 40}" font-size="14" fill="{t["muted"]}">{esc(label)}</text></g>'
        for k, (n, label) in enumerate(facts)
    )
    lx = x0
    body = f"""
{_label(0, 34, "FLAGSHIP  ·  OPEN SOURCE", t)}
<text class="in" {d(.05)} x="-2" y="88" font-size="44" font-weight="600" letter-spacing="-1.2" fill="{t['fg']}">Compose Kit</text>
<text class="in" {d(.15)} x="0" y="124" font-size="16" fill="{t['muted']}">Seven agent skills that make AI coding agents</text>
<text class="in" {d(.15)} x="0" y="146" font-size="16" fill="{t['muted']}">write better Jetpack Compose and KMP code.</text>
<text class="mono in" {d(.25)} x="0" y="184" font-size="12.5" fill="{t['muted']}">v{esc(kit['version'])}  ·  {kit['stars']} ★  ·  MIT</text>
{fact_svg}

{_label(lx, 34, "RUBRIC ITEMS PASSED  ·  % OF 39  ·  V6 TEST", t)}
<g class="in" {d(.2)}>
  <circle cx="{lx + 5}" cy="58" r="4.5" stroke="{t['muted']}" stroke-width="1.5"/>
  <text x="{lx + 17}" y="62.5" font-size="12.5" fill="{t['muted']}">without the kit</text>
  <circle cx="{lx + 126}" cy="58" r="5.5" fill="{t['fg']}"/>
  <text x="{lx + 139}" y="62.5" font-size="12.5" fill="{t['muted']}">with Compose Kit v6.1</text>
  <text class="mono" x="{W}" y="62" text-anchor="end" font-size="11" letter-spacing="1.2" fill="{t['subtle']}">LIFT, PTS</text>
</g>
{grid}
{''.join(rows)}
<text class="in" {d(1.4)} x="{W}" y="{H - 6}" text-anchor="end" font-size="11.5" fill="{t['subtle']}">† add-on models, graded by a different pair of graders</text>
"""
    title = (
        f"Compose Kit: seven agent skills for Jetpack Compose and Compose Multiplatform. v6 test, percent of {KIT_ITEMS} rubric "
        "items passed without the kit and with v6.1: "
        + "; ".join(f"{m} {100 * b / KIT_ITEMS:.1f}% to {100 * a / KIT_ITEMS:.1f}%" for m, b, a, _ in KIT_RESULTS) + "."
    )
    return doc(H, body, title, " ".join(css))


def build_shipped(apps: list[dict], t: dict) -> str:
    """A hairline phone that draws wireframes of the shipped apps, with synced captions."""
    H = 380
    n = len(apps)
    step = 100 / n
    px, py, pw, ph = 24, 8, 188, 364
    L, R = px + 22, px + pw - 22          # screen content bounds
    mid = px + pw / 2
    s = f'stroke="{t["fg"]}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1"'
    s2 = f'stroke="{t["subtle"]}" stroke-width="1.2" stroke-linecap="round" pathLength="1" stroke-dasharray="1"'

    ticks = "".join(f"M{L + k * 12} 318 v{-10 if k % 5 == 0 else -5} " for k in range(13))
    ring = f"""
<circle class="sd" cx="{mid}" cy="150" r="46" {s}/>
<circle class="sd" cx="{mid}" cy="150" r="35" {s2}/>
<path d="M{mid - 46} 88 V214 M{mid + 46} 88 V214" stroke="{t['subtle']}" stroke-width="1.2" stroke-dasharray="3 4"/>
<path class="sd" d="M{mid - 42} 232 H{mid + 42} M{mid - 42} 232 l6 -4 M{mid - 42} 232 l6 4 M{mid + 42} 232 l-6 -4 M{mid + 42} 232 l-6 4" {s2}/>
<text class="mono" x="{mid}" y="256" text-anchor="middle" font-size="12" fill="{t['muted']}">17.3 mm</text>
<path class="sd" d="M{L} 318 H{R} {ticks}" {s}/>"""

    rows = "".join(
        f'<rect class="sd" x="{L}" y="{196 + k * 44}" width="46" height="30" rx="4" {s2}/>'
        f'<path class="sd" d="M{L + 58} {206 + k * 44} h{[78, 64, 84][k]} M{L + 58} {218 + k * 44} h{[50, 70, 40][k]}" {s2}/>'
        for k in range(3)
    )
    video = f"""
<rect class="sd" x="{L}" y="62" width="{R - L}" height="84" rx="6" {s}/>
<path class="sd" d="M{mid - 8} 92 l18 12 l-18 12 z" {s}/>
<path class="sd" d="M{L} 166 H{R}" {s2}/>
<path class="sd" d="M{L} 166 H{L + 86}" {s}/><circle cx="{L + 86}" cy="166" r="3.5" fill="{t['fg']}"/>
{rows}"""

    import random
    rnd = random.Random(11)
    cell, cols = 8, 18
    gx, gy = mid - cols * cell / 2, 78
    finder = lambda cx, cy: (  # noqa: E731
        f'<rect class="sd" x="{gx + cx * cell + 1}" y="{gy + cy * cell + 1}" width="{5 * cell - 2}" height="{5 * cell - 2}" rx="5" {s}/>'
        f'<rect x="{gx + (cx + 1.5) * cell}" y="{gy + (cy + 1.5) * cell}" width="{2 * cell}" height="{2 * cell}" rx="2.5" fill="{t["fg"]}"/>'
    )
    in_finder = lambda c, r: (c < 6 and r < 6) or (c >= cols - 6 and r < 6) or (c < 6 and r >= cols - 6)  # noqa: E731
    mods = "".join(
        f'<circle cx="{gx + c * cell + cell / 2}" cy="{gy + r * cell + cell / 2}" r="2.6" fill="{t["fg"]}"/>'
        for r in range(cols) for c in range(cols) if not in_finder(c, r) and rnd.random() < .46
    )
    qr = f"""{finder(0, 0)}{finder(cols - 5, 0)}{finder(0, cols - 5)}<g class="mods">{mods}</g>
<rect class="sd" x="{L}" y="262" width="{R - L}" height="34" rx="17" {s2}/>
<text class="mono" x="{mid}" y="283" text-anchor="middle" font-size="11.5" fill="{t['muted']}">generate</text>"""

    bars = "".join(
        f'<path class="sd" d="M{L + 4 + k * 13} 232 v-{h}" {s if k == 8 else s2}/>'
        for k, h in enumerate([14, 22, 10, 30, 18, 26, 12, 34, 46, 20, 28])
    )
    teams = "".join(
        f'<circle class="sd" cx="{L + 9}" cy="{270 + k * 30}" r="9" {s2}/>'
        f'<path class="sd" d="M{L + 28} {270 + k * 30} h{[70, 54][k]}" {s2}/>'
        f'<text class="mono" x="{R}" y="{274 + k * 30}" text-anchor="end" font-size="11.5" fill="{t["muted"]}">{["182/4", "179"][k]}</text>'
        for k in range(2)
    )
    cricket = f"""
<text class="mono" x="{L}" y="100" font-size="32" font-weight="600" fill="{t['fg']}">182/4</text>
<text class="mono" x="{L}" y="122" font-size="11.5" fill="{t['muted']}">18.2 overs · chasing 185</text>
<path class="sd" d="M{L} 232 H{R}" {s2}/>{bars}{teams}"""

    scenes = {"RingFit": ring, "ViewTube": video, "QR Code Generator": qr, "CricScore": cricket}
    tx = 300
    scene_svg, caption_svg, seg_svg, css = [], [], [], []
    for i, app in enumerate(apps):
        a, b = i * step, (i + 1) * step
        hold = "" if i == 0 else f"0%, {a:.2f}% {{ opacity: 0; }} "
        css.append(
            f"@keyframes sc{i} {{ {hold}{a if i else 0:.2f}% {{ opacity: 0; }} {a + 2:.2f}%, {b - 2:.2f}% {{ opacity: 1; }} {b:.2f}%, 100% {{ opacity: 0; }} }}"
            f" @keyframes dr{i} {{ 0%, {a:.2f}% {{ stroke-dashoffset: 1; }} {a + 9:.2f}%, 100% {{ stroke-dashoffset: 0; }} }}"
            f" @keyframes sg{i} {{ 0%, {a:.2f}% {{ transform: scaleX(0); }} {b:.2f}%, 100% {{ transform: scaleX(1); }} }}"
            f" .sc{i} {{ animation: sc{i} var(--cyc) linear infinite; }} .sc{i} .sd {{ animation: dr{i} var(--cyc) linear infinite; }}"
            f" .sg{i} {{ transform-box: fill-box; transform-origin: left; animation: sg{i} var(--cyc) linear infinite; }}"
        )
        rest = "" if i == 0 else ' style="opacity:0"'
        scene_svg.append(f'<g class="sc{i}"{rest}>{scenes[app["name"]]}</g>')
        caption_svg.append(f"""<g class="sc{i}"{rest}>
  <text class="mono" x="{tx}" y="120" font-size="12" letter-spacing="1.2" fill="{t['subtle']}">{i + 1:02d} / {n:02d}  ·  {esc(app.get('stores', 'GOOGLE PLAY'))}</text>
  <text x="{tx - 2}" y="174" font-size="44" font-weight="600" letter-spacing="-1.2" fill="{t['fg']}">{esc(app['name'])}</text>
  <text x="{tx}" y="212" font-size="20" fill="{t['fg']}">{esc(app['meta'])}</text>
  <text x="{tx}" y="244" font-size="16" fill="{t['muted']}">{esc(app['desc'])}</text>
</g>""")
        sx = tx + i * 58
        seg_svg.append(
            f'<rect x="{sx}" y="296" width="48" height="2" rx="1" fill="{t["line"]}"/>'
            f'<rect class="sg{i}" x="{sx}" y="296" width="48" height="2" rx="1" fill="{t["fg"]}"{"" if i == 0 else " style=" + chr(34) + "transform:scaleX(0)" + chr(34)}/>'
        )
    body = f"""
<g class="in">
  <rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="30" stroke="{t['subtle']}" stroke-width="1.5"/>
  <rect x="{mid - 20}" y="{py + 14}" width="40" height="5" rx="2.5" fill="{t['line']}"/>
</g>
{''.join(scene_svg)}
{''.join(caption_svg)}
{''.join(seg_svg)}
"""
    full_css = f"svg {{ --cyc: {n * 4.5}s; }} " + " ".join(css)
    title = "Apps I built and shipped on Google Play: " + "; ".join(f"{a['name']} ({a['meta']})" for a in apps)
    return doc(H, body, title, full_css)


def build_ledger(rows: list[dict], t: dict) -> str:
    """Solutions, not fixes: the recurring problem on the left, the tool built for it on the right."""
    top, row = 78, 58
    H = top + row * len(rows) - 10
    px, lx0, lx1, sx = 424, 444, 536, 556
    parts, css = [], []
    for i, r in enumerate(rows):
        y = top + i * row
        delay = .15 + i * .28
        css.append(f".pd{i} {{ animation: pd {1.1:.1f}s {EASE} {delay + .25:.2f}s both; }}")
        parts.append(f"""
<text class="in" {d(delay)} x="{px}" y="{y + 5}" text-anchor="end" font-size="15.5" fill="{t['muted']}">{esc(r['problem'])}</text>
<rect class="draw" {d(delay + .25)} x="{lx0}" y="{y - .5}" width="{lx1 - lx0}" height="1" fill="{t['subtle']}"/>
<circle class="pd{i}" cx="{lx1}" cy="{y}" r="3" fill="{t['accent']}"/>
<g class="in" {d(delay + .7)}>
  <text x="{sx}" y="{y + 6}" font-size="20" font-weight="600" letter-spacing="-.3" fill="{t['fg']}">{esc(r['name'])}</text>
  <text class="mono" x="{W}" y="{y + 5}" text-anchor="end" font-size="12" fill="{t['muted']}">{esc(r['proof'])}</text>
</g>
<rect x="0" y="{y + row / 2 - .5}" width="{W}" height="1" fill="{t['line']}" opacity="{0 if i == len(rows) - 1 else .6}"/>""")
    css.append(f"@keyframes pd {{ from {{ transform: translateX(-{lx1 - lx0}px); opacity: 0; }} 20% {{ opacity: 1; }} }}")
    body = f"""
{_label(px, 34, "A PROBLEM THAT KEPT COMING BACK", t, "end")}{_label(sx, 34, "WHAT I BUILT FOR IT", t)}
{''.join(parts)}
"""
    title = "Solutions, not fixes. " + " ".join(f"{r['problem']}: {r['name']} ({r['proof']})." for r in rows)
    return doc(H, body, title, " ".join(css))

#!/usr/bin/env python3
"""Minimal, typographic SVGs for the GitHub profile README.

Principles
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

<rect class="draw" {d(.3)} x="0" y="128" width="{W}" height="1" fill="{t['line']}"/>

<text class="mono in" {d(.5)} x="0" y="160" font-size="13" letter-spacing=".2" fill="{t['muted']}">{esc(' · '.join(p['keywords']))}</text>
<text class="mono in" {d(.58)} x="{W}" y="160" text-anchor="end" font-size="13" letter-spacing=".2" fill="{t['muted']}">{esc(p['now'])}</text>
"""
    return doc(176, body, f"{p['name']} — {p['role']}")


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


# ───────────────────────── work rows ─────────────────────────

def build_work_row(item: dict, index: int, t: dict, *, last: bool = False) -> str:
    h = 76 if last else 75
    delay = index * .08
    bottom = (
        f'<rect class="draw" {d(delay + .2)} x="0" y="{h - 1}" width="{W}" height="1" fill="{t["line"]}"/>' if last else ""
    )
    body = f"""
<rect class="draw" {d(delay)} x="0" y="0" width="{W}" height="1" fill="{t['line']}"/>
<g class="in" {d(delay + .15)}>
  <text class="mono" x="0" y="44" font-size="13" fill="{t['subtle']}">{index + 1:02d}</text>
  <text x="44" y="45" font-size="18" font-weight="600" fill="{t['fg']}">{esc(item['name'])}</text>
  <text x="224" y="45" font-size="16" fill="{t['muted']}">{esc(item['desc'])}</text>
  <text class="mono" x="{W - 30}" y="44" text-anchor="end" font-size="13" fill="{t['muted']}">{esc(item['meta'])}</text>
  <text x="{W}" y="45" text-anchor="end" font-size="16" fill="{t['subtle']}">↗</text>
</g>
{bottom}"""
    return doc(h, body, f"{item['name']} — {item['desc']} ({item['meta']})")


# ───────────────────────── experience ─────────────────────────

def build_experience(data: dict, t: dict) -> str:
    jobs = data["experience"]
    row = 78
    top = 22
    h = top + row * len(jobs) - 18
    lx = 158
    parts = [
        f'<rect class="down" {d(.1)} x="{lx - .5}" y="{top}" width="1" height="{row * (len(jobs) - 1)}" fill="{t["line"]}"/>'
    ]
    for i, job in enumerate(jobs):
        y = top + i * row
        if i == 0:
            dot = (
                f'<circle class="breathe" cx="{lx}" cy="{y}" r="4.5" fill="{t["accent"]}"/>'
                f'<circle cx="{lx}" cy="{y}" r="4.5" fill="{t["accent"]}"/>'
            )
        else:
            dot = f'<circle cx="{lx}" cy="{y}" r="4" fill="{t["subtle"]}"/>'
        parts.append(f"""
<g class="in" {d(.15 + i * .12)}>
  <text class="mono" x="0" y="{y + 5}" font-size="13" fill="{t['subtle']}">{esc(job['when'])}</text>
  {dot}
  <text x="{lx + 26}" y="{y + 6}" font-size="17" font-weight="600" fill="{t['fg']}">{esc(job['org'])}<tspan font-weight="400" fill="{t['muted']}">  ·  {esc(job['title'])}</tspan></text>
  <text x="{lx + 26}" y="{y + 32}" font-size="15" fill="{t['muted']}">{esc(job['note'])}</text>
</g>""")
    css = (
        f".down {{ transform-box: fill-box; transform-origin: top; animation: down 1.2s {EASE} both; }}"
        " @keyframes down { from { transform: scaleY(0); } }"
    )
    title = "Experience: " + "; ".join(f"{j['org']}, {j['title']} ({j['when']})" for j in jobs)
    return doc(h, "".join(parts), title, css)

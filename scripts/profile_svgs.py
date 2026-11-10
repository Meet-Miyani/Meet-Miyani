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


# ───────────────────────── signature graphics ─────────────────────────
# Line-art pieces in the same language as the rest: hairlines, mono labels,
# one accent. Loops are slow and small; resting state is always legible.

def _label(x: float, y: float, text: str, t: dict, anchor: str = "start") -> str:
    return (
        f'<text class="mono" x="{x}" y="{y}" text-anchor="{anchor}" font-size="11" letter-spacing="1.2" '
        f'fill="{t["subtle"]}">{esc(text)}</text>'
    )


def build_blueprint(t: dict) -> str:
    """How I build: typed contracts → KSP → shared library → production apps."""
    H = 300
    cy = 160
    node = f'stroke="{t["subtle"]}" stroke-width="1.25"'
    code = [("@Event", t["subtle"]), ("data class Purchase(", t["fg"]), ("  val sku: String,", t["muted"]),
            ("  val total: Money,", t["muted"]), (")", t["fg"])]
    code_svg = "".join(
        f'<text class="mono" x="18" y="{cy - 36 + i * 19}" font-size="12.5" fill="{c}" xml:space="preserve">{esc(s)}</text>'
        for i, (s, c) in enumerate(code)
    )
    modules = ["analytics events", "payload parsers", "ui components"]
    mod_svg = "".join(
        f'<rect x="488" y="{cy - 55 + i * 40}" width="164" height="30" rx="6" stroke="{t["line"]}"/>'
        f'<text class="mono" x="502" y="{cy - 35 + i * 40}" font-size="12.5" fill="{t["muted"]}">{m}</text>'
        for i, m in enumerate(modules)
    )
    apps = [("User app", "new checkout", -62), ("Driver app", "−90% OOM", 0), ("Partner app", "CMP PoC", 62)]
    app_svg = "".join(
        f'<g class="in" {d(1.0 + i * .1)}>'
        f'<rect class="arrive" x="770" y="{cy + dy - 22}" width="190" height="44" rx="8" stroke="{t["subtle"]}" stroke-width="1.25"/>'
        f'<text x="788" y="{cy + dy + 5}" font-size="15" font-weight="600" fill="{t["fg"]}">{name}</text>'
        f'<text class="mono" x="946" y="{cy + dy + 4}" text-anchor="end" font-size="11.5" fill="{t["accent"] if i == 1 else t["muted"]}">{note}</text></g>'
        for i, (name, note, dy) in enumerate(apps)
    )
    wire = f'stroke="{t["line"]}" stroke-width="1.25" pathLength="1" stroke-dasharray="1"'
    dot = f'r="3" fill="{t["accent"]}" opacity="0"'
    css = f"""
.wire {{ animation: wire 1s {EASE} both; }} @keyframes wire {{ from {{ stroke-dashoffset: 1; }} }}
.spin {{ transform-box: fill-box; transform-origin: center; animation: spin 24s linear infinite; }} @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
.p1 {{ animation: p1 6s linear 1.6s infinite; }} .p2 {{ animation: p2 6s linear 1.6s infinite; }}
.p3a {{ animation: p3a 6s linear 1.6s infinite; }} .p3b {{ animation: p3b 6s linear 1.6s infinite; }} .p3c {{ animation: p3c 6s linear 1.6s infinite; }}
@keyframes p1 {{ 0% {{ opacity: 0; transform: translateX(0); }} 2% {{ opacity: 1; }} 20% {{ opacity: 1; transform: translateX(94px); }} 22%, 100% {{ opacity: 0; transform: translateX(94px); }} }}
@keyframes p2 {{ 0%, 30% {{ opacity: 0; transform: translateX(0); }} 32% {{ opacity: 1; }} 50% {{ opacity: 1; transform: translateX(100px); }} 52%, 100% {{ opacity: 0; transform: translateX(100px); }} }}
@keyframes p3b {{ 0%, 60% {{ opacity: 0; transform: translate(0,0); }} 62% {{ opacity: 1; }} 84% {{ opacity: 1; transform: translate(100px,0); }} 86%, 100% {{ opacity: 0; transform: translate(100px,0); }} }}
@keyframes p3a {{ 0%, 60% {{ opacity: 0; transform: translate(0,0); }} 62% {{ opacity: 1; }} 68% {{ transform: translate(50px,0); }} 78% {{ transform: translate(50px,-62px); }} 84% {{ opacity: 1; transform: translate(100px,-62px); }} 86%, 100% {{ opacity: 0; transform: translate(100px,-62px); }} }}
@keyframes p3c {{ 0%, 60% {{ opacity: 0; transform: translate(0,0); }} 62% {{ opacity: 1; }} 68% {{ transform: translate(50px,0); }} 78% {{ transform: translate(50px,62px); }} 84% {{ opacity: 1; transform: translate(100px,62px); }} 86%, 100% {{ opacity: 0; transform: translate(100px,62px); }} }}
.arrive {{ animation: arrive 6s linear 1.6s infinite; }} @keyframes arrive {{ 0%, 82%, 100% {{ stroke: {t['subtle']}; }} 86%, 92% {{ stroke: {t['accent']}; }} }}
"""
    body = f"""
{_label(0, 62, "01  TYPED CONTRACTS", t)}{_label(330, 62, "02  CODEGEN", t, "middle")}{_label(470, 62, "03  SHARED LIBRARY", t)}{_label(770, 62, "04  PRODUCTION APPS", t)}

<g class="in" {d(.1)}><rect x=".6" y="{cy - 60}" width="196" height="120" rx="10" {node}/>{code_svg}</g>
<path class="wire" {d(.5)} d="M197 {cy} H290" {wire}/>
<g class="in" {d(.4)}>
  <circle cx="330" cy="{cy}" r="38" {node}/>
  <circle class="spin" cx="330" cy="{cy}" r="46" stroke="{t['line']}" stroke-width="1.25" stroke-dasharray="3 7"/>
  <text class="mono" x="330" y="{cy + 5}" text-anchor="middle" font-size="15" font-weight="600" fill="{t['fg']}">KSP</text>
</g>
<path class="wire" {d(.8)} d="M376 {cy} H470" {wire}/>
<g class="in" {d(.7)}><rect x="470" y="{cy - 74}" width="200" height="148" rx="10" {node}/>{mod_svg}</g>
<path class="wire" {d(1.1)} d="M670 {cy} H770" {wire}/>
<path class="wire" {d(1.1)} d="M720 {cy} V{cy - 62} H770" {wire}/>
<path class="wire" {d(1.1)} d="M720 {cy} V{cy + 62} H770" {wire}/>
{app_svg}

<circle class="p1" cx="197" cy="{cy}" {dot}/><circle class="p2" cx="373" cy="{cy}" {dot}/>
<circle class="p3a" cx="670" cy="{cy}" {dot}/><circle class="p3b" cx="670" cy="{cy}" {dot}/><circle class="p3c" cx="670" cy="{cy}" {dot}/>

<text class="mono in" {d(1.4)} x="0" y="{H - 14}" font-size="12" fill="{t['subtle']}">one source of truth  →  generated, type-safe code  →  one library  →  three apps</text>
"""
    return doc(H, body, "How I build: typed contracts go through KSP code generation into one shared library that powers three production Android apps (User, Driver, Partner).", css)


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
  <text class="mono" x="{tx}" y="120" font-size="12" letter-spacing="1.2" fill="{t['subtle']}">{i + 1:02d} / {n:02d}  ·  GOOGLE PLAY</text>
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


def build_pulse(weeks: list[int], total: int, labels: list[tuple[int, str]], t: dict) -> str:
    """One line: weekly contributions over the last year."""
    H = 176
    top, base = 40, 128
    peak = max(weeks + [1])
    n = len(weeks)
    pts = [(i * W / (n - 1), base - (v / peak) * (base - top)) for i, v in enumerate(weeks)]
    path = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(n - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, min(base, p1[1] + (p2[1] - p0[1]) / 6))
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, min(base, p2[1] - (p3[1] - p1[1]) / 6))
        path += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    ex, ey = pts[-1]
    months = "".join(
        f'<text class="mono" x="{i * W / (n - 1):.0f}" y="{H - 8}" font-size="11" fill="{t["subtle"]}">{name}</text>'
        for i, name in labels if i * W / (n - 1) < W - 40
    )
    css = f".sweep {{ transform-box: fill-box; transform-origin: left; animation: draw 2.4s {EASE} both; }} .late {{ animation-delay: 2.1s; }}"
    body = f"""
<defs>
  <linearGradient id="pf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t['fg']}" stop-opacity=".10"/><stop offset="1" stop-color="{t['fg']}" stop-opacity="0"/></linearGradient>
  <clipPath id="pc"><rect class="sweep" x="0" y="0" width="{W}" height="{base + 2}"/></clipPath>
</defs>
<text class="mono in" x="0" y="14" font-size="12" fill="{t['muted']}">{total:,} contributions in the last 52 weeks</text>
<text class="mono in" x="{W}" y="14" text-anchor="end" font-size="12" fill="{t['subtle']}">peak week: {peak}</text>
<rect x="0" y="{base}" width="{W}" height="1" fill="{t['line']}"/>
<g clip-path="url(#pc)">
  <path d="{path} V{base} H0 Z" fill="url(#pf)"/>
  <path d="{path}" stroke="{t['fg']}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>
</g>
<g class="in late">
  <circle class="breathe" cx="{ex - 4:.1f}" cy="{ey:.1f}" r="4" fill="{t['accent']}"/>
  <circle cx="{ex - 4:.1f}" cy="{ey:.1f}" r="4" fill="{t['accent']}"/>
</g>
{months}
"""
    return doc(H, body, f"{total:,} GitHub contributions in the last 52 weeks", css)

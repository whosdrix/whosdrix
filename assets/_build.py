"""Generates the animated SVGs for github.com/whosdrix's profile README.
Run:  python3 build_assets.py <repo_dir>
Everything is hand-rolled SVG + CSS keyframes, no external services."""
import sys, pathlib, html

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".") / "assets"
OUT.mkdir(parents=True, exist_ok=True)

PINK, GREY, WHITE, BG = "#ff0055", "#8b8b95", "#f4f4f5", "#09090b"
MONO = 'ui-monospace, "SFMono-Regular", "JetBrains Mono", Menlo, Consolas, monospace'
REDUCED = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"
W = 830  # roughly GitHub's README column width on desktop


def esc(s):
    return html.escape(s, quote=False)


# ───────────────────────── terminal ─────────────────────────
def terminal():
    CYCLE = 22.0          # seconds per loop
    CH = 9.1              # approx monospace char width at 15px
    LH = 27
    x0, y = 28, 78
    # (kind, text, start_s, end_s)  cmd = typed, out = appears
    script = [
        ("cmd", "whoami", 0.6, 1.3),
        ("out", "martin, aka drix. czech republic.", 1.7, None),
        ("cmd", "cat now.txt", 3.0, 4.0),
        ("out", "> websites for a living", 4.4, None),
        ("out", "> small tools when something annoys me", 4.8, None),
        ("out", "> currently losing an argument with css", 5.2, None),
        ("cmd", "ls ./projects --public", 7.0, 8.6),
        ("load", "", 9.0, None),
        ("out", "a few things are cooking. check back.", 11.0, None),
        ("cmd", "git push --force", 12.8, 14.2),
        ("err", "nope. not on a friday.", 14.8, None),
    ]
    HOLD_END = 19.5
    pct = lambda s: f"{s / CYCLE * 100:.2f}%"
    end = pct(HOLD_END)
    gone = pct(HOLD_END + 0.6)

    css, body = [], []
    for i, (kind, text, t0, t1) in enumerate(script):
        cls = f"l{i}"
        # whole line: invisible until t0, visible until HOLD_END, fade, invisible
        css.append(
            f"@keyframes {cls} {{ 0%, {pct(t0 - 0.01)} {{ opacity: 0; }} {pct(t0)}, {end} {{ opacity: 1; }} {gone}, 100% {{ opacity: 0; }} }}"
            f" .{cls} {{ animation: {cls} {CYCLE}s linear infinite; }}"
        )
        if kind == "cmd":
            n = len(text)
            wpx = n * CH + 14
            css.append(
                f"@keyframes t{i} {{ 0%, {pct(t0)} {{ transform: translateX(0); }} "
                f"{pct(t1)}, 100% {{ transform: translateX({wpx:.0f}px); }} }}"
                f" .t{i} {{ animation: t{i} {CYCLE}s steps(1000) infinite; }}"
            )
            # steps(1000) over whole cycle ~ smooth; fake per-char steps below
            css[-1] = (
                f"@keyframes t{i} {{ 0%, {pct(t0)} {{ transform: translateX(0); }} "
                + " ".join(
                    f"{pct(t0 + (t1 - t0) * k / n)} {{ transform: translateX({k * CH:.1f}px); }}"
                    for k in range(1, n)
                )
                + f" {pct(t1)}, 100% {{ transform: translateX({wpx:.0f}px); }} }}"
                f" .t{i} {{ animation: t{i} {CYCLE}s step-end infinite; }}"
            )
            nxt = next((sc[2] for sc in script[i + 1:]), HOLD_END)
            css.append(
                f"@keyframes cv{i} {{ 0%, {pct(t0 - 0.01)} {{ opacity: 0; }} {pct(t0)} {{ opacity: 1; }} "
                f"{pct(t1 + 0.25)} {{ opacity: 1; }} {pct(t1 + 0.26)}, 100% {{ opacity: 0; }} }}"
                f" .cv{i} {{ animation: cv{i} {CYCLE}s step-end infinite; }}"
            )
            tx = x0 + 18
            body.append(
                f'<g class="{cls}"><text x="{x0}" y="{y}" class="p">$</text>'
                f'<text x="{tx}" y="{y}" class="c">{esc(text)}</text>'
                f'<rect class="t{i}" x="{tx - 1}" y="{y - 16}" width="{wpx + 4:.0f}" height="22" fill="{BG}"/>'
                f'<g class="cv{i}"><rect class="t{i}" x="{tx}" y="{y - 14}" width="9" height="18" fill="{PINK}"/></g></g>'
            )
        elif kind == "load":
            body.append(
                f'<g class="{cls}"><text x="{x0}" y="{y}" class="o">scanning</text>'
                + "".join(
                    f'<circle class="ld" style="animation-delay:{k * 0.15:.2f}s" cx="{x0 + 92 + k * 12}" cy="{y - 5}" r="3" fill="{PINK}"/>'
                    for k in range(3)
                )
                + "</g>"
            )
        else:
            klass = "e" if kind == "err" else "o"
            body.append(f'<text class="{cls} {klass}" x="{x0}" y="{y}">{esc(text)}</text>')
        y += LH if kind != "cmd" or i == 0 else LH
        if kind == "out" and i + 1 < len(script) and script[i + 1][0] == "cmd":
            y += 8
        if kind == "load":
            y += 0

    H = y + 10
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <style>
    text {{ font-family: {MONO}; font-size: 15px; }}
    .p {{ fill: {PINK}; font-weight: 700; }}
    .c {{ fill: {WHITE}; }}
    .o {{ fill: {GREY}; }}
    .e {{ fill: {PINK}; }}
    .bar {{ font-size: 12px; fill: {GREY}; letter-spacing: .5px; }}
    .blink {{ opacity: .9; }}
    .ld {{ animation: ld 0.9s ease-in-out infinite; }}
    @keyframes ld {{ 0%,100% {{ opacity: .2; transform: translateY(0); }} 50% {{ opacity: 1; transform: translateY(-3px); }} }}
    {" ".join(css)}
    {REDUCED}
  </style>
  <rect width="{W}" height="{H}" rx="12" fill="{BG}"/>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="#fff" stroke-opacity=".08"/>
  <circle cx="24" cy="22" r="5.5" fill="#ff5f57"/><circle cx="42" cy="22" r="5.5" fill="#febc2e"/><circle cx="60" cy="22" r="5.5" fill="#28c840"/>
  <text x="{W / 2}" y="26" text-anchor="middle" class="bar">drix@home: ~</text>
  <line x1="0" y1="42" x2="{W}" y2="42" stroke="#fff" stroke-opacity=".06"/>
  {"".join(body)}
</svg>'''
    (OUT / "terminal.svg").write_text(svg)


# ───────────────────────── section titles ─────────────────────────
def title(slug, num, label):
    """Transparent bg, colors readable on both GitHub light and dark."""
    H = 54
    lw = len(label) * 13.2
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <style>
    text {{ font-family: {MONO}; }}
    .n {{ fill: {PINK}; font-size: 13px; font-weight: 700; letter-spacing: 1px; }}
    .t {{ fill: {GREY}; font-size: 22px; font-weight: 700; }}
    .u {{ animation: grow 1.4s cubic-bezier(.2,.8,.2,1) both, shimmer 5s ease-in-out 1.4s infinite; transform-origin: 0 0; }}
    .s {{ animation: slide 3.5s cubic-bezier(.6,0,.4,1) 1.4s infinite; }}
    @keyframes grow {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
    @keyframes shimmer {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .55; }} }}
    @keyframes slide {{ from {{ transform: translateX(-80px); }} to {{ transform: translateX({W}px); }} }}
    {REDUCED}
  </style>
  <text x="0" y="30" class="n">{num}</text>
  <text x="38" y="31" class="t">{esc(label)}</text>
  <rect class="u" x="38" y="42" width="{lw:.0f}" height="3" rx="1.5" fill="{PINK}"/>
  <line x1="{38 + lw + 14:.0f}" y1="43.5" x2="{W}" y2="43.5" stroke="{GREY}" stroke-opacity=".3"/>
  <rect class="s" x="0" y="42.5" width="80" height="2" fill="{PINK}" opacity=".7"/>
</svg>'''
    (OUT / f"title-{slug}.svg").write_text(svg)


# ───────────────────────── stack ─────────────────────────
def stack():
    rows = [
        ("daily", ["TypeScript", "Next.js", "Tailwind", "Node", "Postgres", "Cloudflare", "Vercel"]),
        ("sometimes", ["Java", "Python", "MongoDB", "Git hooks I regret"]),
    ]
    CH, PADX, GAP, PH = 8.4, 16, 10, 34
    out, y, k = [], 18, 0
    for label, items in rows:
        out.append(f'<text x="0" y="{y + 22}" class="lb">{label}</text>')
        x = 110
        for it in items:
            w = len(it) * CH + PADX * 2 + 14
            if x + w > W:
                x, y = 110, y + PH + 12
            d = 0.25 + k * 0.09
            fl = 3.5 + (k % 4) * 0.6
            out.append(
                f'<g class="pop" style="animation-delay:{d:.2f}s"><g class="bob" style="animation-delay:{d + 0.7:.2f}s;animation-duration:{fl:.1f}s">'
                f'<rect x="{x}" y="{y}" width="{w:.0f}" height="{PH}" rx="17" class="bx"/>'
                f'<circle cx="{x + PADX + 2}" cy="{y + PH / 2}" r="3.5" class="dt" style="animation-delay:{k * 0.3:.1f}s"/>'
                f'<text x="{x + PADX + 13}" y="{y + 22}" class="tx">{esc(it)}</text></g></g>'
            )
            x += w + GAP
            k += 1
        y += PH + 22
    H = y - 4
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <style>
    text {{ font-family: {MONO}; }}
    .lb {{ fill: {GREY}; font-size: 13px; letter-spacing: 1px; }}
    .tx {{ fill: {GREY}; font-size: 14px; }}
    .bx {{ fill: {PINK}; fill-opacity: .06; stroke: {PINK}; stroke-opacity: .45; }}
    .dt {{ fill: {PINK}; animation: pulse 2.4s ease-in-out infinite; }}
    .pop {{ animation: pop .7s cubic-bezier(.2,.9,.3,1.3) both; }}
    .bob {{ animation: bob 3.5s ease-in-out infinite alternate; }}
    @keyframes pop {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
    @keyframes bob {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-3px); }} }}
    @keyframes pulse {{ 0%,100% {{ opacity: .35; }} 50% {{ opacity: 1; }} }}
    {REDUCED}
  </style>
  {"".join(out)}
</svg>'''
    (OUT / "stack.svg").write_text(svg)


# ───────────────────────── empty project slot ─────────────────────────
def slot():
    H = 120
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <style>
    text {{ font-family: {MONO}; }}
    .b {{ fill: none; stroke: {GREY}; stroke-opacity: .5; stroke-dasharray: 6 6; animation: march 1.2s linear infinite; }}
    .k {{ fill: {PINK}; font-size: 12px; letter-spacing: 1.5px; font-weight: 700; }}
    .h {{ fill: {GREY}; font-size: 18px; font-weight: 700; }}
    .s {{ fill: {GREY}; font-size: 13px; opacity: .8; }}
    .bar {{ fill: {PINK}; animation: load 3.2s cubic-bezier(.6,0,.4,1) infinite; transform-origin: 28px 0; }}
    .cur {{ animation: blink 1s steps(1) infinite; }}
    @keyframes march {{ to {{ stroke-dashoffset: -24; }} }}
    @keyframes load {{ 0% {{ transform: scaleX(0); }} 70% {{ transform: scaleX(1); opacity: 1; }} 100% {{ transform: scaleX(1); opacity: 0; }} }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
    {REDUCED}
  </style>
  <rect class="b" x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12"/>
  <text x="28" y="36" class="k">SLOT 01 · RESERVED</text>
  <text x="28" y="64" class="h">something's compiling<tspan class="cur" fill="{PINK}">_</tspan></text>
  <text x="28" y="88" class="s">public projects land here as they ship. most of my stuff is private, the good bits won't be.</text>
  <rect x="28" y="100" width="{W - 56}" height="3" rx="1.5" fill="{GREY}" fill-opacity=".2"/>
  <rect class="bar" x="28" y="100" width="{W - 56}" height="3" rx="1.5"/>
</svg>'''
    (OUT / "slot.svg").write_text(svg)


# ───────────────────────── footer ─────────────────────────
def footer():
    H = 90
    pts = 60
    import math
    def wave(phase, amp):
        return " ".join(
            f"{'M' if i == 0 else 'L'}{i * W / pts:.1f},{45 + amp * math.sin(i / pts * math.pi * 4 + phase):.1f}"
            for i in range(pts + 1)
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <style>
    text {{ font-family: {MONO}; }}
    .w1 {{ animation: sh 6s linear infinite; }}
    .w2 {{ animation: sh 9s linear infinite reverse; }}
    .sig {{ fill: {GREY}; font-size: 12px; letter-spacing: 3px; }}
    .hb {{ animation: hb 1.6s ease-in-out infinite; transform-origin: {W / 2}px 45px; }}
    @keyframes sh {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-{W / 2}px); }} }}
    @keyframes hb {{ 0%,100% {{ transform: scale(1); }} 15% {{ transform: scale(1.35); }} 30% {{ transform: scale(1); }} 45% {{ transform: scale(1.2); }} }}
    {REDUCED}
  </style>
  <defs><mask id="m"><rect width="{W}" height="{H}" fill="#fff"/><rect x="{W / 2 - 150}" y="20" width="300" height="50" fill="#000"/></mask></defs>
  <g mask="url(#m)"><g class="w1"><path d="{wave(0, 10)}" fill="none" stroke="{PINK}" stroke-opacity=".55" stroke-width="1.5"/>
    <path d="{wave(0, 10)}" transform="translate({W},0)" fill="none" stroke="{PINK}" stroke-opacity=".55" stroke-width="1.5"/></g>
  <g class="w2"><path d="{wave(1.5, 6)}" fill="none" stroke="{GREY}" stroke-opacity=".35"/>
    <path d="{wave(1.5, 6)}" transform="translate({W},0)" fill="none" stroke="{GREY}" stroke-opacity=".35"/></g></g>
  <circle class="hb" cx="{W / 2 - 122}" cy="45" r="4" fill="{PINK}"/>
  <text x="{W / 2 + 8}" y="49.5" text-anchor="middle" class="sig">HAND-MADE · MOSTLY</text>
</svg>'''
    (OUT / "footer.svg").write_text(svg)


terminal()
title("projects", "01", "stuff i've put out")
title("stack", "02", "what i reach for")
title("lately", "03", "lately")
title("contact", "04", "find me")
stack()
slot()
footer()
print("built:", sorted(p.name for p in OUT.iterdir()))

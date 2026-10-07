"""Draws assets/activity.svg from the last 30 days of GitHub contributions.
Run by .github/workflows/activity.yml once a day. Locally:
  GITHUB_TOKEN=... python3 assets/_activity.py whosdrix
  python3 assets/_activity.py --demo        (fake data, for tweaking the look)"""
import json, os, sys, math, random, pathlib, urllib.request, datetime as dt

LOGIN = next((a for a in sys.argv[1:] if not a.startswith("-")), "whosdrix")
DAYS = 30
PINK, GREY, WHITE, BG = "#ff0055", "#8b8b95", "#f4f4f5", "#09090b"
MONO = 'ui-monospace, "SFMono-Regular", "JetBrains Mono", Menlo, Consolas, monospace'
OUT = pathlib.Path(__file__).with_name("activity.svg")


def fetch():
    q = """query($login:String!){ user(login:$login){ contributionsCollection{
      contributionCalendar{ weeks{ contributionDays{ date contributionCount }}}}}}"""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": q, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    data = json.load(urllib.request.urlopen(req))
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = [(d["date"], d["contributionCount"]) for w in weeks for d in w["contributionDays"]]
    return days[-DAYS:]


def demo():
    today = dt.date.today()
    random.seed(4)
    return [((today - dt.timedelta(days=DAYS - 1 - i)).isoformat(),
             max(0, int(random.gauss(4, 4)) if random.random() > .25 else 0)) for i in range(DAYS)]


def draw(days):
    W, H = 830, 250
    L, R, T, B = 40, 24, 70, 44           # plot padding
    pw, ph = W - L - R, H - T - B
    counts = [c for _, c in days]
    total, peak = sum(counts), max(counts)
    top = max(4, math.ceil(peak / 4) * 4)
    xs = [L + i * pw / (len(days) - 1) for i in range(len(days))]
    ys = [T + ph - c / top * ph for c in counts]

    # smooth path (Catmull-Rom → cubic Bézier)
    pts = list(zip(xs, ys))
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, min(T + ph, p1[1] + (p2[1] - p0[1]) / 6))
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, min(T + ph, p2[1] - (p3[1] - p1[1]) / 6))
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    area = d + f" L{xs[-1]:.1f},{T + ph} L{xs[0]:.1f},{T + ph} Z"

    grid = "".join(
        f'<line x1="{L}" x2="{W - R}" y1="{T + ph - k / 4 * ph:.1f}" y2="{T + ph - k / 4 * ph:.1f}" class="g"/>'
        f'<text x="{L - 10}" y="{T + ph - k / 4 * ph + 4:.1f}" class="ax" text-anchor="end">{top * k // 4}</text>'
        for k in range(5)
    )
    labels = "".join(
        f'<text x="{xs[i]:.1f}" y="{H - 18}" class="ax" text-anchor="middle">'
        f'{dt.date.fromisoformat(days[i][0]).strftime("%b %-d").lower()}</text>'
        for i in range(0, len(days), 7)
    )
    dots = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{3.2 if c else 2}" class="{"dt" if c else "dz"}" '
        f'style="animation-delay:{.9 + i * .045:.2f}s"/>'
        for i, (x, y, c) in enumerate(zip(xs, ys, counts))
    )
    pi = counts.index(peak) if peak else None
    peak_mark = ""
    if pi is not None:
        px, py = xs[pi], ys[pi]
        anchor = "end" if px > W - 160 else "start"
        off = -12 if anchor == "end" else 12
        peak_mark = (f'<g class="pk"><circle cx="{px:.1f}" cy="{py:.1f}" r="9" class="ring"/>'
                     f'<text x="{px + off:.1f}" y="{py - 12:.1f}" class="pt" text-anchor="{anchor}">peak · {peak}</text></g>')
    streak = 0
    for c in reversed(counts):
        if not c:
            break
        streak += 1
    active = sum(1 for c in counts if c)
    stats = f"{total} contributions · {active}/{DAYS} days active · {streak}-day streak"
    if not total:
        stats = "quiet month. something's brewing offline."
    updated = dt.date.today().strftime("%b %-d").lower()

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <linearGradient id="a" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0" stop-color="{PINK}" stop-opacity=".35"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="c"><rect width="{W}" height="{H}" rx="12"/></clipPath>
  </defs>
  <style>
    text {{ font-family: {MONO}; }}
    .hd {{ fill: {WHITE}; font-size: 15px; font-weight: 700; }}
    .sb {{ fill: {GREY}; font-size: 12px; }}
    .ax {{ fill: {GREY}; font-size: 11px; opacity: .7; }}
    .g  {{ stroke: #fff; stroke-opacity: .06; }}
    .ln {{ fill: none; stroke: {PINK}; stroke-width: 2.4; stroke-linecap: round; stroke-dasharray: 2400; stroke-dashoffset: 2400;
          animation: draw 2.2s cubic-bezier(.6,0,.2,1) .3s forwards; }}
    .ar {{ fill: url(#a); opacity: 0; animation: fade 1.2s ease 1.6s forwards; }}
    .dt {{ fill: {WHITE}; stroke: {PINK}; stroke-width: 2; opacity: 0; animation: pop .4s ease forwards; }}
    .dz {{ fill: {GREY}; opacity: 0; animation: pop .4s ease forwards; }}
    .pk {{ opacity: 0; animation: fade .6s ease 2.6s forwards; }}
    .ring {{ fill: none; stroke: {PINK}; animation: ping 2s ease-out 2.6s infinite; transform-box: fill-box; transform-origin: center; }}
    .pt {{ fill: {PINK}; font-size: 12px; font-weight: 700; }}
    .live {{ fill: {PINK}; animation: blink 1.6s ease-in-out infinite; }}
    @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
    @keyframes fade {{ to {{ opacity: 1; }} }}
    @keyframes pop  {{ to {{ opacity: 1; }} }}
    @keyframes ping {{ 0% {{ transform: scale(.6); opacity: 1; }} 100% {{ transform: scale(2); opacity: 0; }} }}
    @keyframes blink {{ 50% {{ opacity: .25; }} }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; opacity: 1 !important; stroke-dashoffset: 0 !important; }} }}
  </style>
  <g clip-path="url(#c)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <text x="{L - 12}" y="32" class="hd">last {DAYS} days</text>
    <text x="{L - 12}" y="52" class="sb">{stats}</text>
    <circle cx="{W - R - 112}" cy="28" r="4" class="live"/>
    <text x="{W - R}" y="32" class="sb" text-anchor="end">synced {updated}</text>
    {grid}{labels}
    <path d="{area}" class="ar"/>
    <path d="{d}" class="ln"/>
    {dots}{peak_mark}
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="#fff" stroke-opacity=".08"/>
</svg>'''


days = demo() if "--demo" in sys.argv else fetch()
OUT.write_text(draw(days))
print(f"wrote {OUT} ({sum(c for _, c in days)} contributions)")

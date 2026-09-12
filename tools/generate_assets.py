#!/usr/bin/env python3
"""Generate animated SVG assets for the profile README.

Matches the palette/idiom of the existing hand-made assets: 1000-wide,
#050a12 ground, cyan/purple/green accents, pure SMIL (no CSS keyframes,
since GitHub's camo proxy serves these as <img> and CSS animation inside
an <img>-embedded SVG still runs, but SMIL is what the rest of the set
already uses -- keep one idiom).
"""
import os

BG     = "#050a12"
PANEL  = "#070d17"
PANEL2 = "#0b1220"
EDGE   = "#164e63"
GRID   = "#0f2233"
CYAN   = "#22d3ee"
BLUE   = "#60a5fa"
PURPLE = "#a78bfa"
GREEN  = "#4ade80"
PINK   = "#f472b6"
AMBER  = "#fbbf24"
SLATE  = "#94a3b8"
DIM    = "#475569"
WHITE  = "#ecfeff"

MONO = "ui-monospace,'SF Mono','Cascadia Code','JetBrains Mono',Menlo,Consolas,monospace"

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")


def kt(times, total):
    """Format a keyTimes attribute from absolute seconds.

    Clamps into [0,1] and enforces the non-decreasing requirement, so a
    keyframe computed past the end of the cycle degrades to 1.0 instead of
    emitting an out-of-range keyTimes list (which browsers drop silently,
    leaving the whole animation dead).
    """
    out, prev = [], 0.0
    for t in times:
        v = min(1.0, max(0.0, t / total))
        v = max(v, prev)
        out.append(v)
        prev = v
    out[-1] = 1.0
    return ";".join(f"{v:.4f}" for v in out)


def head(w, h, extra=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" fill="none" '
        f'role="img" aria-label="{extra}">'
    )


def window(w, h, title, x=0, y=0, dots=True):
    """Terminal-style window chrome."""
    s = f'<g transform="translate({x},{y})">'
    s += f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12" fill="{PANEL}" stroke="{EDGE}"/>'
    s += f'<path d="M12 0.5 H{w-12} a11.5 11.5 0 0 1 11.5 11.5 V34 H0.5 V12 A11.5 11.5 0 0 1 12 0.5 Z" fill="{PANEL2}"/>'
    s += f'<line x1="0.5" y1="34" x2="{w-0.5}" y2="34" stroke="{EDGE}"/>'
    if dots:
        for i, c in enumerate((PINK, AMBER, GREEN)):
            s += f'<circle cx="{22+i*20}" cy="17.5" r="5" fill="{c}" opacity="0.85"/>'
    s += (f'<text x="{w/2}" y="22" font-family="{MONO}" font-size="12" fill="{DIM}" '
          f'text-anchor="middle" letter-spacing="0.5">{title}</text>')
    s += "</g>"
    return s


# --------------------------------------------------------------------------
# 1. terminal.svg -- character-by-character typing
# --------------------------------------------------------------------------
def terminal():
    W, H = 1000, 372
    # Measured advance for this stack at 14.5px is 8.73 (ratio 0.602). Use a
    # slightly generous value so a wider fallback mono never truncates the
    # clip-path reveal -- an over-wide clip just parks the caret one cell past
    # the text, which is what a real terminal caret does anyway.
    CW, FS = 8.86, 14.5
    X0, Y0, LH = 26, 64, 30

    lines = [
        ("p", "whoami"),
        ("o", "V Sanjay  ·  CSE (Core) @ Chennai Institute of Technology  ·  B.E. 2029  ·  CGPA 8.67"),
        ("p", "cat ~/.config/focus"),
        ("o", "Cloud infrastructure   DevOps   Distributed systems"),
        ("p", "./build.sh --all"),
        ("k", "SatQuery   hybrid satellite-image QA"),
        ("k", "CourseC    AI course builder"),
        ("p", "echo $BELIEF"),
        ("q", "predict what needs perception, calculate what can be calculated"),
    ]

    # ---- timeline ----
    t, spans = 0.6, []
    for kind, text in lines:
        n = len(text) + (2 if kind == "p" else 0)
        dur = n * (0.032 if kind == "p" else 0.010)
        spans.append((t, t + dur))
        t += dur + (0.30 if kind == "p" else 0.16)
    HOLD, FADE = 3.2, 0.4
    clear = t + HOLD
    T = clear + FADE + 0.6

    body = [f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>']
    body.append(window(W, H, "sanjay@cloud:~ — zsh — 100×24"))
    defs = []

    for i, ((kind, text), (t0, t1)) in enumerate(zip(lines, spans)):
        y = Y0 + i * LH
        indent = X0
        pre = ""
        if kind == "p":
            pre = (f'<text x="{X0}" y="{y}" font-family="{MONO}" font-size="{FS}" fill="{GREEN}">$</text>')
            indent = X0 + CW * 2
            fill, weight = CYAN, "600"
        elif kind == "k":
            pre = (f'<text x="{X0}" y="{y}" font-family="{MONO}" font-size="{FS}" fill="{GREEN}">ok</text>'
                   f'<text x="{X0-8}" y="{y}" font-family="{MONO}" font-size="{FS}" fill="{DIM}">[</text>'
                   f'<text x="{X0+2*CW}" y="{y}" font-family="{MONO}" font-size="{FS}" fill="{DIM}">]</text>')
            indent = X0 + CW * 4
            fill, weight = SLATE, "400"
        elif kind == "q":
            fill, weight = PURPLE, "400"
            text = f'"{text}"'
        else:
            fill, weight = SLATE, "400"

        w = len(text) * CW + 4
        cid = f"c{i}"
        defs.append(
            f'<clipPath id="{cid}"><rect x="{indent-2}" y="{y-FS}" width="0" height="{FS+8}">'
            f'<animate attributeName="width" values="0;0;{w};{w};0;0" '
            f'keyTimes="{kt([0, t0, t1, clear, clear+0.001, T], T)}" '
            f'dur="{T}s" repeatCount="indefinite"/></rect></clipPath>'
        )
        # prompt sigil / [ok] marker fades in with its line
        if pre:
            body.append(
                f'<g opacity="0">{pre}<animate attributeName="opacity" values="0;0;1;1;0;0" '
                f'keyTimes="{kt([0, t0-0.001, t0, clear, clear+0.001, T], T)}" '
                f'dur="{T}s" repeatCount="indefinite"/></g>'
            )
        body.append(
            f'<g clip-path="url(#{cid})"><text x="{indent}" y="{y}" font-family="{MONO}" '
            f'font-size="{FS}" font-weight="{weight}" fill="{fill}" '
            f'xml:space="preserve">{text}</text></g>'
        )
        # caret rides the reveal edge
        body.append(
            f'<rect y="{y-FS+2}" width="8.4" height="{FS+2}" fill="{CYAN}" opacity="0">'
            f'<animate attributeName="x" values="{indent};{indent};{indent+w-4};{indent+w-4}" '
            f'keyTimes="{kt([0, t0, t1, T], T)}" dur="{T}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
            f'keyTimes="{kt([0, t0-0.001, t0, t1+0.12, t1+0.13, T], T)}" '
            f'dur="{T}s" repeatCount="indefinite"/></rect>'
        )

    # resting caret after the last line, blinking
    ry = Y0 + len(lines) * LH
    body.append(
        f'<rect x="{X0}" y="{ry-FS+2}" width="8.4" height="{FS+2}" fill="{CYAN}" opacity="0">'
        f'<animate attributeName="opacity" values="0;0;1;0;1;0;1;0;0" '
        f'keyTimes="{kt([0, spans[-1][1], spans[-1][1]+0.4, spans[-1][1]+0.8, spans[-1][1]+1.2, spans[-1][1]+1.6, spans[-1][1]+2.0, clear, T], T)}" '
        f'dur="{T}s" repeatCount="indefinite"/></rect>'
    )

    return head(W, H, "Animated terminal: whoami") + "<defs>" + "".join(defs) + "</defs>" + "".join(body) + "</svg>"


# --------------------------------------------------------------------------
# 2. k8s.svg -- scheduler placing pods across nodes, then scaling
# --------------------------------------------------------------------------
def k8s():
    W, H = 1000, 300
    T = 12.0
    body = [f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>']
    defs = [
        f'<linearGradient id="wire" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="{CYAN}" stop-opacity="0.9"/>'
        f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>',
        f'<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
        f'<feGaussianBlur stdDeviation="3" result="b"/><feMerge>'
        f'<feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
    ]

    body.append(f'<text x="26" y="34" font-family="{MONO}" font-size="13" fill="{DIM}">'
                f'$ kubectl apply -f deploy.yaml  <tspan fill="{GREEN}">--replicas=15</tspan></text>')

    # control plane
    cx, cy = 120, 168
    body.append(f'<rect x="{cx-72}" y="{cy-54}" width="144" height="108" rx="12" '
                f'fill="{PANEL}" stroke="{PURPLE}" stroke-opacity="0.5"/>')
    body.append(f'<circle cx="{cx}" cy="{cy-14}" r="19" fill="none" stroke="{PURPLE}" stroke-width="2" filter="url(#glow)">'
                f'<animate attributeName="r" values="17;21;17" dur="3s" repeatCount="indefinite"/>'
                f'<animate attributeName="stroke-opacity" values="1;0.45;1" dur="3s" repeatCount="indefinite"/></circle>')
    # helm-ish spokes
    body.append(f'<g stroke="{PURPLE}" stroke-width="2" stroke-linecap="round">'
                f'<animateTransform attributeName="transform" type="rotate" '
                f'from="0 {cx} {cy-14}" to="360 {cx} {cy-14}" dur="14s" repeatCount="indefinite"/>'
                + "".join(
                    f'<line x1="{cx}" y1="{cy-14}" x2="{cx}" y2="{cy-14-26}" '
                    f'transform="rotate({a} {cx} {cy-14})" opacity="0.75"/>' for a in range(0, 360, 60))
                + "</g>")
    body.append(f'<text x="{cx}" y="{cy+34}" font-family="{MONO}" font-size="12" fill="{PURPLE}" '
                f'text-anchor="middle">control-plane</text>')
    body.append(f'<text x="{cx}" y="{cy+50}" font-family="{MONO}" font-size="10" fill="{DIM}" '
                f'text-anchor="middle">scheduler · etcd</text>')

    # worker nodes
    nodes = [(430, 74), (430, 168), (430, 262)]
    NW, NH = 500, 74
    for ni, (nx, ny) in enumerate(nodes):
        body.append(f'<rect x="{nx}" y="{ny-NH/2}" width="{NW}" height="{NH}" rx="10" '
                    f'fill="{PANEL}" stroke="{EDGE}"/>')
        body.append(f'<text x="{nx+14}" y="{ny-NH/2+20}" font-family="{MONO}" font-size="11" '
                    f'fill="{SLATE}">node-{ni+1}</text>')
        body.append(f'<circle cx="{nx+NW-16}" cy="{ny-NH/2+16}" r="4" fill="{GREEN}">'
                    f'<animate attributeName="opacity" values="1;0.25;1" dur="2s" '
                    f'begin="{ni*0.4}s" repeatCount="indefinite"/></circle>')
        # wire from control plane
        body.append(f'<line x1="{cx+72}" y1="{cy}" x2="{nx}" y2="{ny}" stroke="{EDGE}" stroke-width="1.5"/>')
        body.append(f'<line x1="{cx+72}" y1="{cy}" x2="{nx}" y2="{ny}" stroke="url(#wire)" stroke-width="2.5" '
                    f'stroke-dasharray="40 260" stroke-dashoffset="300">'
                    f'<animate attributeName="stroke-dashoffset" values="300;0" dur="2.2s" '
                    f'begin="{ni*0.5}s" repeatCount="indefinite"/></line>')

    # pods: 3 baseline per node, then 2 more each on the scale event.
    # Geometry is drawn about the origin and translated into place by the outer
    # <g>, so the inner scale animation pops from the pod's own centre.
    scale_at = 6.0
    births = []
    for ni, (nx, ny) in enumerate(nodes):
        for pi in range(5):
            # 5 pods of 26px on a 66px pitch, centred in the node box
            px = nx + (NW - (4 * 66 + 26)) / 2 + pi * 66 + 13
            born = (0.5 + ni * 0.35 + pi * 0.28) if pi < 3 else (scale_at + ni * 0.3 + (pi - 3) * 0.35)
            births.append(born)
            col = CYAN if pi < 3 else GREEN
            keys = [0, born - 0.001, born, born + 0.35, T]
            body.append(
                f'<g transform="translate({px},{ny})">'
                f'<g opacity="0">'
                f'<rect x="-13" y="-13" width="26" height="26" rx="6" fill="{col}" '
                f'fill-opacity="0.16" stroke="{col}"/>'
                f'<circle cx="0" cy="0" r="3.5" fill="{col}"/>'
                f'<animate attributeName="opacity" values="0;0;0.4;1;1" keyTimes="{kt(keys,T)}" '
                f'dur="{T}s" repeatCount="indefinite"/>'
                f'<animateTransform attributeName="transform" type="scale" values="0.4;0.4;1.25;1;1" '
                f'keyTimes="{kt(keys,T)}" dur="{T}s" repeatCount="indefinite"/>'
                f'</g></g>'
            )

    # replica counter -- steps as pods actually come up
    body.append(f'<text x="{W-96}" y="34" font-family="{MONO}" font-size="13" fill="{SLATE}" '
                f'text-anchor="end">ready</text>')
    order = sorted(births)
    for i, b in enumerate(order):
        n = i + 1
        nxt = order[i + 1] if i + 1 < len(order) else T
        col = GREEN if n == 15 else CYAN
        body.append(
            f'<text x="{W-26}" y="34" font-family="{MONO}" font-size="13" fill="{col}" '
            f'font-weight="700" text-anchor="end" opacity="0">{n}/15'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
            f'keyTimes="{kt([0, b+0.34, b+0.35, nxt+0.34, nxt+0.35, T], T)}" '
            f'dur="{T}s" repeatCount="indefinite"/></text>')
    return head(W, H, "Kubernetes scheduler placing pods") + "<defs>" + "".join(defs) + "</defs>" + "".join(body) + "</svg>"


# --------------------------------------------------------------------------
# 3. metrics.svg -- observability panel
# --------------------------------------------------------------------------
def metrics():
    import math, random
    W, H = 1000, 260
    T = 10.0
    rnd = random.Random(7)
    body = [f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>']
    defs = [
        f'<linearGradient id="fillc" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0.35"/>'
        f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>',
        f'<linearGradient id="fillp" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{PURPLE}" stop-opacity="0.35"/>'
        f'<stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></linearGradient>',
    ]

    body.append(f'<text x="26" y="30" font-family="{MONO}" font-size="13" fill="{DIM}">'
                f'$ watch -n1 <tspan fill="{CYAN}">promtool query instant</tspan></text>')

    panels = [(26, 50, 300, "cpu_usage{node}", CYAN, "fillc", "62%"),
              (350, 50, 300, "mem_working_set", PURPLE, "fillp", "3.4 GiB")]

    for (px, py, pw, label, col, grad, val) in panels:
        ph = 170
        body.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" fill="{PANEL}" stroke="{EDGE}"/>')
        body.append(f'<text x="{px+14}" y="{py+22}" font-family="{MONO}" font-size="11" fill="{SLATE}">{label}</text>')
        body.append(f'<text x="{px+pw-14}" y="{py+22}" font-family="{MONO}" font-size="13" fill="{col}" '
                    f'font-weight="700" text-anchor="end">{val}</text>')
        for gi in range(1, 4):
            gy = py + 34 + gi * 30
            body.append(f'<line x1="{px+12}" y1="{gy}" x2="{px+pw-12}" y2="{gy}" stroke="{GRID}"/>')

        n = 44
        x0, x1 = px + 12, px + pw - 12
        base = py + 148
        amp = 82
        pts = []
        for i in range(n):
            v = 0.45 + 0.30 * math.sin(i / 4.4 + (0 if col == CYAN else 1.7)) + rnd.uniform(-0.09, 0.09)
            v = max(0.06, min(0.97, v))
            pts.append((x0 + (x1 - x0) * i / (n - 1), base - amp * v))
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        area = d + f" L{pts[-1][0]:.1f},{base} L{pts[0][0]:.1f},{base} Z"
        body.append(f'<path d="{area}" fill="url(#{grad})" opacity="0">'
                    f'<animate attributeName="opacity" values="0;1" keyTimes="0;1" dur="1.6s" fill="freeze"/></path>')
        L = 1400
        body.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2" stroke-linejoin="round" '
                    f'stroke-linecap="round" stroke-dasharray="{L}" stroke-dashoffset="{L}">'
                    f'<animate attributeName="stroke-dashoffset" values="{L};0" dur="2.6s" fill="freeze"/></path>')
        # tracer dot sweeping the series
        body.append(f'<circle r="4" fill="{col}" filter="url(#glow2)">'
                    f'<animateMotion path="{d}" dur="{T}s" repeatCount="indefinite" rotate="0"/>'
                    f'<animate attributeName="opacity" values="0;1;1" keyTimes="0;0.2;1" dur="{T}s" repeatCount="indefinite"/>'
                    f'</circle>')

    defs.append(f'<filter id="glow2" x="-200%" y="-200%" width="500%" height="500%">'
                f'<feGaussianBlur stdDeviation="3.5" result="b"/><feMerge>'
                f'<feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')

    # right rail: SLO bars
    rx, ry, rw = 674, 50, 300
    body.append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="170" rx="10" fill="{PANEL}" stroke="{EDGE}"/>')
    body.append(f'<text x="{rx+14}" y="{ry+22}" font-family="{MONO}" font-size="11" fill="{SLATE}">service_level</text>')
    slos = [("api  ", 0.995, GREEN), ("queue", 0.972, CYAN), ("build", 0.918, AMBER), ("infra", 0.999, GREEN)]
    for i, (nm, v, c) in enumerate(slos):
        by = ry + 48 + i * 30
        bw = rw - 130
        body.append(f'<text x="{rx+14}" y="{by+4}" font-family="{MONO}" font-size="11" fill="{DIM}" '
                    f'xml:space="preserve">{nm}</text>')
        body.append(f'<rect x="{rx+70}" y="{by-7}" width="{bw}" height="10" rx="5" fill="{PANEL2}"/>')
        body.append(f'<rect x="{rx+70}" y="{by-7}" width="0" height="10" rx="5" fill="{c}">'
                    f'<animate attributeName="width" values="0;{bw*v:.1f}" dur="1.5s" '
                    f'begin="{0.3+i*0.18}s" fill="freeze"/></rect>')
        body.append(f'<text x="{rx+rw-14}" y="{by+4}" font-family="{MONO}" font-size="11" fill="{c}" '
                    f'text-anchor="end">{v*100:.1f}%</text>')

    return head(W, H, "Live metrics panel") + "<defs>" + "".join(defs) + "</defs>" + "".join(body) + "</svg>"


# --------------------------------------------------------------------------
# 4. divider.svg -- animated scanline rule
# --------------------------------------------------------------------------
def divider():
    W, H = 1000, 18
    defs = [f'<linearGradient id="dg" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{EDGE}" stop-opacity="0"/>'
            f'<stop offset="0.5" stop-color="{EDGE}" stop-opacity="1"/>'
            f'<stop offset="1" stop-color="{EDGE}" stop-opacity="0"/></linearGradient>',
            f'<linearGradient id="ds" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>'
            f'<stop offset="0.5" stop-color="{CYAN}" stop-opacity="1"/>'
            f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>']
    body = [f'<line x1="0" y1="9" x2="{W}" y2="9" stroke="url(#dg)" stroke-width="1.5"/>',
            f'<g><rect x="-260" y="7.5" width="260" height="3" fill="url(#ds)" rx="1.5"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0,0;{W+300},0" '
            f'dur="4.5s" repeatCount="indefinite"/></g>',
            f'<circle cx="{W/2}" cy="9" r="3" fill="{CYAN}">'
            f'<animate attributeName="opacity" values="0.25;1;0.25" dur="2.4s" repeatCount="indefinite"/></circle>']
    return head(W, H, "divider") + "<defs>" + "".join(defs) + "</defs>" + "".join(body) + "</svg>"


# --------------------------------------------------------------------------
# 5. repos.svg -- real code volume per repository, bars growing in
# --------------------------------------------------------------------------
def repos():
    # (repo, lines of code, primary language, accent)
    data = [
        ("Geo_Logics",            14925, "Python",     CYAN),
        ("AI_powered_learning",    7234, "Python",     CYAN),
        ("GeoLogics",              4684, "Python",     PURPLE),
        ("kodeZ",                  4112, "Python",     PURPLE),
        ("codeZ",                  1380, "Python",     BLUE),
        ("Operating-Systems",       792, "C / Shell",  GREEN),
        ("job",                     302, "JavaScript", AMBER),
        ("new-app",                 191, "TypeScript", AMBER),
        ("Jenkins-zero-to-hero-",    33, "CI config",  PINK),
    ]
    W = 1000
    top, rh = 62, 30
    H = top + len(data) * rh + 20
    mx = max(v for _, v, _, _ in data)
    # bar origin clears the longest repo name (21 chars at 12px mono ~= 151px)
    lx, bx = 26, 278            # label column, bar origin
    bw = W - bx - 96            # bar track width

    body = [f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>']
    body.append(f'<text x="{lx}" y="30" font-family="{MONO}" font-size="13" fill="{DIM}">'
                f'$ cloc --by-repo  <tspan fill="{CYAN}">--sort=desc</tspan></text>')
    body.append(f'<text x="{W-26}" y="30" font-family="{MONO}" font-size="11" fill="{DIM}" '
                f'text-anchor="end">lines of code</text>')
    body.append(f'<line x1="{lx}" y1="44" x2="{W-26}" y2="44" stroke="{EDGE}" stroke-opacity="0.5"/>')

    for i, (name, v, lang, col) in enumerate(data):
        y = top + i * rh + 14
        w = bw * v / mx
        body.append(f'<text x="{lx}" y="{y+4}" font-family="{MONO}" font-size="12" fill="{SLATE}">{name}</text>')
        body.append(f'<text x="{bx-18}" y="{y+4}" font-family="{MONO}" font-size="10" fill="{DIM}" '
                    f'text-anchor="end">{lang}</text>')
        body.append(f'<rect x="{bx}" y="{y-7}" width="{bw}" height="13" rx="3" fill="{PANEL2}"/>')
        body.append(
            f'<rect x="{bx}" y="{y-7}" width="0" height="13" rx="3" fill="{col}" fill-opacity="0.85">'
            f'<animate attributeName="width" values="0;{w:.1f}" dur="1.3s" '
            f'begin="{0.25+i*0.13}s" fill="freeze" calcMode="spline" '
            f'keyTimes="0;1" keySplines="0.2 0.9 0.3 1"/></rect>')
        # leading edge highlight
        body.append(
            f'<rect x="{bx}" y="{y-7}" width="2.5" height="13" fill="{WHITE}" opacity="0">'
            f'<animate attributeName="x" values="{bx};{bx+w-2.5:.1f}" dur="1.3s" '
            f'begin="{0.25+i*0.13}s" fill="freeze" calcMode="spline" '
            f'keyTimes="0;1" keySplines="0.2 0.9 0.3 1"/>'
            f'<animate attributeName="opacity" values="0;0.9;0" dur="1.3s" '
            f'begin="{0.25+i*0.13}s" fill="freeze"/></rect>')
        body.append(f'<text x="{W-26}" y="{y+4}" font-family="{MONO}" font-size="12" fill="{col}" '
                    f'font-weight="700" text-anchor="end" opacity="0">{v:,}'
                    f'<animate attributeName="opacity" values="0;1" dur="0.4s" '
                    f'begin="{1.25+i*0.13}s" fill="freeze"/></text>')

    return head(W, H, "Code volume per repository") + "".join(body) + "</svg>"


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("terminal", terminal), ("k8s", k8s), ("metrics", metrics),
                     ("divider", divider), ("repos", repos)):
        p = os.path.join(OUT, f"{name}.svg")
        open(p, "w").write(fn())
        print(f"{p}  {os.path.getsize(p):,} bytes")

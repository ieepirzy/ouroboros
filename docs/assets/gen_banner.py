# Generates docs/assets/banner.svg. Run: python3 gen_banner.py (writes banner.svg in the current directory).
import math, random

W, H = 1280, 320
cx, cy, r = 190, 160, 100
random.seed(7)

def lerp(a, b, t): return a + (b - a) * t
def hexc(c): return tuple(int(c[i:i+2], 16) for i in (1, 3, 5))
def mix(c1, c2, t):
    a, b = hexc(c1), hexc(c2)
    return "#%02x%02x%02x" % tuple(round(lerp(x, y, t)) for x, y in zip(a, b))

def pt(deg, rad=r):
    a = math.radians(deg)
    return cx + rad * math.cos(a), cy + rad * math.sin(a)

out = []
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="title desc">')
out.append('<title id="title">ouroboros</title>')
out.append('<desc id="desc">A serpent eating its own tail, drawn as a copper circuit trace around a small grid of hardwired weights.</desc>')
out.append('<defs>'
           '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
           '<stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#111a24"/></linearGradient>'
           '<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">'
           '<stop offset="0" stop-color="#e8a45c" stop-opacity="0.18"/><stop offset="1" stop-color="#e8a45c" stop-opacity="0"/></radialGradient>'
           '<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">'
           '<path d="M32 0H0V32" fill="none" stroke="#1f2a36" stroke-width="1"/></pattern>'
           '</defs>')
out.append(f'<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>')
out.append(f'<rect width="{W}" height="{H}" rx="18" fill="url(#grid)" opacity="0.55"/>')

# background routing traces (manhattan), faint
traces = [
    [(300, 88), (360, 88), (380, 68), (1220, 68)],
    [(300, 232), (370, 232), (392, 254), (1220, 254)],
    [(1040, 68), (1040, 40)], [(1120, 254), (1120, 284)],
]
for tr in traces:
    d = "M" + " L".join(f"{x} {y}" for x, y in tr)
    out.append(f'<path d="{d}" fill="none" stroke="#24313f" stroke-width="2" stroke-linejoin="round"/>')
    for (x, y) in (tr[0], tr[-1]):
        out.append(f'<circle cx="{x}" cy="{y}" r="3.5" fill="#0d1117" stroke="#2f3f50" stroke-width="2"/>')

out.append(f'<circle cx="{cx}" cy="{cy}" r="150" fill="url(#glow)"/>')

# serpent body: tapered copper trace, tail -> head, clockwise
start, sweep = -78, 343          # tail angle, degrees travelled
n = 60
head_c, tail_c = "#f2b366", "#7a4a22"
for i in range(n):
    t0, t1 = i / n, (i + 1) / n
    a0, a1 = start + sweep * t0, start + sweep * t1 + 0.6
    w = lerp(4, 17, t1 ** 0.8)
    x0, y0 = pt(a0); x1, y1 = pt(a1)
    out.append(f'<path d="M{x0:.2f} {y0:.2f} A{r} {r} 0 0 1 {x1:.2f} {y1:.2f}" fill="none" '
               f'stroke="{mix(tail_c, head_c, t1)}" stroke-width="{w:.2f}" stroke-linecap="round"/>')

# vias along the body (inner centre line)
for k in range(1, 9):
    a = start + sweep * (k / 9)
    x, y = pt(a)
    rr = lerp(1.4, 3.2, k / 9)
    out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{rr:.2f}" fill="#0d1117" opacity="0.85"/>')

# head: round and friendly, big eye with a sparkle, little blush, nibbling the tail tip
ha = start + sweep
hx, hy = pt(ha)
tang = ha + 96                     # clockwise tangent, nudged inward to follow the curve
out.append(f'<g transform="translate({hx:.2f} {hy:.2f}) rotate({tang:.2f})">'
           f'<path d="M-8 -12 C4 -19 22 -18 29 -8 C32 -4 32 -1 30 1 L24 1 L30 3 C31 7 29 11 25 14 '
           f'C17 20 2 19 -8 12 Z" fill="{head_c}"/>'
           f'<circle cx="11" cy="-4" r="6.2" fill="#0d1117"/>'
           f'<circle cx="13.4" cy="-6.4" r="2.2" fill="#ffffff"/>'
           f'<circle cx="9.2" cy="-1.6" r="1" fill="#ffffff" opacity="0.8"/>'
           f'<ellipse cx="17" cy="7.5" rx="4.2" ry="2.6" fill="#ff8fa3" opacity="0.55"/>'
           f'</g>')

# hardwired-weight die in the centre: filled = nonzero weight, empty = eliminated zero
N, cell, gap = 6, 12, 4
size = N * cell + (N - 1) * gap
x0, y0 = cx - size / 2, cy - size / 2
pad = 10
out.append(f'<rect x="{x0-pad}" y="{y0-pad}" width="{size+2*pad}" height="{size+2*pad}" rx="6" '
           f'fill="#0f161e" stroke="#3a4b5c" stroke-width="2"/>')
for s in range(N):  # pins
    p = x0 + s * (cell + gap) + cell / 2
    for (ax, ay, bx, by) in ((p, y0-pad, p, y0-pad-8), (p, y0+size+pad, p, y0+size+pad+8),
                             (x0-pad, p - x0 + y0, x0-pad-8, p - x0 + y0),
                             (x0+size+pad, p - x0 + y0, x0+size+pad+8, p - x0 + y0)):
        out.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="#3a4b5c" stroke-width="2" stroke-linecap="round"/>')
for i in range(N):
    for j in range(N):
        x = x0 + j * (cell + gap); y = y0 + i * (cell + gap)
        v = random.random()
        if v < 0.3:
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="2" fill="none" stroke="#2a3744" stroke-width="1.5" stroke-dasharray="2 2"/>')
        else:
            op = lerp(0.35, 1.0, (v - 0.3) / 0.7)
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="2" fill="#e8a45c" opacity="{op:.2f}"/>')

# wordmark
mono = "ui-monospace, SFMono-Regular, 'JetBrains Mono', Menlo, Consolas, monospace"
sans = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Helvetica, Arial, sans-serif"
out.append(f'<text x="420" y="160" font-family="{mono}" font-size="76" font-weight="700" fill="#e6edf3" letter-spacing="-1">ouroboros</text>')
out.append(f'<text x="424" y="205" font-family="{sans}" font-size="26" fill="#e8a45c">fixed weights in, silicon out.</text>')
out.append(f'<text x="424" y="238" font-family="{sans}" font-size="18" fill="#8b949e">An open compiler from model checkpoints to hardwired-weight hardware.</text>')
out.append('</svg>')
open("banner.svg", "w").write("\n".join(out))

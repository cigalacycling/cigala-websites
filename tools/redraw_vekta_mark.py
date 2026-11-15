"""Redraw the yellow Vekta mark in coaching/webp/vekta-white.webp sharply (Matteo 15 Nov: the yellow part looked wrong).
The old mark was un-mixed from a small 280 px logo: soft, with a dark fringe. This draws the same shape (two rounded
L-strokes with a thin gap, and a dot) at 8x and scales down, and keeps the white "vekta" wordmark as it was.
  python3 -I tools/redraw_vekta_mark.py [R GAP [DST]]   (used: 23 2.8 -> coaching/webp/vekta-white-v2.webp)
"""
import sys, math
from PIL import Image, ImageDraw
ROOT = __file__.rsplit('/tools/', 1)[0] + '/'
SRC = ROOT + 'coaching/webp/vekta-white.webp'
Y = (251, 192, 1)
R = float(sys.argv[1]) if len(sys.argv) > 1 else 23
GAP = float(sys.argv[2]) if len(sys.argv) > 2 else 2.8
W = 22.5            # stroke width (measured)
CX, CY = 71.0, 69.0 # where the two strokes cross (centre of the vertical and the horizontal)
S = 8

def path(pts_fn, n=400): return [pts_fn(i / n) for i in range(n + 1)]
def upper(t):   # from the top, down, quarter-turn to the right, to the right end
    a, b = (CY - R) - 13.0, 1.0   # straight length on top
    L1 = (CY - R) - (3 + W / 2); L2 = math.pi / 2 * R; L3 = 138 - W / 2 + 1 - (CX + R)
    d = t * (L1 + L2 + L3)
    if d < L1: return (CX, 3 + W / 2 + d)
    d -= L1
    if d < L2: th = d / R; return (CX + R - R * math.cos(th), CY - R + R * math.sin(th))
    return (CX + R + (d - L2), CY)
def lower(t):   # from the left end, right, quarter-turn down, to the bottom
    L1 = (CX - R) - (4 + W / 2); L2 = math.pi / 2 * R; L3 = 134 - W / 2 - (CY + R)
    d = t * (L1 + L2 + L3)
    if d < L1: return (4 + W / 2 + d, CY)
    d -= L1
    if d < L2: th = d / R; return (CX - R + R * math.sin(th), CY + R - R * math.cos(th))
    return (CX, CY + R + (d - L2))

def brush(dr, pts, w, fill):
    r = w * S / 2
    for x, y in pts: dr.ellipse((x * S - r, y * S - r, x * S + r, y * S + r), fill=fill)

old = Image.open(SRC).convert('RGBA')
big = Image.new('RGBA', (old.width * S, old.height * S), (0, 0, 0, 0))
mask = Image.new('L', big.size, 0); dm = ImageDraw.Draw(mask)
brush(dm, path(lower), W, 255)
brush(dm, path(upper), W + 2 * GAP, 0)      # the thin gap between the strokes
brush(dm, path(upper), W, 255)
dm.ellipse(((103 - 9.6) * S, (40 - 9.6) * S, (103 + 9.6) * S, (40 + 9.6) * S), fill=255)
mark = Image.new('RGBA', big.size, Y + (255,)); mark.putalpha(mask)
mark = mark.resize(old.size, Image.LANCZOS)
out = old.copy()
px = out.load()
for y in range(out.height):          # clear the old mark (everything left of the wordmark)
    for x in range(0, 160): px[x, y] = (0, 0, 0, 0)
out.alpha_composite(mark)
dst = sys.argv[3] if len(sys.argv) > 3 else ROOT + 'coaching/webp/vekta-white-v2.webp'
out.save(dst, 'WEBP', quality=90, method=6, exact=True)
print('saved', dst, out.size)

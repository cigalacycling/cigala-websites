"""White (monochrome) version of a partner logo for the dark site: the background, and a solid coloured box
the logo sits in (Zwift orange, TrainingPeaks navy, Cycling Ireland green), become transparent; the lettering
and mark become white. Matteo, 15 Nov: "As seen in" logos without the white squares.
  python3 -I tools/monologo.py SRC DST [--nobox] [--holes]
"""
import sys
from collections import deque
from PIL import Image

def flood(px, W, H, seeds, same):
    seen = [[False] * W for _ in range(H)]; q = deque(seeds)
    while q:
        x, y = q.popleft()
        if 0 <= x < W and 0 <= y < H and not seen[y][x] and same(px[x, y]):
            seen[y][x] = True; q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return seen

def mono(src, dst, pad=6, nobox=False, holes=False):
    im = Image.open(src).convert('RGBA'); W, H = im.size; px = im.load()
    near = lambda c, ref, t=48: c[3] < 30 if ref[3] < 30 else (c[3] < 30 or sum(abs(c[i] - ref[i]) for i in range(3)) < t)   # a transparent background only matches transparent pixels
    edge = [(x, y) for x in range(W) for y in (0, H - 1)] + [(x, y) for y in range(H) for x in (0, W - 1)]
    bgc = px[0, 0]
    bg = flood(px, W, H, edge, lambda c: near(c, bgc))
    # a solid box inside? take the colour just inside the remaining area's bounding box
    xs = [x for y in range(H) for x in range(W) if not bg[y][x]]; ys = [y for y in range(H) for x in range(W) if not bg[y][x]]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    box = px[min(x1, x0 + 2), min(y1, y0 + 2)]
    area = (x1 - x0 + 1) * (y1 - y0 + 1)
    boxed = sum(1 for y in range(y0, y1 + 1) for x in range(x0, x1 + 1) if near(px[x, y], box)) > 0.35 * area
    boxed = boxed and not nobox
    if boxed:
        inner = flood(px, W, H, [(x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2)], lambda c: near(c, box, 90))
        for y in range(H):
            for x in range(W):
                bg[y][x] = bg[y][x] or inner[y][x]
    out = Image.new('RGBA', im.size, (255, 255, 255, 0)); op = out.load()
    for y in range(H):
        for x in range(W):
            if not bg[y][x] and px[x, y][3] > 30 and not (holes and sum(px[x, y][:3]) / 3 < 90):   # holes: dark lettering inside a shape stays see-through
                op[x, y] = (255, 255, 255, 255)
    out = out.crop(out.getbbox())
    canvas = Image.new('RGBA', (out.width + 2 * pad, out.height + 2 * pad), (255, 255, 255, 0)); canvas.alpha_composite(out, (pad, pad))
    canvas.save(dst, 'WEBP', quality=90, method=6)
    return boxed

if __name__ == '__main__':
    print(mono(sys.argv[1], sys.argv[2], nobox='--nobox' in sys.argv, holes='--holes' in sys.argv))

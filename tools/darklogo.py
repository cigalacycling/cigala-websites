"""Make a logo with a baked-in white background usable on the dark site.
Only the white background connected to the image edge becomes transparent (inner whites stay),
and near-black text/lines become white, except inside keep-boxes (e.g. a dark round logo).
  python3 -I tools/darklogo.py SRC DST [x0,y0,x1,y1 ...]
"""
import sys
from collections import deque
from PIL import Image

def darkify(src, dst, keep=()):
    im = Image.open(src).convert('RGB'); W, H = im.size; px = im.load()
    white = lambda p: min(p) >= 225 and max(p) - min(p) < 30
    bg = [[False] * W for _ in range(H)]
    q = deque((x, y) for x in range(W) for y in (0, H - 1)) + deque((x, y) for y in range(H) for x in (0, W - 1))
    while q:
        x, y = q.popleft()
        if 0 <= x < W and 0 <= y < H and not bg[y][x] and white(px[x, y]):
            bg[y][x] = True; q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    out = Image.new('RGBA', im.size); op = out.load()
    inkeep = lambda x, y: any(a <= x <= c and b <= y <= d for a, b, c, d in keep)
    for y in range(H):
        for x in range(W):
            r, g, b = px[x, y]; lum = (r + g + b) / 3; sat = max(r, g, b) - min(r, g, b)
            if bg[y][x]: op[x, y] = (255, 255, 255, 0)
            elif sat < 40 and lum < 140 and not inkeep(x, y):
                # dark ink -> white; anti-aliased edge pixels next to the background fade out
                op[x, y] = (255, 255, 255, 255)
            elif sat < 40 and lum >= 140 and not inkeep(x, y) and any(
                    0 <= x + dx < W and 0 <= y + dy < H and bg[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                op[x, y] = (255, 255, 255, int(255 - lum))  # grey edge between ink and background
            else: op[x, y] = (r, g, b, 255)
    out.save(dst, 'WEBP', quality=90, method=6)

if __name__ == '__main__':
    darkify(sys.argv[1], sys.argv[2], [tuple(map(int, k.split(','))) for k in sys.argv[3:]])

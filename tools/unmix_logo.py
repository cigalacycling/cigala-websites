"""Logo on a white background -> transparent, for the dark site. Unlike darklogo.py this keeps the
anti-aliased edges: alpha is how far each pixel is from white, colour is un-mixed from white.
Grey/black ink becomes white; coloured ink (Vekta yellow) keeps its colour. Optional crop box and upscale.
  python3 -I tools/unmix_logo.py SRC DST [x0,y0,x1,y1] [scale]
"""
import sys
from PIL import Image

def unmix(src, dst, box=None, scale=1):
    im = Image.open(src).convert('RGBA')
    if box: im = im.crop(box)
    if scale != 1: im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
    px = im.load(); out = Image.new('RGBA', im.size); op = out.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a0 = px[x, y]
            a = 1 - min(r, g, b) / 255
            if a < 0.03 or a0 < 10: op[x, y] = (255, 255, 255, 0); continue
            c = [max(0, min(255, round((v - (1 - a) * 255) / a))) for v in (r, g, b)]
            if max(c) - min(c) < 60: c = [255, 255, 255]          # neutral ink -> white
            op[x, y] = (*c, round(a * a0))
    out = out.crop(out.getbbox()); out.save(dst, 'WEBP', quality=90, method=6, exact=True)
    return out.size

if __name__ == '__main__':
    box = tuple(map(int, sys.argv[3].split(','))) if len(sys.argv) > 3 else None
    print(unmix(sys.argv[1], sys.argv[2], box, int(sys.argv[4]) if len(sys.argv) > 4 else 1))

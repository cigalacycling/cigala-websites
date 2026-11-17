"""Transparent Vivify logo (Marine 17 Nov): the white V + VIVIFY SPORTS from the master logo, teal square removed.
Alpha comes from how far each pixel is from the teal towards white, so the anti-aliased edges stay smooth.
  python3 -I tools/vivify_logo.py  -> vivify/webp/vivify-logo-white.webp (+ .png)
"""
import glob, os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/vivify/'
src = Image.open(glob.glob(ROOT + 'img-orig/0e1488_f038fcb12444476fab18be6dc4bf29e1*')[0]).convert('RGB')
teal = (25, 68, 75)
out = Image.new('RGBA', src.size, (255, 255, 255, 0))
px, po = src.load(), out.load()
for y in range(src.size[1]):
    for x in range(src.size[0]):
        r, g, b = px[x, y]
        a = max((r - teal[0]) / (255 - teal[0]), (g - teal[1]) / (255 - teal[1]), (b - teal[2]) / (255 - teal[2]))
        a = max(0.0, min(1.0, a))
        if a > 0.02: po[x, y] = (255, 255, 255, round(a * 255))
# the master file has a thin light line along its edges: clear a 16 px strip all round
W, H = out.size
for y in range(H):
    for x in range(W):
        if x < 16 or y < 16 or x >= W - 16 or y >= H - 16: po[x, y] = (255, 255, 255, 0)
# faint pixels along the file's outer edge are not part of the logo: crop on clearly visible pixels only
mask = out.getchannel('A').point(lambda v: 255 if v > 90 else 0)
bbox = mask.getbbox(); pad = 12
out = out.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(src.size[0], bbox[2] + pad), min(src.size[1], bbox[3] + pad)))
out.save(ROOT + 'webp/vivify-logo-white.webp', 'WEBP', quality=95, method=6)
out.save(ROOT + 'vivify-logo-white.png')
print(out.size)

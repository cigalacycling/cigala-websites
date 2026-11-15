"""Marine Lenehan's author image for the end of her articles (Matteo 15 Nov 2026), same style as Matteo's
(tools/make_author_signature.py): her portrait with the background removed (rembg isnet-general-use with alpha matting,
coaching/vivify/marine-lenehan-cutout.webp, from vivifysports.com/about) and her signature in white
(coaching/vivify/marine-lenehan-signature-white.webp, cut from her signature image with tools/unmix_logo.py).
  python3 -I tools/make_marine_signature.py -> coaching/vivify/marine-lenehan-author-signature.webp
"""
from PIL import Image
ROOT = __file__.rsplit('/tools/', 1)[0] + '/'
photo = Image.open(ROOT + 'coaching/vivify/marine-lenehan-cutout.webp').convert('RGBA')
sig = Image.open(ROOT + 'coaching/vivify/marine-lenehan-signature-white.webp').convert('RGBA')
w, h = photo.size; a = photo.getchannel('A'); px = a.load(); fade = int(h * .2)
for y in range(h - fade, h):
    k = (h - y) / fade
    for x in range(w): px[x, y] = int(px[x, y] * k)
photo.putalpha(a)
sw = int(w * .82); sig = sig.resize((sw, int(sig.height * sw / sig.width)), Image.LANCZOS)
H = h + sig.height // 2
out = Image.new('RGBA', (w, H), (0, 0, 0, 0)); out.alpha_composite(photo, (0, 0)); out.alpha_composite(sig, ((w - sw) // 2, H - sig.height - 6))
out.thumbnail((720, 1000), Image.LANCZOS)
dst = ROOT + 'coaching/vivify/marine-lenehan-author-signature.webp'
out.save(dst, 'WEBP', quality=90, method=6); print(dst, out.size)

"""Author image for the end of Matteo's blog posts (Matteo 15 Nov 2026): the white-jersey cut-out (transparent background)
with his signature in white underneath, replacing the childhood photo on a white box (it showed as a white card on the dark site).
  python3 -I tools/make_author_signature.py  ->  coaching/brand/matteo-cigala-author-signature.webp
"""
from PIL import Image
ROOT = __file__.rsplit('/tools/', 1)[0] + '/'
photo = Image.open(ROOT + 'survey/NfmCmGsjq4LL9bTAi38NXN/matteo-white.png').convert('RGBA')     # 900x1071, transparent
sig = Image.open(ROOT + 'tourspages/img/cigala-tours-signature.webp').convert('RGBA')           # 924x251, white
# soft fade at the bottom of the photo so the signature sits on it
w, h = photo.size; a = photo.getchannel('A'); px = a.load(); fade = int(h * .22)
for y in range(h - fade, h):
    k = (h - y) / fade
    for x in range(w): px[x, y] = int(px[x, y] * k)
photo.putalpha(a)
sw = int(w * .78); sig = sig.resize((sw, int(sig.height * sw / sig.width)), Image.LANCZOS)
H = h + sig.height // 2
out = Image.new('RGBA', (w, H), (0, 0, 0, 0)); out.alpha_composite(photo, (0, 0)); out.alpha_composite(sig, ((w - sw) // 2, H - sig.height - 6))
out.thumbnail((720, 1000), Image.LANCZOS)
dst = ROOT + 'coaching/brand/matteo-cigala-author-signature.webp'
out.save(dst, 'WEBP', quality=90, method=6); print(dst, out.size)

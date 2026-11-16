"""WebP copies of Tours staging images, made on demand by the page builders.

    from tours_img import webp
    im = webp('https://staging.tours.cigalacycling.com/wp-content/uploads/2026/06/x.jpg', 1200)   # or a media id
    im['url'], im['alt'], im['id']

- Source: the largest original on staging (the full-size file next to a "-scaled" copy). WebP quality 90, at most maxw wide.
- Alt text: the alt the image already has in the media library (CLAUDE.md: keep existing alt). If it has none,
  pass alt=... (a description of the photo). The alt is set on the new media item too.
- Uploaded once to Tours STAGING and recorded in stg-tours/media-webp.json under 'src-<id>-<maxw>'.
"""
import os, io, sys, json, time, ssl, urllib.request, urllib.error
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
HOST = 'staging.tours.cigalacycling.com'   # never the live host
B = f'https://{HOST}/wp-json/wp/v2'
MAP = ROOT + 'stg-tours/media-webp.json'
OUTDIR = ROOT + 'webp-tours/'
ctx = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
lib = {x['id']: x for x in json.load(open(ROOT + 'stg-tours/media-library.json'))}
by_url = {x['source_url'].replace('https://tours.', 'https://staging.tours.'): x for x in lib.values()}

def _req(url, data=None, headers=None, method=None):
    assert url.startswith(f'https://{HOST}/'), url
    url = urllib.parse.quote(url, safe=':/?=&%')
    for i in range(20):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers or {'User-Agent': 'Mozilla/5.0'}, method=method), context=ctx, timeout=120).read()
        except urllib.error.HTTPError as e:
            if e.code in (502, 503, 504): time.sleep(3); continue
            raise RuntimeError(f'{e.code} {url}: {e.read()[:300]}')
        except Exception:
            time.sleep(3)
    raise RuntimeError('unreachable ' + url)

def media(src):
    """media-library entry for a staging media id or upload URL (any size variant, live or staging host)."""
    if isinstance(src, int): return lib[src]
    u = src.replace('https://tours.', 'https://staging.tours.')
    if u in by_url: return by_url[u]
    import re
    base = re.sub(r'-\d+x\d+(\.\w+)$', r'\1', u)          # a resized copy -> the original
    if base in by_url: return by_url[base]
    stem = base.rsplit('.', 1)[0]
    for k, v in by_url.items():
        if k.rsplit('.', 1)[0] in (stem, stem + '-scaled'): return v
    raise KeyError('not in the staging media library: ' + src)

def webp(src, maxw=1600, alt=None, redo=False, trim=False):
    m = media(src)
    key = f"src-{m['id']}-{maxw}" + ('-trim' if trim else '')
    done = json.load(open(MAP))
    if key in done and not redo: return done[key]
    u = m['source_url']
    raw = None
    if '-scaled.' in u:   # WordPress keeps the full-size upload next to the -scaled copy
        try: raw = _req(u.replace('-scaled.', '.'))
        except RuntimeError: raw = None
    raw = raw or _req(u)
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(raw)))   # phone photos: apply the camera's rotation tag
    im = im.convert('RGBA') if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info) else im.convert('RGB')
    w0 = im.size
    if trim:   # product photos on white (the rental bike): crop the empty white around the subject, keep a small margin
        from PIL import ImageChops
        bb = ImageChops.difference(im.convert('RGB'), Image.new('RGB', im.size, (255, 255, 255))).convert('L').point(lambda v: 255 if v > 18 else 0).getbbox()
        if bb:
            mx, my = round((bb[2] - bb[0]) * .04), round((bb[3] - bb[1]) * .06)
            im = im.crop((max(0, bb[0] - mx), max(0, bb[1] - my), min(im.width, bb[2] + mx), min(im.height, bb[3] + my)))
    if im.width > maxw: im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    a = (m.get('alt_text') or '').strip() or alt
    assert a, f'no alt text for {u}: pass alt='
    stem = os.path.basename(u).rsplit('.', 1)[0].replace('-scaled', '')
    fn = f'cigala-tours-{stem}-{maxw}{"-trim" if trim else ""}.webp'
    os.makedirs(OUTDIR, exist_ok=True)
    im.save(OUTDIR + fn, 'WEBP', quality=90)
    r = json.loads(_req(B + '/media', data=open(OUTDIR + fn, 'rb').read(), method='POST',
                        headers={'Content-Type': 'image/webp', 'Content-Disposition': f'attachment; filename="{fn}"', 'User-Agent': 'Mozilla/5.0'}))
    _req(B + f'/media/{r["id"]}', data=json.dumps({'alt_text': a}).encode(), method='POST', headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    done = json.load(open(MAP))
    done[key] = {'id': r['id'], 'url': r['source_url'], 'alt': a, 'from': list(w0), 'size': list(im.size), 'orig': m['id']}
    json.dump(done, open(MAP, 'w'), indent=1, ensure_ascii=False)
    print('  webp', key, w0, '->', im.size, r['id'])
    return done[key]

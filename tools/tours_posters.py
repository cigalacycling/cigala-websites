"""Trip posters (the photo next to each trip's intro) with the map badge in our style (Matteo 16 Nov).

The live posters have a map badge baked into the top-right corner (a slate tile with a white country).
This paints our badge over it: a dark tile with the country in our map style (tourspages/maps/badge-<slug>.svg,
made by tours_route_maps.py) and the tour's area in green. The badge sits in the same place on every
poster: 66-96% across, 4-35% down (as a share of the image width).

    python3 -I tools/tours_posters.py [slug ...]

Output: WebP q90 from the largest original, uploaded to Tours STAGING with the original's alt text,
recorded in stg-tours/media-webp.json as 'poster-<slug>'. build_tours_trips.py uses it when present.
"""
import os, io, re, sys, json
from PIL import Image, ImageDraw, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tours_img import _req, media, B, MAP, OUTDIR, ROOT

BOX = (.655, .036, .964, .356)   # cover box (x0, y0, x1, y1) as a share of the poster width: a little larger than the old badge

def svg_png(svg_path, px):
    """render the badge SVG to a transparent PNG with Node Playwright (the pre-installed Chromium)"""
    import subprocess, tempfile
    tmp = tempfile.mkdtemp() + '/b.png'
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:%d,height:%d}});"
          "const fs=require('fs');let s=fs.readFileSync(%s,'utf8').replace('<svg ','<svg width=\"%d\" height=\"%d\" ');"
          "await p.setContent('<html><body style=\"margin:0;background:transparent\">'+s+'</body></html>');"
          "await p.screenshot({path:%s,omitBackground:true});await b.close()})()") % (px, px, json.dumps(svg_path), px, px, json.dumps(tmp))
    subprocess.run(['node', '-e', js], check=True)
    return Image.open(tmp).convert('RGBA')

def poster(slug):
    m = json.load(open(ROOT + f'stg-tours/out/list-trip-{slug}.json'))['main']
    src = re.search(r'<div class="cardimg"><img[^>]+src="([^"]+)"', m)
    if not src: return print(slug, 'no poster')
    done = json.load(open(MAP))
    orig = next(v['orig'] for v in done.values() if isinstance(v, dict) and v.get('url') == src.group(1))
    o = media(orig); u = o['source_url']
    raw = None
    if '-scaled.' in u:
        try: raw = _req(u.replace('-scaled.', '.'))
        except RuntimeError: raw = None
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(raw or _req(u)))).convert('RGB')
    if im.width > 1200: im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
    W = im.width
    x0, y0, x1, y1 = [round(v * W) for v in BOX]
    s = x1 - x0; r = round(s * .13)
    tile = Image.new('RGBA', (s, y1 - y0), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    d.rounded_rectangle((0, 0, s - 1, y1 - y0 - 1), radius=r, fill=(12, 14, 16, 255), outline=(255, 255, 255, 40), width=max(1, s // 180))
    mp = svg_png(ROOT + f'tourspages/maps/badge-{slug}.svg', round(s * .86))
    tile.alpha_composite(mp, ((s - mp.width) // 2, (y1 - y0 - mp.height) // 2))
    out = im.convert('RGBA'); out.alpha_composite(tile, (x0, y0)); out = out.convert('RGB')
    if os.environ.get('DRY'): out.save(os.environ['DRY'] + f'poster-{slug}.jpg'); return print(slug, 'dry run')
    fn = f'cigala-tours-poster-{slug}.webp'
    os.makedirs(OUTDIR, exist_ok=True)
    out.save(OUTDIR + fn, 'WEBP', quality=90)
    alt = (o.get('alt_text') or '').strip() or done[next(k for k, v in done.items() if isinstance(v, dict) and v.get('url') == src.group(1))]['alt']
    r_ = json.loads(_req(B + '/media', data=open(OUTDIR + fn, 'rb').read(), method='POST',
                         headers={'Content-Type': 'image/webp', 'Content-Disposition': f'attachment; filename="{fn}"', 'User-Agent': 'Mozilla/5.0'}))
    _req(B + f'/media/{r_["id"]}', data=json.dumps({'alt_text': alt}).encode(), method='POST', headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    done = json.load(open(MAP))
    done['poster-' + slug] = {'id': r_['id'], 'url': r_['source_url'], 'alt': alt, 'size': list(out.size), 'orig': orig}
    json.dump(done, open(MAP, 'w'), indent=1, ensure_ascii=False)
    print(slug, out.size, r_['id'])

if __name__ == '__main__':
    import tours_route_maps as trm
    for slug in sys.argv[1:] or trm.POSTER_BADGES:
        poster(slug)

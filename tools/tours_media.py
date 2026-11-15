"""Make WebP (quality 90) copies of the Tours homepage images from the largest originals
and upload them to Tours staging. Writes stg-tours/media-webp.json  {key: {id, url, alt}}.

Sources are staging media IDs (originals already on the site) or local files.
Re-running skips keys that are already uploaded.
Needs the proxy-injected staging credential (no secrets here).
"""
import os, io, json, time, ssl, urllib.request, urllib.error, urllib.parse
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
B = 'https://staging.tours.cigalacycling.com/wp-json/wp/v2'
OUTDIR = ROOT + 'webp-tours/'
MAP = ROOT + 'stg-tours/media-webp.json'
ctx = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
lib = {x['id']: x for x in json.load(open(ROOT + 'stg-tours/media-library.json'))}

# key: (source, max width, alt)   source = staging media id, or a local path
# alt None = keep the alt text the image already has on the site
A = {
    'hero': (4893, 2400, 'Cigala Cycling Tours riders celebrating on the coast in Cyprus'),
    'custom': (4440, 1600, None),
    'cta': (4594, 1600, None),
    'story': (4900, 1600, None),
    'matteo': ('survey/NfmCmGsjq4LL9bTAi38NXN/matteo-white.png', 900, 'Matteo Cigala in Cigala Cycling kit'),
    'guide-flanders': (3209, 1000, None),
    'guide-como': ('tourspages/img/guides-1.jpg', 1000, 'Cycling Lake Como: Ghisallo, Sormano and the Giro di Lombardia roads'),
    'guide-pack': (6281, 1000, None),
    'logo': (4282, 240, None),
    'logo-mdd': (8587, 400, None),
    'logo-lombardia': (858, 400, None),
    'logo-strade': (857, 400, None),
    'logo-algarve': (856, 400, None),
    # trip cards: featured photo of each live trip page
    'trip-discover-the-algarve-granfondo': (4955, 1200, None),
    'trip-chianti-gran-fondo-strade-bianche': (5162, 1200, None),
    'trip-tour-of-flanders-experience': (3215, 1200, None),
    'trip-cyprus-crossing-gravel': (4889, 1200, None),
    'trip-tuscany-epic-gravel': (4440, 1200, None),
    'trip-maratona-dles-dolomites': (8609, 1200, None),
    'trip-dolomites': (4867, 1200, None),
    'trip-italian-alps': (4927, 1200, None),
    'trip-alpine-gravel-escape': (6113, 1200, None),
    'trip-french-alps': (4877, 1200, None),
    'trip-wonderful-slovenia': (4959, 1200, None),
    'trip-lake-garda-and-stelvio': (4911, 1200, None),
    'trip-lake-garda-gravel': (6378, 1200, None),
    'trip-italys-coast-to-coast': (4972, 1200, None),
    'trip-lake-como-gran-fondo-il-lombardia': (7740, 1200, None),
    # logo file Matteo sent on 15 Nov (proper border); keeps the logo's existing alt text
    'logo-v2': ('tours/brand/ccToursLogo-matteo-2026-11-15.png', 343, None),
    # signature, cut from the coaching blog image Matteo-Cigala-6-years-old.png, white ink on transparent
    'signature': ('webp-tours/cigala-tours-signature.webp', 924, "Matteo Cigala's signature"),
    # trip-list pages
    'hero-road': (4911, 2400, None),
    'hero-gravel': (7766, 2400, None),
    'hero-granfondo': (8601, 2400, None),
    'hero-italian': (8616, 2400, None),
    'card-alpine-gravel-escape': ('webp-tours/cigala-tours-card-alpine-gravel-escape.webp', 1100, "Alpine Gravel Escape cycling tour: 320 km, 9,300 m climbing"),
    'card-chianti-gran-fondo-strade-bianche': ('webp-tours/cigala-tours-card-chianti-gran-fondo-strade-bianche.webp', 1100, "Chianti Strade Bianche cycling tour: 350 km, 6,000 m climbing"),
    'card-cyprus-crossing-gravel': ('webp-tours/cigala-tours-card-cyprus-crossing-gravel.webp', 1100, "Cyprus Crossing cycling tour: 415 km, 8,700 m climbing"),
    'card-discover-the-algarve-granfondo': ('webp-tours/cigala-tours-card-discover-the-algarve-granfondo.webp', 1100, "Algarve & Gran Fondo cycling tour: 420 km, 5,800 m climbing"),
    'card-dolomites': ('webp-tours/cigala-tours-card-dolomites.webp', 1100, "Dolomites cycling tour: 290 km, 8,200 m climbing"),
    'card-french-alps': ('webp-tours/cigala-tours-card-french-alps.webp', 1100, "French Alps cycling tour: 485 km, 13,700 m climbing"),
    'card-italian-alps': ('webp-tours/cigala-tours-card-italian-alps.webp', 1100, "Italian Alps cycling tour: 380 km, 10,200 m climbing"),
    'card-italys-coast-to-coast': ('webp-tours/cigala-tours-card-italys-coast-to-coast.webp', 1100, "Italy'S Coast to Coast cycling tour: 470 km, 4,600 m climbing"),
    'card-lake-como-il-lombardia': ('webp-tours/cigala-tours-card-lake-como-il-lombardia.webp', 1100, "Lake Como & Il Lombardia cycling tour: 410 km, 5,300 m climbing"),
    'card-lake-garda-gravel': ('webp-tours/cigala-tours-card-lake-garda-gravel.webp', 1100, "Lake Garda Gravel cycling tour: 340 km, 3,500 m climbing"),
    'card-lake-garda-stelvio': ('webp-tours/cigala-tours-card-lake-garda-stelvio.webp', 1100, "Lake Garda & Stelvio cycling tour: 460 km, 4,000 m climbing"),
    'card-maratona-dles-dolomites': ('webp-tours/cigala-tours-card-maratona-dles-dolomites.webp', 1100, "Maratona Dles Dolomites cycling tour: 250\u2013350 km, 5,000\u20137,000 m climbing"),
    'card-tour-of-flanders-experience': ('webp-tours/cigala-tours-card-tour-of-flanders-experience.webp', 1100, "Tour of Flanders Experience cycling tour: 120\u2013300 km, 1,000\u20133,000 m climbing"),
    'card-tuscany-epic-gravel': ('webp-tours/cigala-tours-card-tuscany-epic-gravel.webp', 1100, "Tuscany Epic cycling tour: 490 km, 7,100 m climbing"),
    'card-wonderful-slovenia': ('webp-tours/cigala-tours-card-wonderful-slovenia.webp', 1100, "Wonderful Slovenia cycling tour: 440 km, 6,600 m climbing"),
    # event logos Matteo sent on 15 Nov (newest versions); keep the alt text the old logos had
    'logo-algarve-v2': ('tours/brand/events/algarve-granfondo-wordmark.png', 800, None),
    'logo-strade-v2': ('tours/brand/events/strade-bianche-gran-fondo.png', 400, None),
    'logo-lombardia-v2': ('tours/brand/events/il-lombardia-gran-fondo.png', 400, None),
    # guest photos: square crops from the originals matching the live crops (made by hand, already WebP q90)
    'guest-steve': ('webp-tours/cigala-tours-guest-steve.webp', 240, 'Person smiling while riding a celeste-colored Bianchi road bicycle'),
    'guest-hank': ('webp-tours/cigala-tours-guest-hank.webp', 240, 'Cycling Alps Cigala Cycling'),
    'guest-william': ('webp-tours/cigala-tours-guest-william.webp', 240, None),
    'guest-andreas': ('webp-tours/cigala-tours-guest-andreas.webp', 240, None),
    'guest-fraser': ('webp-tours/cigala-tours-guest-fraser.webp', 240, None),
    'guest-mike': ('webp-tours/cigala-tours-guest-mike.webp', 240, None),
}
GUEST_ALT = {'logo-v2': 4282, 'logo-algarve-v2': 856, 'logo-strade-v2': 857, 'logo-lombardia-v2': 858, 'guest-william': 5949, 'guest-andreas': 5932, 'guest-fraser': 5934, 'guest-mike': 5933}

def req(url, data=None, headers=None, method=None, tries=20):
    url = urllib.parse.quote(url, safe=':/?=&%')  # filenames like ©MolingAlex
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers or {'User-Agent': 'Mozilla/5.0'}, method=method), context=ctx, timeout=120)
            return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (502, 503, 504): time.sleep(3); continue
            raise RuntimeError(f'{e.code} {url}: {e.read()[:300]}')
        except Exception:
            time.sleep(3)  # proxy could not connect (DNS still spreading): nothing reached the server
    raise RuntimeError('unreachable ' + url)

def original(mid):
    u = lib[mid]['source_url']
    if '-scaled.' in u:  # WordPress keeps the full-size upload next to the -scaled copy
        try: return req(u.replace('-scaled.', '.'))
        except RuntimeError: pass
    return req(u)

os.makedirs(OUTDIR, exist_ok=True)
done = json.load(open(MAP)) if os.path.exists(MAP) else {}
for key, (src, maxw, alt) in A.items():
    if key in done: continue
    raw = original(src) if isinstance(src, int) else open(ROOT + src, 'rb').read()
    if isinstance(src, str) and src.endswith('.webp'):   # already final: upload as is, no second encode
        fn = os.path.basename(src); im = Image.open(io.BytesIO(raw)); w0 = im.size
        alt = alt or lib[GUEST_ALT[key]]['alt_text']
        r = json.loads(req(B + '/media', data=raw, method='POST', headers={'Content-Type': 'image/webp', 'Content-Disposition': f'attachment; filename="{fn}"', 'User-Agent': 'Mozilla/5.0'}))
        req(B + f'/media/{r["id"]}', data=json.dumps({'alt_text': alt}).encode(), method='POST', headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
        done[key] = {'id': r['id'], 'url': r['source_url'], 'alt': alt, 'from': w0, 'size': w0}
        json.dump(done, open(MAP, 'w'), indent=1, ensure_ascii=False); print(key, r['id']); continue
    im = Image.open(io.BytesIO(raw))
    im = im.convert('RGBA') if im.mode in ('RGBA', 'LA', 'P') and 'transparency' in im.info or im.mode in ('RGBA', 'LA') else im.convert('RGB')
    w0 = im.size
    if im.width > maxw: im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    fn = f'cigala-tours-{key}.webp'
    im.save(OUTDIR + fn, 'WEBP', quality=90)
    if alt is None: alt = lib[src]['alt_text'] if isinstance(src, int) else lib[GUEST_ALT[key]]['alt_text'] if key in GUEST_ALT else ''
    assert alt, key
    body = open(OUTDIR + fn, 'rb').read()
    r = json.loads(req(B + '/media', data=body, method='POST', headers={'Content-Type': 'image/webp', 'Content-Disposition': f'attachment; filename="{fn}"', 'User-Agent': 'Mozilla/5.0'}))
    req(B + f'/media/{r["id"]}', data=json.dumps({'alt_text': alt}).encode(), method='POST', headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    done[key] = {'id': r['id'], 'url': r['source_url'], 'alt': alt, 'from': w0, 'size': im.size}
    json.dump(done, open(MAP, 'w'), indent=1, ensure_ascii=False)
    print(key, w0, '->', im.size, r['id'])
print(len(done), 'images in', MAP)

"""Tours share images (Matteo 16 Nov, after the Coaching session's og:image check of staging.tours):
1) branded 1200x630 cards, in the homepage card's layout (brand-assets/share/tours-share.html), for the hub pages
   that used a plain photo or the homepage card: /destinations/, /trips/, /guides/, /trips/gravel-trips/;
2) a 1200x630 crop of the full-size photo for pages whose share image was an upright 576px "large" size
   (shows as a small thumbnail on Facebook/LinkedIn).
JPG q90 (WhatsApp/LinkedIn don't show WebP previews). Set as Rank Math Facebook image (Twitter uses it).
Before: stg-tours/backup/share-before.json.   python3 -I tools/tours_share_cards.py
"""
import os, sys, json, re, io, subprocess, urllib.request, urllib.parse, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tours_img import _req, B, media
from PIL import Image, ImageOps
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
OUT = ROOT + 'brand-assets/share/tours/'
S = 'https://staging.tours.cigalacycling.com'
CARDS = {   # path: (photo media id, photo position, headline lines, sub line, alt)
 '/destinations/': (3719, '50% 45%', ['Cycling', 'destinations', 'in Europe'], 'Italy, France, Portugal, Spain, Slovenia, Cyprus and more, ridden with our guides.', 'Riders on a Dolomites pass road below the Sella towers'),
 '/trips/': (4955, '50% 50%', ['Upcoming', 'bike tours', '2027'], 'Road, gravel and gran fondo tours across Europe, led by former professional cyclists.', 'Cyclists racing through a crowd with flags at a Gran Fondo'),
 '/guides/': (4856, '50% 40%', ['Cycling', 'guides & tips'], 'Climbs, regions, packing and planning, from riders who know these roads.', 'The Stelvio Pass hairpins from above'),
 '/trips/gravel-trips/': (7767, '50% 55%', ['Gravel', 'bike tours'], 'White roads of Tuscany, Alpine passes and Cyprus, with full support.', 'A group of riders on a Tuscan gravel road'),
}
CROPS = {'/guides/corsica-cycling-guide/': None, '/guides/the-tuscany-gravel-tour-riding-the-tuscany-trail/': None, '/guides/road-vs-gravel-bike-holiday/': 7766,   # its own photo is only 481px wide
         '/guides/gravel-cycling-cyprus/': None, '/guides/stelvio-pass-cycling-guide/': None, '/trips/lake-garda-gravel/': None}

def get(u): return urllib.request.urlopen(urllib.request.Request(urllib.parse.quote(u, safe=':/?=&%'), headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read()
def original(mid):
    try: u = media(mid)['source_url']
    except Exception: u = json.loads(_req(B + f'/media/{mid}?_fields=source_url'))['source_url']
    for v in (u.replace('-scaled.', '.'), u):
        try: return ImageOps.exif_transpose(Image.open(io.BytesIO(get(v)))).convert('RGB')
        except Exception: pass
def page_info(path):
    h = get(S + path + '?nc=1').decode('utf-8', 'replace')
    og = (re.search(r'property="og:image" content="([^"]+)"', h) or [None, None])[1]
    pid = re.search(r'postid-(\d+)|page-id-(\d+)', h); pid = int(pid.group(1) or pid.group(2))
    title = H.unescape(re.search(r'<title>(.*?)</title>', h).group(1))
    return pid, og, title
def upload(fn, alt):
    r = json.loads(_req(B + '/media', data=open(OUT + fn, 'rb').read(), method='POST',
                        headers={'Content-Type': 'image/jpeg', 'Content-Disposition': f'attachment; filename="{fn}"', 'User-Agent': 'Mozilla/5.0'}))
    _req(B + f'/media/{r["id"]}', data=json.dumps({'alt_text': alt}).encode(), method='POST', headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    return r
def set_meta(pid, r):
    _req(S + '/wp-json/rankmath/v1/updateMeta', data=json.dumps({'objectType': 'post', 'objectID': pid, 'meta': {
        'rank_math_facebook_image': r['source_url'], 'rank_math_facebook_image_id': r['id'], 'rank_math_twitter_use_facebook': 'on'}}).encode(),
        method='POST', headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})

os.makedirs(OUT, exist_ok=True)
bk = ROOT + 'stg-tours/backup/share-before.json'
before = json.load(open(bk)) if os.path.exists(bk) else {}
tpl = open(ROOT + 'brand-assets/share/tours-share.html').read()
for path, (mid, pos, lines, sub, alt) in CARDS.items():
    if before.get(path, {}).get('new'): continue
    pid, og, title = page_info(path); before.setdefault(path, {'id': pid, 'og_image': og})
    slug = path.strip('/').replace('/', '-')
    original(mid).save(OUT + f'photo-{slug}.jpg', quality=92)
    h = re.sub(r'url\([^)]*cigala-tours-hero\.webp\) 50% 45%', f'url(photo-{slug}.jpg) {pos}', tpl)
    h = re.sub(r'<h1>.*?</h1>', '<h1>' + '<br>'.join(H.escape(x) for x in lines) + '</h1>', h, flags=re.S)
    h = re.sub(r'<div class="sub">.*?</div>', f'<div class="sub">{H.escape(sub)}</div>', h, flags=re.S)
    h = h.replace('../../', '../../../')
    open(OUT + f'card-{slug}.html', 'w').write(h)
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1200,height:630}});"
          f"await p.goto('file://{OUT}card-{slug}.html',{{waitUntil:'networkidle'}});await p.evaluate(()=>document.fonts.ready);"
          f"await p.screenshot({{path:'{OUT}cigala-tours-share-{slug}.jpg',type:'jpeg',quality:90}});await b.close()}})()")
    subprocess.run(['node', '-e', js], check=True)
    r = upload(f'cigala-tours-share-{slug}.jpg', f'{alt}: {title.split(" | ")[0]} - Cigala Cycling Tours'); set_meta(pid, r); print('card', path, r['id']); before[path]['new'] = r['id']; json.dump(before, open(bk, 'w'), indent=1)
for path in CROPS:
    if before.get(path, {}).get('new'): continue
    pid, og, title = page_info(path); before.setdefault(path, {'id': pid, 'og_image': og})
    fm = CROPS[path] or json.loads(_req(B + f'/{"posts" if "/guides/" in path else "pages"}/{pid}?_fields=featured_media'))['featured_media']
    im = original(fm); W, Hh = im.size; th = round(W * 630 / 1200)
    if th <= Hh: top = round((Hh - th) * .45); im = im.crop((0, top, W, top + th))
    else: tw = round(Hh * 1200 / 630); l = (W - tw) // 2; im = im.crop((l, 0, l + tw, Hh))
    im = im.resize((1200, 630), Image.LANCZOS); slug = path.strip('/').split('/')[-1]
    im.save(OUT + f'cigala-tours-share-{slug}.jpg', quality=90)
    alt = (media(fm).get('alt_text') or title).strip()
    r = upload(f'cigala-tours-share-{slug}.jpg', alt); set_meta(pid, r); print('crop', path, r['id'], 'from', fm, (W, Hh)); before[path]['new'] = r['id']; json.dump(before, open(bk, 'w'), indent=1)
json.dump(before, open(bk, 'w'), indent=1)

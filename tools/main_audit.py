"""SEO / share-preview audit of cigalacycling.com staging (all published pages and posts)."""
import json, re, ssl, sys, urllib.request, html as H
from html.parser import HTMLParser
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
BASE = 'https://staging.cigalacycling.com'
def get(u, method='GET'):
    req = urllib.request.Request(u, method=method, headers={'User-Agent': 'Mozilla/5.0 audit'})
    class NR(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k): return None
    op = urllib.request.build_opener(NR, urllib.request.HTTPSHandler(context=ctx))
    try:
        r = op.open(req, timeout=30); return r.status, r.read().decode('utf-8', 'replace') if method == 'GET' else '', None
    except urllib.error.HTTPError as e: return e.code, '', e.headers.get('Location')
urls = []
for t in ['pages', 'posts']:
    _, b, _ = get(f'{BASE}/wp-json/wp/v2/{t}?per_page=100&_fields=link')
    urls += [x['link'] for x in json.loads(b)]
rows = []; links = set(); imgs = set()
for u in urls:
    code, s, _ = get(u + '?nc=1')
    head = s[:s.find('</head>')]
    m = lambda p: (re.search(p, head, re.S) or [None, None])[1]
    r = {'url': u.replace(BASE, ''), 'status': code,
         'title': H.unescape(m(r'<title>(.*?)</title>') or '').strip(),
         'desc': H.unescape(m(r'<meta name="description" content="([^"]*)"') or ''),
         'og_title': H.unescape(m(r'<meta property="og:title" content="([^"]*)"') or ''),
         'og_desc': H.unescape(m(r'<meta property="og:description" content="([^"]*)"') or ''),
         'og_image': (m(r'<meta property="og:image" content="([^"]*)"') or '').split('/')[-1],
         'tw_image': (m(r'<meta name="twitter:image" content="([^"]*)"') or ''),
         'lang': m(r'<html[^>]*lang="([^"]+)"'),
         'h1': len(re.findall(r'<h1\b', s)), 'robots': m(r"<meta name='robots' content='([^']*)'"),
         'canonical': m(r'<link rel="canonical" href="([^"]*)"')}
    bad = []
    for b in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', s, re.S):
        try: json.loads(b)
        except Exception as e: bad.append(str(e)[:60])
    r['jsonld_bad'] = bad
    r['img_noalt'] = [re.search(r'src="([^"]+)"', i).group(1).split('/')[-1] for i in re.findall(r'<img\b[^>]*>', s) if re.search(r'src="', i) and not re.search(r'\salt="[^"]+"', i)]
    r['http'] = sorted(set(re.findall(r'(?:href|src)="(http://[^"]+)"', s)))
    for h in re.findall(r'href="([^"#]+)"', s):
        if h.startswith(('mailto:', 'tel:')): continue
        if h.startswith('/') or 'cigalacycling.com' in h: links.add(h if h.startswith('http') else BASE + h)
    for i in re.findall(r'<img\b[^>]*\ssrc="([^"]+)"', s): imgs.add(i)
    rows.append(r)
for r in rows:
    flags = []
    if not (30 <= len(r['title']) <= 60): flags.append(f"title {len(r['title'])} chars")
    if not (70 <= len(r['desc']) <= 160): flags.append(f"desc {len(r['desc'])} chars")
    if r['h1'] != 1: flags.append(f"h1 x{r['h1']}")
    if r['jsonld_bad']: flags.append('bad JSON-LD')
    if r['img_noalt']: flags.append(f"no alt: {r['img_noalt']}")
    if r['http']: flags.append(f"http: {r['http'][:3]}")
    if not r['og_image'] or 'logo' in r['og_image'].lower() or 'cropped' in r['og_image']: flags.append(f"og:image {r['og_image'] or 'missing'}")
    if r['og_image'].endswith('.webp'): flags.append('og:image is webp (some apps do not show webp previews)')
    if not r['og_desc']: flags.append('og:description missing')
    print(json.dumps({k: r[k] for k in ['url', 'status', 'title', 'desc', 'og_title', 'og_image', 'lang', 'h1', 'robots']}, ensure_ascii=False))
    print('   FLAGS:', flags or 'none')
dup = {}
for k in ['title', 'desc', 'og_title', 'og_desc']:
    seen = {}
    for r in rows: seen.setdefault(r[k], []).append(r['url'])
    for v, us in seen.items():
        if len(us) > 1 and v: print('DUPLICATE', k, us, v[:70])
print('internal links:', len(links)); badl = []
for l in sorted(links):
    if '/wp-' in l or 'xmlrpc' in l or '/feed' in l: continue
    c, _, loc = get(l.replace('https://cigalacycling.com', BASE), 'HEAD')
    if c != 200: badl.append((c, l, loc))
print('links not 200:', badl)
badi = []
for i in sorted(imgs):
    c, _, loc = get(i if i.startswith('http') else BASE + i, 'HEAD')
    if c != 200: badi.append((c, i))
print('images not 200:', badi)

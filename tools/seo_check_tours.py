"""Compare Tours STAGING pages with the live SEO baseline (tours/baseline-2026-11-15.json).

Usage: python3 -I tools/seo_check_tours.py /about/ /contact/ ...
For each page: title, meta description, robots, canonical path, og:title, H1 and H2 (case-insensitive; the
design shows headings in capitals with CSS), image alt texts of the live page that are missing now
(the logo in the old header/footer is ignored), live internal links that are gone, and schema types.
Exit code 1 if anything that must stay the same changed.
"""
import os, re, sys, json, ast, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from push_tours_wp import req

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
LIVE, STG = 'https://tours.cigalacycling.com', 'https://staging.tours.cigalacycling.com'
base = {p['url'][len(LIVE):]: p for p in json.load(open(ROOT + 'tours/baseline-2026-11-15.json'))}
lst = lambda v: ast.literal_eval(v) if isinstance(v, str) and v.startswith('[') else (v or [])
T = lambda x: re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x or ''))).strip()
norm = lambda x: re.sub(r'[\s’\']+', ' ', T(x).upper().replace('“', '"').replace('”', '"')).strip()

def page(path):
    code, r = req(STG + path + ('&' if '?' in path else '?') + 'seo=1')
    h = r.decode('utf-8', 'replace')
    one = lambda p: (re.search(p, h, re.S) or [None, None])[1]
    alts = [html.unescape(a) for a in re.findall(r'<img [^>]*?alt="([^"]*)"', h)]
    links = set(u.replace(STG, '') for u in re.findall(r'href="(' + re.escape(STG) + r'/[^"#?]*)', h))
    links |= set(u for u in re.findall(r'href="(/[^"#?]*)"', h))
    types = []
    for b in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', h, re.S):
        d = json.loads(b); types += [x.get('@type') for x in d.get('@graph', [d])]
    return {'status': code, 'title': html.unescape(one(r'<title>(.*?)</title>') or ''),
            'meta_description': html.unescape(one(r'<meta name="description" content="([^"]*)"') or ''),
            'robots': one(r'<meta name="robots" content="([^"]*)"') or '',
            'canonical': (one(r'<link rel="canonical" href="([^"]*)"') or '').replace(STG, LIVE),
            'og_title': html.unescape(one(r'<meta property="og:title" content="([^"]*)"') or ''),
            'h1': [T(x) for x in re.findall(r'<h1[^>]*>(.*?)</h1>', h, re.S)],
            'h2': [T(x) for x in re.findall(r'<h2[^>]*>(.*?)</h2>', h, re.S)],
            'alts': alts, 'links': links, 'types': types}

bad = 0
for path in sys.argv[1:]:
    b, s = base.get(path), page(path)
    if not b: print(path, 'not in the baseline (new page)', s['status'], s['h1']); continue
    out = []
    for k in ('title', 'meta_description', 'robots', 'canonical', 'og_title'):
        if (b[k] or '') != (s[k] or ''): out.append(f'  ! {k}: {b[k]!r} -> {s[k]!r}')
    for k in ('h1', 'h2'):
        bl, sl = [norm(x) for x in lst(b[k]) if T(x)], [norm(x) for x in s[k]]
        miss, new = [x for x in bl if x not in sl], [x for x in sl if x not in bl]
        if miss: out.append(f'  ! {k} gone: {miss}')
        if new: out.append(f'    {k} new: {new}')
        if k == 'h1' and len(s['h1']) != 1: out.append(f'  ! {len(s["h1"])} H1s')
    balts = [i['alt'] for i in lst(b['images']) if i.get('alt') and 'ccToursLogo' not in i['src']]
    gone = sorted(set(a for a in balts if a not in s['alts']))
    if gone: out.append(f'  ~ live alt texts not on the page now ({len(gone)}): {gone[:8]}')
    bl = set(u.replace(LIVE, '') or '/' for u in lst(b['internal_links']) if '/wp-content/' not in u)
    lgone = sorted(u for u in bl - s['links'] if u not in ('/', ''))
    if lgone: out.append(f'  ~ live internal links not on the page now: {lgone}')
    bt = sorted(set(t for t in lst(b['schema_types']) if t != 'Review')); st = sorted(set(s['types']))
    if bt != st: out.append(f'  ~ schema: {bt} -> {st}')
    hard = [o for o in out if o.startswith('  !')]
    bad += bool(hard)
    print(path, s['status'], 'OK' if not hard else 'CHANGED', '| h1', s['h1'], '| h2', len(s['h2']))
    for o in out: print(o)
sys.exit(1 if bad else 0)

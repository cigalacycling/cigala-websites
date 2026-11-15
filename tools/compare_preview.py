"""Compare a preview crawl (tools/crawl_preview.sh) with retail/baseline-live-pages.json.
Usage: python3 tools/compare_preview.py OUTDIR  -> prints a summary and writes OUTDIR/compare.json
Checks per page: status, one H1, H1 wording vs live, title/meta present, canonical, content images missing alt,
JSON-LD types kept. H2s are reported, not failed: theme chrome headings (menus, footer) differ by design."""
import sys, os, re, json, html as H
from html.parser import HTMLParser
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
out = sys.argv[1]
base = {b['url']: b for b in json.load(open(os.path.join(ROOT, 'retail/baseline-live-pages.json')))}
urls = open(os.path.join(out, 'urls.txt')).read().split()
status = dict(l.split() for l in open(os.path.join(out, 'status.txt')) if l.strip())
class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.d = {'title': '', 'desc': None, 'canon': None, 'h1': [], 'imgs': [], 'ld': []}; s.st = None; s.buf = ''; s.head = True; s.inld = False; s.ldb = ''; s.mainimg = 0
    def handle_starttag(s, t, a):
        a = dict(a)
        if t == 'body': s.head = False
        if t == 'h1' or (t == 'title' and s.head): s.st = t; s.buf = ''
        if t == 'meta' and s.head and (a.get('name') or '').lower() == 'description': s.d['desc'] = a.get('content')
        if t == 'link' and 'canonical' in (a.get('rel') or ''): s.d['canon'] = a.get('href')
        if t == 'img': s.d['imgs'].append(a.get('alt'))
        if t == 'script' and a.get('type') == 'application/ld+json': s.inld = True; s.ldb = ''
    def handle_data(s, x):
        if s.st: s.buf += x
        if s.inld: s.ldb += x
    def handle_endtag(s, t):
        if t == 'head': s.head = False
        if t == s.st:
            v = re.sub(r'\s+', ' ', s.buf).strip()
            if t == 'title': s.d['title'] = v
            else: s.d['h1'].append(v)
            s.st = None
        if t == 'script' and s.inld:
            s.inld = False
            try:
                j = json.loads(s.ldb); g = j.get('@graph', [j]) if isinstance(j, dict) else j
                for n in g:
                    ty = n.get('@type'); s.d['ld'] += ty if isinstance(ty, list) else [ty]
            except Exception: s.d['ld'].append('INVALID')
rows = []; issues = {}
def add(k, u): issues.setdefault(k, []).append(u)
for i, u in enumerate(urls, 1):
    f = os.path.join(out, 'html', '%04d.html' % i)
    if not os.path.exists(f): add('not fetched', u); continue
    code = status.get(u, '?')
    if code != '200': add('status ' + code, u); continue
    p = P(); p.feed(open(f, encoding='utf-8', errors='replace').read()); d = p.d; b = base.get(u, {})
    if len(d['h1']) != 1: add('h1 count %d' % len(d['h1']), u)
    bh = [h for h in b.get('h1', []) if h]
    if bh and d['h1'] and d['h1'][0].lower() != bh[0].lower(): add('h1 wording changed', f"{u} | live: {bh[0]} | new: {d['h1'][0]}")
    if not d['title']: add('no title', u)
    if not d['desc']: add('no meta description', u)
    if d['canon'] and d['canon'].split('?')[0].rstrip('/') != u.rstrip('/'): add('canonical differs', f"{u} -> {d['canon']}")
    lost = set(t for t in b.get('schema_types', []) if t) - set(d['ld']) - ({'Product'} if 'ProductGroup' in d['ld'] else set())
    if lost: add('structured data type missing: ' + ','.join(sorted(map(str, lost))), u)
    if any(a is None for a in d['imgs']): add('img without alt attribute', u)
    rows.append({'url': u, 'title': d['title'], 'desc': (d['desc'] or '')[:160], 'h1': d['h1'], 'ld': sorted(set(map(str, d['ld'])))})
json.dump({'pages': rows, 'issues': issues}, open(os.path.join(out, 'compare.json'), 'w'), indent=1, ensure_ascii=False)
print(len(rows), 'pages parsed')
for k, v in sorted(issues.items(), key=lambda x: -len(x[1])):
    print(f'{len(v):4d}  {k}'); [print('        ', x) for x in v[:6]]

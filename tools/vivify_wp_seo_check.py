"""Compare Marine's WordPress draft with the live Wix SEO baseline: title, meta description, H1s, H2s per page.
  python3 -I tools/vivify_wp_seo_check.py
"""
import os, re, json, subprocess, importlib.util, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
spec = importlib.util.spec_from_file_location('b', ROOT + 'tools/build_vivify.py'); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
from html.parser import HTMLParser
src = open(ROOT + 'tools/crawl.py').read(); exec('import json\n' + src[src.index('class P('):src.index('def norm')])
S = 'https://basic-darkslategray-cod-55.hostingersite.com'
def n(x): return re.sub(r'\s+', ' ', html.unescape(x).replace('​', '')).strip().upper()
_n0 = n
def n(x): return _n0(b.fix_typos(x))   # Marine 17 Nov: typos fixed on purpose
bad = 0
for f in json.load(open(ROOT + 'vivify/wp-pages.json')):
    url = S + '/' + ('' if f == 'index.html' else f[:-5] + '/')
    body = subprocess.run(['curl', '-sS', '-L', '-m', '60', url], capture_output=True, text=True).stdout
    p = P(); p.feed(body); d = p.d
    if f in b.NEW:
        t, m, lh1, lh2 = b.NEW[f][1], b.NEW[f][2], None, None
    else:
        r = b.BASE.get(b.LIVE + b.PAGES[f]) or b.BASE[b.LIVE]
        t, m = r['title'], r.get('meta_description') or ''
        lh1 = [n(x) for x in r['h1'] if n(x)]; lh2 = set(n(x) for x in r['h2'] if n(x))
    out = []
    if n(d['title']) != n(t): out.append(f'TITLE wp="{d["title"]}" want="{t}"')
    if n(d['meta_description'] or '') != n(m): out.append(f'META wp="{(d["meta_description"] or "")[:60]}" want="{m[:60]}"')
    if len(d['h1']) != 1: out.append(f'H1 count {len(d["h1"])}')
    if lh2 is not None:
        miss = lh2 - set(n(x) for x in d['h2'])
        if miss: out.append(f'H2 missing {sorted(miss)[:3]}')
    if out: bad += 1; print(f); [print('   ', o) for o in out]
print('pages with differences:', bad)

"""Compare the Vivify preview (vivify/site/) with the live SEO baseline: title, meta description, H1s, H2s per page.

  python3 -I tools/seo_check_vivify.py
Expected differences are explained in vivify/SEO-NOTES.md.
"""
import re, os, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
spec = importlib.util.spec_from_file_location('b', ROOT + 'tools/build_vivify.py'); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
from html.parser import HTMLParser
src = open(ROOT + 'tools/crawl.py').read(); exec('import json\n' + src[src.index('class P('):src.index('def norm')])
def n(x): return re.sub(r'\s+', ' ', x.replace('​', '')).strip().upper()
_n0 = n
def n(x): return _n0(b.fix_typos(x))   # Marine 17 Nov: typos fixed on purpose
for f, path in b.PAGES.items():
    if f in b.NEW: continue
    live = b.BASE.get(b.LIVE + path) or b.BASE[b.LIVE]
    p = P(); p.feed(open(ROOT + 'vivify/site/' + f).read()); d = p.d
    out = []
    if d['title'] != live['title']: out.append('TITLE differs')
    if (d['meta_description'] or '') != (live.get('meta_description') or ''): out.append('META differs')
    lh1 = [n(x) for x in live['h1'] if n(x)]; nh1 = [n(x) for x in d['h1']]
    if lh1 != nh1: out.append(f'H1 live={lh1} new={nh1}')
    lh2 = set(n(x) for x in live['h2'] if n(x)); nh2 = set(n(x) for x in d['h2'])
    if lh2 - nh2: out.append(f'H2 missing={sorted(lh2 - nh2)}')
    if nh2 - lh2: out.append(f'H2 added={len(nh2 - lh2)}: {sorted(nh2 - lh2)[:4]}')
    print(f, 'OK' if not out else ''); [print('   ', o) for o in out]

"""Compare the staging crawl with the live baseline (CLAUDE.md: compare against the crawl after).
  python3 -I tools/compare_coaching_crawl.py stg-coaching/crawl-after-2026-11-15.json
Per page: title, meta description, H1, H2 set (footer tagline change approved), image alt texts, schema types.
"""
import sys, json, re
base = {r['url'].replace('https://coaching.cigalacycling.com', ''): r for r in json.load(open('coaching/baseline.json')) if r.get('status') == 200}
after = {r['url'].replace('https://staging.coaching.cigalacycling.com', ''): r for r in json.load(open(sys.argv[1])) if r.get('status') == 200}
FOOT = {'Cycling & Triathlon Coaching - Bike Tours - Retail': 'Train Smarter, Ride Faster'}
norm = lambda s: re.sub(r'\s+', ' ', (s or '').replace('Canda', 'Canada')).strip()
issues = 0
for path, b in sorted(base.items()):
    a = after.get(path)
    if not a: print('MISSING ON STAGING', path); issues += 1; continue
    out = []
    if norm(a.get('title')) != norm(b.get('title')): out.append(f"title: {b.get('title')!r} -> {a.get('title')!r}")
    if norm(a.get('meta_description')) != norm(b.get('meta_description')): out.append('meta changed')
    bh1 = [h for h in b.get('h1', []) if h][:1]; ah1 = a.get('h1', [])
    if len(ah1) != 1: out.append(f'{len(ah1)} H1s')
    bh2 = {FOOT.get(h, h) for h in b.get('h2', []) if h}; ah2 = {h for h in a.get('h2', []) if h}
    miss = bh2 - ah2
    if miss: out.append(f'H2 missing: {sorted(miss)[:4]}')
    balts = {i['alt'] for i in b.get('images', []) if i.get('alt')}; aalts = {i['alt'] for i in a.get('images', []) if i.get('alt')}
    lost = balts - aalts
    if lost: out.append(f'{len(lost)} alt texts not on page: {sorted(lost)[:3]}')
    if set(b.get('schema_types', [])) - set(a.get('schema_types', [])): out.append(f"schema lost: {set(b['schema_types']) - set(a['schema_types'])}")
    if out: issues += 1; print(path, '|', ' ; '.join(out))
print('pages with differences:', issues, 'of', len(base))

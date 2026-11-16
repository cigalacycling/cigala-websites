"""Matteo 16 Nov: SEO titles that say 2026 -> 2027 (Tours staging; the guides' Rank Math titles). Only the year changes.
    python3 -I tools/tours_seo_year.py [slug ...]      (no args: every post/page whose live title has 2026, from the baseline crawl)
"""
import os, re, sys, json, html, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tours_img import _req, ROOT
HOST = 'https://staging.tours.cigalacycling.com'
base = json.load(open(ROOT + 'tours/baseline-2026-11-15.json'))
pages = base.get('pages', base) if isinstance(base, dict) else base
items = pages.items() if isinstance(pages, dict) else [(p.get('url'), p) for p in pages]
want = {u.rstrip('/').rsplit('/', 1)[-1]: p['title'] for u, p in items if '2026' in (p.get('title') or '')}
if sys.argv[1:]: want = {k: v for k, v in want.items() if k in sys.argv[1:]}
posts = json.loads(_req(HOST + '/wp-json/wp/v2/posts?per_page=100&_fields=id,slug,link'))
pages_ = json.loads(_req(HOST + '/wp-json/wp/v2/pages?per_page=100&_fields=id,slug,link'))
ids = {x['slug']: ('post', x['id'], x['link']) for x in posts}; ids.update({x['slug']: ('post', x['id'], x['link']) for x in pages_})
for slug, title in want.items():
    kind, pid, link = ids[slug]
    new = html.unescape(title).replace('2026', '2027')
    r = _req(HOST + '/wp-json/rankmath/v1/updateMeta', data=json.dumps({'objectType': 'post', 'objectID': pid, 'meta': {'rank_math_title': new}}).encode(),
             method='POST', headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    page = urllib.request.urlopen(urllib.request.Request(link.replace('https://tours.', 'https://staging.tours.') + '?nc=1', headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read().decode()
    print(slug, '->', re.search(r'<title>(.*?)</title>', page).group(1))

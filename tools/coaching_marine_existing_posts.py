"""Marine's articles that were already on the Coaching blog (signed "Marine Lenehan, Nutritionist at Vivify Sports & Cigala
Cycling" with her old photo on a white box): tag them "By Marine Lenehan" (her name on the blog cards) and swap the white-box
photo for her new author image (Matteo 15 Nov 2026: "the cherry juice blog is missing the author"). STAGING only.
Originals are saved in stg-coaching/posts-backup/<id>.html first.
  python3 -I tools/coaching_marine_existing_posts.py
"""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_media import req, B, ROOT
import coaching_vivify_posts as V
state = json.load(open(V.STATE)); block = V.author_block(state)
OLD = re.compile(r'<!-- wp:image [^>]*-->\s*<figure[^>]*>\s*<img[^>]*Untitled-design-30[^>]*>\s*</figure>\s*<!-- /wp:image -->', re.S)
mine = {p['id'] for p in state['posts'].values()}
posts = json.loads(req(B + '/posts?per_page=100&context=edit&_fields=id,slug,tags,content'))
for p in posts:
    raw = p['content']['raw']
    if p['id'] in mine or not re.search(r'Marine Lenehan\s*<br', raw): continue
    new, n = OLD.subn(block, raw)
    bk = ROOT + f'stg-coaching/posts-backup/{p["id"]}.html'
    if not os.path.exists(bk): open(bk, 'w').write(raw)
    tags = sorted(set(p['tags']) | {V.TAG_MARINE})
    req(B + f'/posts/{p["id"]}', data=json.dumps({'content': new, 'tags': tags}).encode(), method='POST', headers=V.HDR)
    print(p['id'], p['slug'], 'photo swapped' if n else 'no old photo', 'tagged')

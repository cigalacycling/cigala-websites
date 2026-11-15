"""Replace the childhood photo at the end of Matteo's blog posts with the new author image (Matteo 15 Nov 2026).
STAGING only. Uploads coaching/brand/matteo-cigala-author-signature.webp once (id kept in stg-coaching/author-signature.json),
then in every post whose content has the 'Matteo-Cigala-6-years-old' image block, swaps that block for the new image.
Each post's original content is saved first in stg-coaching/posts-backup/<id>.html.
  python3 -I tools/coaching_posts_author.py [--dry]
"""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_media import req, B, ROOT
HDR = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
IDF = ROOT + 'stg-coaching/author-signature.json'
ALT = 'Matteo Cigala, Founder & Head Coach of Cigala Cycling, in the white Cigala Cycling jersey, with his signature'
DRY = '--dry' in sys.argv

if os.path.exists(IDF): M = json.load(open(IDF))
else:
    r = json.loads(req(B + '/media', data=open(ROOT + 'coaching/brand/matteo-cigala-author-signature.webp', 'rb').read(), method='POST',
                       headers={'Content-Type': 'image/webp', 'Content-Disposition': 'attachment; filename="matteo-cigala-author-signature.webp"', 'User-Agent': 'Mozilla/5.0'}))
    req(B + f'/media/{r["id"]}', data=json.dumps({'alt_text': ALT}).encode(), method='POST', headers=HDR)
    M = {'id': r['id'], 'url': r['source_url']}; json.dump(M, open(IDF, 'w'))
NEW = (f'<!-- wp:image {{"id":{M["id"]},"width":"240px","sizeSlug":"full","linkDestination":"none","className":"cc-author"}} -->\n'
       f'<figure class="wp-block-image size-full is-resized cc-author"><img src="{M["url"]}" alt="{ALT}" class="wp-image-{M["id"]}" style="width:240px"/></figure>\n'
       '<!-- /wp:image -->')
BLOCK = re.compile(r'<!-- wp:image [^>]*-->\s*<figure[^>]*>\s*<img[^>]*Matteo-Cigala-6-years-old[^>]*>\s*</figure>\s*<!-- /wp:image -->', re.S)
os.makedirs(ROOT + 'stg-coaching/posts-backup', exist_ok=True)
posts = json.loads(req(B + '/posts?per_page=100&context=edit&_fields=id,slug,content'))
n = 0
for p in posts:
    raw = p['content']['raw']
    if 'Matteo-Cigala-6-years-old' not in raw: continue
    new, k = BLOCK.subn(NEW, raw)
    if not k: print('NOT MATCHED', p['slug']); continue
    n += 1; print(p['id'], p['slug'], k)
    if DRY: continue
    bk = ROOT + f'stg-coaching/posts-backup/{p["id"]}.html'
    if not os.path.exists(bk): open(bk, 'w').write(raw)
    req(B + f'/posts/{p["id"]}', data=json.dumps({'content': new}).encode(), method='POST', headers=HDR)
print(n, 'posts', '(dry run)' if DRY else 'updated')

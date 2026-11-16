"""Guides: the author image at the end of every guide = the Coaching blog's (Matteo 16 Nov: "the signature image is better
the one on the coaching website, make it consistent"). STAGING only. Uploads coaching/brand/matteo-cigala-author-signature.webp
once (stg-tours/author-signature.json) and swaps the Matteo-Cigala-5.png block in each post; the old alt text is kept.
Backups: stg-tours/backup/post-<id>-before-author.html.   python3 -I tools/tours_guides_author.py
"""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tours_img import _req, B
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
HDR = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
IDF = ROOT + 'stg-tours/author-signature.json'
ALT = 'Matteo Cigala Signature'   # the live alt, kept
if os.path.exists(IDF): M = json.load(open(IDF))
else:
    r = json.loads(_req(B + '/media', data=open(ROOT + 'coaching/brand/matteo-cigala-author-signature.webp', 'rb').read(), method='POST',
                        headers={'Content-Type': 'image/webp', 'Content-Disposition': 'attachment; filename="matteo-cigala-author-signature.webp"', 'User-Agent': 'Mozilla/5.0'}))
    _req(B + f'/media/{r["id"]}', data=json.dumps({'alt_text': ALT}).encode(), method='POST', headers=HDR)
    M = {'id': r['id'], 'url': r['source_url']}; json.dump(M, open(IDF, 'w'))
NEW = (f'<!-- wp:image {{"id":{M["id"]},"width":"240px","sizeSlug":"full","linkDestination":"none","className":"cc-author"}} -->\n'
       f'<figure class="wp-block-image size-full is-resized cc-author"><img src="{M["url"]}" alt="{ALT}" class="wp-image-{M["id"]}" style="width:240px"/></figure>\n'
       '<!-- /wp:image -->')
BLOCK = re.compile(r'<!-- wp:image [^>]*-->\s*<figure[^>]*>\s*<img[^>]*Matteo-Cigala-5\.png[^>]*>\s*</figure>\s*<!-- /wp:image -->', re.S)
posts = json.loads(_req(B + '/posts?per_page=100&context=edit&_fields=id,slug,content'))
n = 0
for p in posts:
    raw = p['content']['raw']
    new, k = BLOCK.subn(NEW, raw)
    if not k: continue
    bk = ROOT + f'stg-tours/backup/post-{p["id"]}-before-author.html'
    if not os.path.exists(bk): open(bk, 'w').write(raw)
    _req(B + f'/posts/{p["id"]}', data=json.dumps({'content': new}).encode(), method='POST', headers=HDR); n += 1
print(n, 'guides updated')

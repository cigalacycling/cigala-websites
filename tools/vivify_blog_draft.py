"""Put a new blog article into Marine's WordPress as a DRAFT and have WordPress email her to review it.

  python3 tools/vivify_blog_draft.py vivify/blog-drafts/<slug>.json [--no-email]

The JSON (one file per article, kept in vivify/blog-drafts/):
  {"title": "...", "slug": "...", "seo_title": "... | Vivify Sports", "meta_description": "... (<=155 chars)",
   "excerpt": "1-2 sentences for the Blog page card",
   "image": {"file": "vivify/blog-drafts/<slug>.jpg", "alt": "descriptive alt text", "credit": "source + licence (CC0/PD)"},
   "body": "<p>..</p><h2>..</h2><ul><li>..</li></ul>..."}   # simple HTML: p, h2, h3, ul/ol + li, strong/em/a
- Same look as the imported posts (tools/vivify_wp_posts.py): Elementor Canvas, Vivify header + byline + hero on top,
  author box + recent posts + footer below, the article itself as normal editable blocks in between.
- Status draft, author Marine, URL /post/<slug>/ once published. Featured image = the photo (WebP q90) for the Blog page card.
- Yoast title + meta set. Then POST /wp-json/vivify/v1/notify-draft (Code Snippets snippet on Marine's site) -> wp_mail to
  marine@vivifysports.com with preview + edit links. She reviews, edits and clicks Publish herself.
State: vivify/blog-drafts/state.json (slug -> post id), so re-running updates the same draft.
"""
import os, re, sys, json, html, math, subprocess, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
V = ROOT + 'vivify/'
sys.argv, ARGS = sys.argv[:1], sys.argv[1:]          # vivify_wp_posts reads sys.argv on import
sys.path.insert(0, ROOT + 'tools')
import vivify_wp_posts as P                            # header, footer, CSS, byline photo, recent posts
from PIL import Image, ImageOps
W, BV, SITE, API = P.W, P.BV, P.SITE, P.API
STATE = V + 'blog-drafts/state.json'
st = json.load(open(STATE)) if os.path.exists(STATE) else {}

def blocks(body):
    """Simple HTML -> Gutenberg blocks, so Marine can edit the text in the block editor."""
    out = []
    for m in re.finditer(r'<(p|h2|h3|ul|ol)\b[^>]*>(.*?)</\1>', body, re.S):
        tag, inner = m.group(1), m.group(2).strip()
        if tag == 'p':
            out.append(f'<!-- wp:paragraph -->\n<p>{inner}</p>\n<!-- /wp:paragraph -->')
        elif tag in ('h2', 'h3'):
            lvl = int(tag[1])
            out.append(f'<!-- wp:heading{"" if lvl == 2 else " {\"level\":3}"} -->\n<{tag} class="wp-block-heading">{inner}</{tag}>\n<!-- /wp:heading -->')
        else:
            items = re.findall(r'<li\b[^>]*>(.*?)</li>', inner, re.S)
            li = ''.join(f'<!-- wp:list-item -->\n<li>{x.strip()}</li>\n<!-- /wp:list-item -->' for x in items)
            attr = ' {"ordered":true}' if tag == 'ol' else ''
            out.append(f'<!-- wp:list{attr} -->\n<{tag} class="wp-block-list">{li}</{tag}>\n<!-- /wp:list -->')
    assert out, 'no p/h2/h3/ul/ol found in body'
    return '\n\n'.join(out)

def upload_image(path, alt, slug):
    im = ImageOps.exif_transpose(Image.open(ROOT + path if not path.startswith('/') else path)).convert('RGB')
    im.thumbnail((1920, 1920))
    tmp = os.environ.get('TMPDIR', '/tmp') + f'/{slug}.webp'
    im.save(tmp, 'WEBP', quality=90)
    r = subprocess.run(['curl', '-sS', '-m', '180', '-X', 'POST', API + '/media', '-H', f'Content-Disposition: attachment; filename="{slug}.webp"',
                        '-H', 'Content-Type: image/webp', '--data-binary', '@' + tmp], capture_output=True, text=True)
    j = json.loads(r.stdout); assert 'id' in j, j
    P.api('POST', f"/media/{j['id']}", {'alt_text': alt})
    return {'id': j['id'], 'url': j['source_url'], 'alt': alt}

def main(path, email=True):
    a = json.load(open(path))
    slug = a['slug']
    assert len(a['meta_description']) <= 160, 'meta description too long'
    hero = upload_image(a['image']['file'], a['image']['alt'], slug) if a.get('image') else None
    body = BV.fix_typos(blocks(a['body']))
    words = len(re.sub(r'<[^>]+>', ' ', body).split())
    read = f'{max(1, math.ceil(words / 220))} min read'
    top = (W.FONTS + '<style>' + W.CSS + '</style>' + P.HEADER + '<span id="main"></span>'
           + '<section style="padding-top:64px;padding-bottom:0"><div class="wrap"><article class="article">'
           + '<a href="/blog/" class="eyebrow" style="text-decoration:none">← Sports Nutrition Blog</a>'
           + f'<h1>{html.escape(a["title"])}</h1>'
           + f'<div class="byline"><img src="{P.ME["url"]}" alt="Marine Lenehan" width="44" height="44"><span><b>Marine Lenehan</b> · MSc Sports Nutritionist<br>{html.escape(read)}</span></div>'
           + (f'<figure style="margin-top:0"><img src="{hero["url"]}" alt="{html.escape(hero["alt"])}" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:12px" fetchpriority="high"></figure>' if hero else '')
           + '<div class="post-body">')
    bottom = ('</div><div class="author panel"><img src="' + P.ME['url'] + '" alt="Marine Lenehan" width="84" height="84"><div>'
              '<span class="eyebrow">Written by</span><div class="h3">Marine Lenehan</div>'
              '<p class="muted" style="margin:8px 0 14px">MSc Sports Nutritionist | WorldTour Professional Cyclist. Founder of Vivify Sports, Wicklow, Ireland.</p>'
              '<a class="btn btn-primary" href="' + BV.DISCOVERY + '">Book a free discovery call</a></div></div></article>'
              f'<div style="margin-top:72px;padding-bottom:88px"><div class="center"><span class="eyebrow">Keep reading</span><h2>Recent Posts</h2><span class="bar"></span></div>'
              f'<div class="bgrid" style="margin-top:28px">{P.recent(slug)}</div></div></div></section>' + P.FOOTER)
    content = '\n\n'.join([P.hblock(top), body, P.hblock(bottom)])
    post = {'title': a['title'], 'slug': slug, 'status': 'draft', 'author': P.MARINE, 'template': 'elementor_canvas',
            'content': content, 'excerpt': a['excerpt']}
    if hero: post['featured_media'] = hero['id']
    pid = st.get(slug)
    j = P.api('POST', '/posts' + (f'/{pid}' if pid else ''), post)
    assert 'id' in j, j
    assert j['status'] == 'draft' or pid, j['status']
    st[slug] = j['id']; json.dump(st, open(STATE, 'w'), indent=1)
    P.curl(['-X', 'POST', SITE + '/wp-json/yoast/v1/bulk_editor/update_search', '-H', 'Content-Type: application/json', '--data-binary', '@-'],
           json.dumps({'items': [{'id': j['id'], 'seo_title': a['seo_title']}, {'id': j['id'], 'meta_description': a['meta_description']}]}))
    print('draft', j['id'], j['status'], SITE + f'/?p={j["id"]}&preview=true')
    if email:
        note = f"Photo: {a['image'].get('credit', '')}" if a.get('image') else ''
        r = P.curl(['-X', 'POST', SITE + '/wp-json/vivify/v1/notify-draft', '-H', 'Content-Type: application/json', '--data-binary', '@-'],
                   json.dumps({'id': j['id'], 'note': note}))
        print('email', r)

if __name__ == '__main__':
    main(ARGS[0], email='--no-email' not in ARGS)

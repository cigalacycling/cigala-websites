"""Import Marine's 33 Wix blog posts into her WordPress draft, word for word.

  python3 -I tools/vivify_wp_posts.py            # all posts (downloads to vivify/raw/posts/ first time)
  python3 -I tools/vivify_wp_posts.py <slug> ... # some posts

- Same URL: /post/<wix slug>/ (permalinks /post/%postname%/), original publish date, author = Marine (user 1).
- Title = the Wix H1 exactly (no case changes). Yoast title + meta = the Wix ones (vivify/baseline-2026-11-16.json).
- Body: Wix rich content -> Gutenberg blocks (parser from tools/coaching_vivify_posts.py), images as WebP q90 from the
  largest Wix original with their Wix alt text; the featured image is the post's hero.
- Look: template Elementor Canvas, with the Vivify CSS + header + byline at the top and author box, recent posts and
  footer at the bottom as Custom HTML blocks; the article blocks in between stay editable in the block editor.
State in vivify/wp-posts.json.
"""
import os, re, io, sys, json, html, subprocess, importlib.util, math
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
V = ROOT + 'vivify/'
sys.path.insert(0, ROOT + 'tools')
from coaching_vivify_posts import Conv, gutenberg, wix_full          # parser only; its upload code targets Coaching staging
import build_vivify_wp as W                                          # CSS, fonts, link/image rewriting, Marine's media
spec = importlib.util.spec_from_file_location('bv', ROOT + 'tools/build_vivify.py'); BV = importlib.util.module_from_spec(spec); spec.loader.exec_module(BV)

SITE = W.SITE; API = SITE + '/wp-json/wp/v2'; LIVE = W.LIVE
STATE = V + 'wp-posts.json'
st = json.load(open(STATE)) if os.path.exists(STATE) else {'media': {}, 'posts': {}}
RAW = V + 'raw/posts/'; os.makedirs(RAW, exist_ok=True)
MARINE = 1

def curl(args, data=None):
    r = subprocess.run(['curl', '-sS', '-m', '180'] + args, input=data, capture_output=True, text=data is None or isinstance(data, str))
    return r.stdout

def api(method, path, body):
    out = curl(['-X', method, API + path, '-H', 'Content-Type: application/json', '--data-binary', '@-'], json.dumps(body))
    return json.loads(out)

def media_name(url):
    mid = url.split('/media/')[1].split('/')[0]
    return re.sub(r'[^a-zA-Z0-9]+', '-', mid.split('.')[0]) + '.webp', mid

def upload(url, alt):
    """reuse an image already in Marine's media library, else WebP q90 from the largest Wix original"""
    name, mid = media_name(url)
    if name in W.MEDIA: return W.MEDIA[name]
    if url in st['media']: return st['media'][url]
    raw = subprocess.run(['curl', '-sS', '-m', '180', url], capture_output=True).stdout
    im = Image.open(io.BytesIO(raw)); im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
    im.thumbnail((2560, 2560), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'WEBP', quality=90, method=6)
    r = subprocess.run(['curl', '-sS', '-m', '180', '-X', 'POST', API + '/media', '-H', f'Content-Disposition: attachment; filename="{name}"',
                        '-H', 'Content-Type: image/webp', '--data-binary', '@-'], input=buf.getvalue(), capture_output=True)
    j = json.loads(r.stdout)
    api('POST', f'/media/{j["id"]}', {'alt_text': alt, 'title': alt or name})
    st['media'][url] = {'id': j['id'], 'url': j['source_url'], 'alt': alt}
    json.dump(st, open(STATE, 'w'), indent=1)
    return st['media'][url]

def fetch(slug):
    p = RAW + slug + '.html'
    if not os.path.exists(p):
        open(p, 'w').write(curl([f'{LIVE}/post/{slug}']))
    return open(p).read()

def parse(s):
    ld = next(json.loads(x) for x in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', s, re.S)
              if '"BlogPosting"' in x or '"Article"' in x)
    h1 = html.unescape(re.sub(r'<[^>]+>', '', re.search(r'<h1[^>]*data-hook="post-title"[^>]*>(.*?)</h1>', s, re.S).group(1))).strip()
    a = s.index('data-hook="rcv-block-first"'); b = s.index('data-hook="rcv-block-last"'); a = s.rfind('<div', 0, a)
    c = Conv(); c.feed(s[a:b])
    hero = None
    img = ld.get('image')
    if isinstance(img, dict) and img.get('url'): hero = wix_full(img['url'])
    og = re.search(r'<meta property="og:image" content="([^"]+)"', s)
    if not hero and og and 'wixstatic' in og.group(1): hero = wix_full(og.group(1))
    return {'h1': h1, 'date': (ld.get('datePublished') or '')[:19], 'blocks': c.blocks, 'hero': hero}

# shared pieces from the built blog page (header with "Blog" as the current page, footer)
_blog = open(V + 'site/blog.html').read()
HEADER = W.fix(re.search(r'<a class="skip".*?</header>', _blog, re.S).group(0))
FOOTER = W.fix(re.search(r'<footer class="site">.*?</footer>', _blog, re.S).group(0))
ME = W.MEDIA[next(n for n in W.MEDIA if n.startswith('0e1488-5ffa2e2730204ef0bae918a9e4ae'))]
CARDS = {(p['url'] or '').rsplit('/', 1)[-1]: p for p in BV.blog_posts()}

def hblock(h):
    return '<!-- wp:html -->\n' + h + '\n<!-- /wp:html -->'

def fmt_date(d):
    import datetime
    try: return datetime.datetime.fromisoformat(d).strftime('%-d %b %Y')
    except Exception: return ''

def recent(slug):
    out = ''
    for s, p in CARDS.items():
        if s == slug or not p['img'] or s not in st['posts'] and s not in WANT: continue
        im = W.MEDIA.get(p['img'] + '.webp')
        if not im: continue
        out += (f'<a class="bcard panel" href="/post/{s}/"><div class="ph"><img src="{im["url"]}" alt="{html.escape(p["title"])}" loading="lazy" decoding="async"></div>'
                f'<div class="tx"><h3 class="h3" style="font-size:19px;margin-bottom:10px">{html.escape(p["title"])}</h3><div class="meta"><span>{html.escape(p["read"])}</span></div></div></a>')
        if out.count('bcard') == 3: break
    return out

def build(slug):
    d = parse(fetch(slug))
    base = BV.BASE.get(f'{LIVE}/post/{slug}')
    if not base:   # not in the Wix sitemap/crawl (iron-deficiency post): read title and meta from its own page
        raw = fetch(slug)
        base = {'title': html.unescape(re.search(r'<title>(.*?)</title>', raw, re.S).group(1)).strip(),
                'meta_description': html.unescape((re.search(r'<meta name="description" content="([^"]*)"', raw) or re.search(r'<meta property="og:description" content="([^"]*)"', raw)).group(1))}
    d['h1'] = BV.fix_typos(d['h1'])
    d['blocks'] = [(b[0], b[1], b[2] or d['h1']) if b[0] == 'img' else b for b in d['blocks']]
    imgs = {}
    for blk in d['blocks']:
        if blk[0] == 'img': imgs[blk[1]] = upload(blk[1], blk[2])
    hero = upload(d['hero'], next((b[2] for b in d['blocks'] if b[0] == 'img' and b[1] == d['hero'] and b[2]), d['h1'])) if d['hero'] else None
    # the hero photo is shown at the top, so drop it from the body if Wix repeats it as the first image
    blocks = list(d['blocks'])
    if hero and blocks and blocks[0][0] == 'img' and blocks[0][1] == d['hero']: blocks = blocks[1:]
    show_hero = hero and not any(b[0] == 'img' and b[1] == d['hero'] for b in blocks)   # Wix shows the cover only in cards
    body = gutenberg(blocks, imgs)
    words = len(re.sub(r'<[^>]+>', ' ', body).split())
    read = (CARDS.get(slug) or {}).get('read') or f'{max(1, math.ceil(words / 220))} min read'
    top = (W.FONTS + '<style>' + W.CSS + '</style>' + HEADER + '<span id="main"></span>'
           + '<section style="padding-top:64px;padding-bottom:0"><div class="wrap"><article class="article">'
           + '<a href="/blog/" class="eyebrow" style="text-decoration:none">← Sports Nutrition Blog</a>'
           + f'<h1>{html.escape(d["h1"])}</h1>'
           + f'<div class="byline"><img src="{ME["url"]}" alt="Marine Lenehan" width="44" height="44"><span><b>Marine Lenehan</b> · MSc Sports Nutritionist<br>{fmt_date(d["date"])} · {html.escape(read)}</span></div>'
           + (f'<figure style="margin-top:0"><img src="{hero["url"]}" alt="{html.escape(hero.get("alt") or d["h1"])}" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:12px" fetchpriority="high"></figure>' if show_hero else '')
           + '<div class="post-body">')
    bottom = ('</div><div class="author panel"><img src="' + ME['url'] + '" alt="Marine Lenehan" width="84" height="84"><div>'
              '<span class="eyebrow">Written by</span><div class="h3">Marine Lenehan</div>'
              '<p class="muted" style="margin:8px 0 14px">MSc Sports Nutritionist | WorldTour Professional Cyclist. Founder of Vivify Sports, Wicklow, Ireland.</p>'
              '<a class="btn btn-primary" href="/contact/">Book a free discovery call</a></div></div></article>'
              f'<div style="margin-top:72px;padding-bottom:88px"><div class="center"><span class="eyebrow">Keep reading</span><h2>Recent Posts</h2><span class="bar"></span></div>'
              f'<div class="bgrid" style="margin-top:28px">{recent(slug)}</div></div></div></section>' + FOOTER)
    content = '\n\n'.join([hblock(top), body, hblock(bottom)])
    content = BV.fix_typos(content)
    post = {'title': d['h1'], 'slug': slug, 'status': 'publish', 'date': d['date'] or None, 'author': MARINE,
            'template': 'elementor_canvas', 'content': content}
    if hero: post['featured_media'] = hero['id']
    pid = st['posts'].get(slug, {}).get('id')
    j = api('POST', '/posts' + (f'/{pid}' if pid else ''), post)
    if 'id' not in j: print('FAIL', slug, j.get('code'), j.get('message')); return
    st['posts'][slug] = {'id': j['id'], 'seo_title': BV.fix_typos(base['title']), 'desc': BV.fix_typos(base.get('meta_description') or '')}
    json.dump(st, open(STATE, 'w'), indent=1)
    print(j['id'], j['link'], len(imgs), 'images')

def yoast():
    items = []
    for slug, p in st['posts'].items():
        items += [{'id': p['id'], 'seo_title': p['seo_title']}, {'id': p['id'], 'meta_description': p['desc']}]
    for i in range(0, len(items), 18):
        out = curl(['-X', 'POST', SITE + '/wp-json/yoast/v1/bulk_editor/update_search', '-H', 'Content-Type: application/json', '--data-binary', '@-'],
                   json.dumps({'items': items[i:i + 18]}))
        res = json.loads(out).get('results', [])
        bad = [x for x in res if not x['success']]
        if bad or not res: print('YOAST FAIL', out[:200])
    print('yoast', len(items) // 2, 'posts')

ALL = [l.strip().rsplit('/', 1)[-1] for l in open(V + 'raw/sitemap-urls.txt') if '/post/' in l] + ['iron-deficiency-anemia-and-performance']
WANT = sys.argv[1:] or ALL
if __name__ == '__main__':
    for s in WANT:
        try: build(s)
        except Exception as ex: print('FAIL', s, type(ex).__name__, ex)
    yoast()
    subprocess.run(['curl', '-sS', '-m', '60', '-X', 'DELETE', SITE + '/wp-json/elementor/v1/cache'], capture_output=True)

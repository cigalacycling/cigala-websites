"""Publish Marine Lenehan's Vivify Sports articles as Coaching blog posts (STAGING only).

Matteo 15 Nov 2026: "draft and publish, keeping the same consistency of all the other blogs of Marine's blog, taking maybe
5 new blogs from her website ... and then you can add them" (to the Nutrition page).

For each article (downloaded from vivifysports.com/post/<slug> into a folder given as argv[1]):
- the text is converted to Gutenberg blocks (paragraphs, headings, lists, tables, images), word for word;
- images: largest original from Wix -> WebP q90, uploaded to staging with the article's own alt text;
- the post is credited to Marine: tag "By Marine Lenehan" (the post template shows her name instead of Matteo's for that
  tag, see build_coaching_wp) and a closing signature block "Marine Lenehan, MSc Sports Nutritionist · Vivify Sports";
- a line at the end says where it was first published, with a link (Matteo's site and Marine's site are partners);
- category Blog, original publication date, featured image = the article's hero image.
State (post ids, media ids) is kept in stg-coaching/vivify-posts.json so re-running updates instead of duplicating.

  python3 -I tools/coaching_vivify_posts.py <folder with the downloaded .html files>
"""
import os, re, sys, json, html, io, urllib.request, ssl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_media import req, B, ROOT
from html.parser import HTMLParser
from PIL import Image

HDR = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
STATE = ROOT + 'stg-coaching/vivify-posts.json'
TAG_MARINE, CAT_BLOG = 9, 1
VIV = 'https://www.vivifysports.com'
ctx = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
POSTS = {   # vivify slug -> our slug
    'carbohydrate-fueling-endurance-sports': 'carbs-per-hour-endurance-fueling',
    'ironman-70-3-nutrition-plan': 'ironman-70-3-nutrition-plan',
    'why-am-i-so-tired-after-exercise-understanding-post-exercise-fatigue-in-endurance-athletes': 'fatigue-after-exercise-endurance-athletes',
    'daily-fat-intake-guide': 'daily-fat-intake-guide',
    'cycling-nutrition-what-to-eat-and-drink-during-bike-rides-of-any-length': 'cycling-nutrition-what-to-eat-and-drink-on-the-bike',
}

def wix_full(u):
    """largest original of a Wix image URL"""
    return re.sub(r'(/media/[^/]+?\.(?:jpe?g|png|webp))/v1/.*$', r'\1', u, flags=re.I)

def upload_image(url, name, alt, state):
    if url in state['media']: return state['media'][url]
    raw = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), context=ctx, timeout=90).read()
    im = Image.open(io.BytesIO(raw)); im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
    if max(im.size) > 2400: im.thumbnail((2400, 2400), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'WEBP', quality=90, method=6)
    r = json.loads(req(B + '/media', data=buf.getvalue(), method='POST', headers={'Content-Type': 'image/webp',
                       'Content-Disposition': f'attachment; filename="{name}.webp"', 'User-Agent': 'Mozilla/5.0'}))
    req(B + f'/media/{r["id"]}', data=json.dumps({'alt_text': alt}).encode(), method='POST', headers=HDR)
    state['media'][url] = {'id': r['id'], 'url': r['source_url'], 'w': im.size[0], 'h': im.size[1]}
    json.dump(state, open(STATE, 'w'), indent=1)
    return state['media'][url]

class Conv(HTMLParser):
    """Wix rich content -> list of blocks: ('p'|'h2'|'h3'|'h4', html) | ('ul'|'ol', [html]) | ('img', src, alt) | ('table', [[cell]])"""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self.buf, self.mode, self.items, self.rows, self.cell = [], None, None, None, None, None
        self.inline = []   # open inline tags
        self.skip = 0
    def out(self, s):
        if self.cell is not None: self.cell.append(s)
        elif self.buf is not None: self.buf.append(s)
    def handle_starttag(self, t, a):
        a = dict(a)
        if t in ('style', 'script', 'svg'): self.skip += 1; return
        if self.skip: return
        if t in ('p', 'h2', 'h3', 'h4', 'h5', 'h6') and self.items is None and self.rows is None:
            self.mode = {'h5': 'h4', 'h6': 'h4'}.get(t, t); self.buf = []
        elif t in ('ul', 'ol') and self.rows is None:
            self.items = []; self.mode = t
        elif t == 'li' and self.items is not None:
            self.buf = []
        elif t == 'table':
            self.rows = []
        elif t == 'tr' and self.rows is not None:
            self.rows.append([])
        elif t == 'td' and self.rows is not None:
            self.cell = []
        elif t == 'img':
            src = a.get('src', '')
            if 'wixstatic.com/media/' in src and self.rows is None:
                self.blocks.append(('img', wix_full(src), a.get('alt') or ''))
        elif t in ('strong', 'b'):
            self.out('<strong>')
        elif t in ('em', 'i'):
            self.out('<em>')
        elif t == 'a' and a.get('href', '').startswith('http'):
            self.out(f'<a href="{html.escape(a["href"])}">'); self.inline.append('a')
        elif t == 'br':
            self.out('<br>')
    def handle_endtag(self, t):
        if t in ('style', 'script', 'svg'): self.skip -= 1; return
        if self.skip: return
        if t in ('strong', 'b'): self.out('</strong>')
        elif t in ('em', 'i'): self.out('</em>')
        elif t == 'a' and self.inline: self.inline.pop(); self.out('</a>')
        elif t in ('p', 'h2', 'h3', 'h4', 'h5', 'h6') and self.buf is not None and self.items is None and self.rows is None:
            txt = clean(''.join(self.buf))
            if txt: self.blocks.append((self.mode, txt))
            self.buf = None
        elif t == 'li' and self.items is not None and self.buf is not None:
            txt = clean(''.join(self.buf))
            if txt: self.items.append(txt)
            self.buf = None
        elif t in ('ul', 'ol') and self.items is not None:
            if self.items: self.blocks.append((t, self.items))
            self.items = None
        elif t == 'td' and self.cell is not None:
            self.rows[-1].append(clean(''.join(self.cell))); self.cell = None
        elif t == 'table' and self.rows is not None:
            rows = [r for r in self.rows if any(r)]
            if rows: self.blocks.append(('table', rows))
            self.rows = None
    def handle_data(self, d):
        if self.skip: return
        self.out(html.escape(d, quote=False))

def clean(s):
    s = re.sub(r'<br>\s*$', '', s.strip())
    s = re.sub(r'(<strong>)\s*(</strong>)|(<em>)\s*(</em>)', '', s)
    s = s.replace('</strong><strong>', '').replace(' ', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return '' if re.fullmatch(r'(<br>|\s)*', s) else s

def gutenberg(blocks, imgs):
    out = []
    for b in blocks:
        k = b[0]
        if k == 'p' and re.fullmatch(r'<strong>[^<]{3,80}</strong>', b[1]):   # a bold-only line is a sub-heading on Wix
            out.append(f'<!-- wp:heading {{"level":3}} -->\n<h3 class="wp-block-heading">{re.sub(r"</?strong>", "", b[1]).strip()}</h3>\n<!-- /wp:heading -->')
        elif k == 'p': out.append(f'<!-- wp:paragraph -->\n<p>{b[1]}</p>\n<!-- /wp:paragraph -->')
        elif k in ('h2', 'h3', 'h4'):
            lv = int(k[1]); attr = '' if lv == 2 else f' {{"level":{lv}}}'
            out.append(f'<!-- wp:heading{attr} -->\n<{k} class="wp-block-heading">{b[1]}</{k}>\n<!-- /wp:heading -->')
        elif k in ('ul', 'ol'):
            items = ''.join(f'<!-- wp:list-item -->\n<li>{x}</li>\n<!-- /wp:list-item -->' for x in b[1])
            attr = ' {"ordered":true}' if k == 'ol' else ''
            out.append(f'<!-- wp:list{attr} -->\n<{k} class="wp-block-list">{items}</{k}>\n<!-- /wp:list -->')
        elif k == 'table':
            head, *body = b[1]
            th = ''.join(f'<th>{c}</th>' for c in head); tb = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in body)
            out.append(f'<!-- wp:table -->\n<figure class="wp-block-table"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></figure>\n<!-- /wp:table -->')
        elif k == 'img':
            m = imgs[b[1]]
            out.append(f'<!-- wp:image {{"id":{m["id"]},"sizeSlug":"full","linkDestination":"none"}} -->\n'
                       f'<figure class="wp-block-image size-full"><img src="{m["url"]}" alt="{html.escape(b[2])}" class="wp-image-{m["id"]}"/></figure>\n<!-- /wp:image -->')
    return '\n\n'.join(out)

def signature(vslug):
    return ('<!-- wp:paragraph {"className":"cc-marine-sig"} -->\n<p class="cc-marine-sig"><strong>Marine Lenehan</strong><br>MSc Sports Nutritionist · founder of '
            f'<a href="{VIV}/">Vivify Sports</a> · WorldTour professional cyclist</p>\n<!-- /wp:paragraph -->\n\n'
            '<!-- wp:paragraph {"className":"cc-marine-src"} -->\n<p class="cc-marine-src"><em>This article was first published on '
            f'<a href="{VIV}/post/{vslug}">vivifysports.com</a>. Want nutrition coaching with Marine alongside your cycling coaching? '
            '<a href="/nutrition/">See how it works</a>.</em></p>\n<!-- /wp:paragraph -->')

def parse(path):
    s = open(path).read()
    ld = next(json.loads(x) for x in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', s, re.S)
              if '"BlogPosting"' in x or '"Article"' in x)
    title = html.unescape(re.search(r'<h1[^>]*data-hook="post-title"[^>]*>(.*?)</h1>', s, re.S).group(1)).strip()
    desc = html.unescape((re.search(r'<meta name="description" content="([^"]*)"', s) or re.search(r'<meta property="og:description" content="([^"]*)"', s)).group(1))
    seo_t = html.unescape(re.search(r'<title>(.*?)</title>', s, re.S).group(1)).strip()
    a = s.index('data-hook="rcv-block-first"'); b = s.index('data-hook="rcv-block-last"')
    a = s.rfind('<div', 0, a)
    c = Conv(); c.feed(s[a:b]); blocks = c.blocks
    hero = None
    img = ld.get('image')
    if isinstance(img, dict): hero = (wix_full(img['url']), title)
    og = re.search(r'<meta property="og:image" content="([^"]+)"', s)
    if not hero and og: hero = (wix_full(og.group(1)), title)
    hero_alt = next((x[2] for x in blocks if x[0] == 'img' and x[1] == (hero or ('',))[0]), '') or title
    if title.isupper(): title = title.capitalize().replace("day's", "Day's").replace(' fat ', ' Fat ')
    if len(desc) > 160: desc = desc[:desc.rfind(' ', 0, 155)] + '…'
    return {'title': title, 'date': ld.get('datePublished', '')[:19], 'desc': desc, 'seo_title': seo_t, 'blocks': blocks, 'hero': hero, 'hero_alt': hero_alt}

# cycling-nutrition-what-to-eat-and-drink-on-the-bike: its Wix hero is the same photo as the carbs article, so its featured
# image was set to the road cyclist photo from vivifysports.com's homepage (media id in stg-coaching/vivify-posts.json).
# the fatigue article has no hero image on Wix: an existing staging photo of a rider resting before a ride
FALLBACK = {'fatigue-after-exercise-endurance-athletes': {'id': 6344, 'url': 'https://staging.coaching.cigalacycling.com/wp-content/uploads/2026/10/emma-harrisova-SqPuXo9yuoM-unsplash-scaled.jpg'}}
def main(folder):
    state = json.load(open(STATE)) if os.path.exists(STATE) else {'media': {}, 'posts': {}}
    for vslug, slug in POSTS.items():
        d = parse(os.path.join(folder, vslug + '.html'))
        imgs = {}
        for n, x in enumerate([b for b in d['blocks'] if b[0] == 'img']):
            imgs[x[1]] = upload_image(x[1], f'{slug}-{n + 1}', x[2] or d['title'], state)
        feat = upload_image(d['hero'][0], f'{slug}-featured', d['hero_alt'], state) if d['hero'] else FALLBACK.get(slug)
        blocks = [b for b in d['blocks'] if not (b[0] == 'img' and d['hero'] and b[1] == d['hero'][0] and b is d['blocks'][0])]
        content = gutenberg(blocks, imgs) + '\n\n' + signature(vslug)
        first_p = next((re.sub(r'<[^>]+>', '', b[1]) for b in d['blocks'] if b[0] == 'p'), d['desc'])
        body = {'title': d['title'], 'slug': slug, 'status': 'publish', 'content': content, 'excerpt': d['desc'] or first_p[:300],
                'categories': [CAT_BLOG], 'tags': [TAG_MARINE], 'date': d['date'] or None}
        if feat: body['featured_media'] = feat['id']
        pid = state['posts'].get(slug, {}).get('id')
        r = json.loads(req(B + (f'/posts/{pid}' if pid else '/posts'), data=json.dumps(body).encode(), method='POST', headers=HDR))
        state['posts'][slug] = {'id': r['id'], 'link': r['link'], 'title': d['title'], 'seo_title': d['seo_title'], 'desc': d['desc'],
                                'featured': feat and feat['url'], 'featured_alt': d['hero_alt'], 'source': f'{VIV}/post/{vslug}',
                                'blocks': {k: sum(1 for b in d['blocks'] if b[0] == k) for k in ('p', 'h2', 'h3', 'ul', 'ol', 'img', 'table')}}
        json.dump(state, open(STATE, 'w'), indent=1)
        print(r['id'], slug, state['posts'][slug]['blocks'])

if __name__ == '__main__':
    main(sys.argv[1])

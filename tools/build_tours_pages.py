"""Tours content pages in the new design: About (more pages are added here one by one).

Source of truth for the words = the page's own Elementor data on Tours staging (a copy of live), so the
H1/H2 wording and tags, body copy, links and image alt text stay exactly as they are live (CLAUDE.md).
The layout follows the page designs in tourspages/ (tools/build_tours.py); their CSS is already in the kit (.cl).

Usage: python3 -I tools/build_tours_pages.py about
Writes the preview tourspages/page-<slug>.html and stg-tours/out/list-<slug>.json; push with
python3 -I tools/push_tours_list.py <slug>.
Images: WebP q90 from the largest originals on staging (tools/tours_img.py), alt text from the media library.
"""
import os, re, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from push_tours_wp import req, B
from tours_img import webp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
L = 'https://tours.cigalacycling.com'
EXT = 'target="_blank" rel="noopener"'
E = lambda x: html.escape(x, quote=True)

# ---------- Elementor data -> a flat list of content items, in page order ----------
def elementor(pid, refresh=True):
    f = ROOT + f'stg-tours/backup/page-{pid}.json'
    if refresh or not os.path.exists(f):
        code, r = req(f'{B}/wp/v2/pages/{pid}?context=edit&_fields=id,link,meta,featured_media')
        assert code == 200, (pid, code)
        if not os.path.exists(f): open(f, 'w').write(r.decode())   # keep the first copy as the backup
        p = json.loads(r)
    else:
        p = json.load(open(f))
    return json.loads(p['meta']['_elementor_data'] or '[]')

def clean(h):
    h = re.sub(r'<span style="[^"]*">(.*?)</span>', r'\1', h, flags=re.S)
    h = re.sub(r' (data-[a-z-]+|style|class)="[^"]*"', '', h)
    h = re.sub(r'<p>(&nbsp;|\s)*</p>', '', h)
    h = h.replace('https://staging.tours.cigalacycling.com', L)
    return h.strip()

def items(els, out=None, depth=0):
    """[(kind, value, settings)]: h1..h6, text (html), img (media id or url), bg (container background), btn (text, url)."""
    out = [] if out is None else out
    for e in els:
        s = e.get('settings', {}); w = e.get('widgetType')
        if w == 'heading': out.append((s.get('header_size', 'h2'), s.get('title', '').strip(), s))
        elif w == 'text-editor': out.append(('text', clean(s.get('editor', '')), s))
        elif w == 'image': out.append(('img', s.get('image', {}).get('id') or s.get('image', {}).get('url'), s))
        elif w == 'button': out.append(('btn', (s.get('text', '').strip(), s.get('link', {}).get('url', '')), s))
        elif e.get('elType') in ('container', 'section', 'column'):
            bg = s.get('background_image', {})
            if bg.get('url'): out.append(('bg', bg.get('id') or bg['url'], s))
            out.append(('open', depth, s))
            items(e.get('elements', []), out, depth + 1)
            out.append(('close', depth, s))
        elif w: out.append((w, None, s))
    return out

def text_of(h): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h))).strip()
def link(u): return u.replace('https://staging.tours.cigalacycling.com', L)

def head_block(eyebrow, h, tag='h2', lede=''):
    l = f'<p class="lede">{lede}</p>' if lede else ''
    return f'<div class="head"><div><div class="eyebrow">{eyebrow}</div><{tag}>{E(h)}</{tag}><div class="bar"></div>{l}</div></div>'

def img_tag(src, maxw, cls='', alt=None, lazy=True):
    im = webp(src, maxw, alt)
    c = f' class="{cls}"' if cls else ''
    return f'<img{c} src="{im["url"]}" alt="{E(im["alt"])}"{" loading=\"lazy\"" if lazy else ""}>'

# shared parts from the trip-list design (same as the tour pages): partners strip and the "custom tour" band
lists = open(ROOT + 'stg-tours/out/list-trips.json').read()
PARTNERS = re.search(r'<section>\s*<div class="in partners">.*?</section>', json.loads(lists)['main'], re.S).group(0)
# the live pages have these labels as H2s: keep them as H2s (styled like the small labels)
PARTNERS_H2 = re.sub(r'<div class="lab">([^<]*)</div>', r'<h2 class="lab">\1</h2>', PARTNERS)

# ===================== About (271) =====================
def about():
    it = items(elementor(271))
    h1 = next(v for k, v, s in it if k == 'h1')
    heads = [i for i, (k, v, s) in enumerate(it) if k == 'h2']
    def h2_index(word): return next(i for i in heads if word in it[i][1].upper())
    why_i, team_i, ready_i, op_i = h2_index('WHY RIDERS'), h2_index('OUR TEAM'), h2_index('READY'), h2_index('TOUR OPERATOR')
    story = ''.join(v for k, v, s in it[:why_i] if k == 'text')
    why = []
    for k, v, s in it[why_i:team_i]:
        if k != 'text': continue
        m = re.match(r'<p><strong>✔\s*(.*?)</strong>\s*(?:<br\s*/?>)?\s*(.*)</p>$', v, re.S)
        assert m, v
        why.append((m.group(1).strip(), m.group(2).strip()))
    whyh = ''.join(f'<div class="panel"><span class="tick" aria-hidden="true"></span><div><h3>{h}</h3><p>{p}</p></div></div>' for h, p in why)
    team = []   # each member: a container with a background photo, then two texts: name, role
    for k, v, s in it[team_i:ready_i]:
        if k == 'bg': team.append([v])
        elif k == 'text' and team and len(team[-1]) < 3: team[-1].append(text_of(v))
    assert team and all(len(m) == 3 for m in team), team
    def disp(n):   # live names are typed in capitals; the card shows them in capitals too (CSS), keep the words
        return n.replace("'", '’').replace('"', '“', 1).replace('"', '”', 1)
    th = ''.join(f'<div class="panel member">{img_tag(src, 600)}<div class="tx"><h3>{E(disp(n))}</h3><p>{E(r)}</p></div></div>' for src, n, r in team)
    ready_h = it[ready_i][1]
    ready_p = next(v for k, v, s in it[ready_i:op_i] if k == 'text')
    btn_t, btn_u = next(v for k, v, s in it[ready_i:op_i] if k == 'btn')
    hero_bg = next(v for k, v, s in it if k == 'bg')
    band_bg = [v for k, v, s in it[:why_i] if k == 'bg'][-1]   # the photo behind "Why riders choose us" live
    matteo = next(src for src, n, r in team if n.upper().startswith('MATTEO'))
    main = f'''<div class="hero plain-hero">
  <div class="in">
    <div class="crumbs"><a href="{L}/" {EXT}>Home</a> / About</div>
    <div class="eyebrow">About Cigala Cycling Tours</div>
    <h1>{E(h1)}</h1>
    <div class="bar"></div>
  </div>
</div>
<section style="padding-top:40px">
  <div class="in story">
    <div class="panel prose" style="padding:clamp(22px,4vw,40px)">{story}</div>
    <div class="photo">{img_tag(matteo, 1100)}</div>
  </div>
</section>
<section>
  <div class="in">
    {head_block('The difference', it[why_i][1])}
    <div class="why6">{whyh}</div>
  </div>
</section>
<section>
  <div class="in">
    {head_block('Who rides with you', it[team_i][1])}
    <div class="team">{th}</div>
  </div>
</section>
<section>
  <div class="in">
    <div class="band">
      {img_tag(band_bg, 1600)}
      <div class="tx">
        <div class="eyebrow">Join us</div>
        <h2>{E(ready_h)}</h2>
        <div class="bar"></div>
        <div class="lede">{ready_p}</div>
        <div class="ctas"><a class="btn btn-go" href="{link(btn_u)}">{E(btn_t.capitalize())} →</a></div>
      </div>
    </div>
  </div>
</section>
{PARTNERS_H2}'''
    return {'id': 271, 'slug': 'about', 'main': main, 'css': PAGE_CSS, 'crumb': 'About'}

# small additions on top of the design CSS, scoped to .cl by the kit build
PAGE_CSS = '''
html .cl .band .lede p { margin: 0; }
html .cl .member h3 { text-transform: uppercase; }
html .cl h2.lab { font-family: var(--body); font-size: 11px; line-height: 1.4; letter-spacing: .09em; font-weight: 600; color: var(--text-3); text-transform: uppercase; margin: 0 0 12px; }
'''

PAGES = {'about': about}

if __name__ == '__main__':
    lists_prev = open(ROOT + 'tourspages/trips.html').read()   # header/footer/CSS exactly as the tour pages
    for name in sys.argv[1:] or PAGES:
        d = PAGES[name]()
        a, b = lists_prev.index('<div class="cl cl-page">'), lists_prev.index('<div class="cc"><footer>')
        prev = lists_prev[:a] + '<div class="cl cl-page">\n' + d['main'] + '\n</div>\n' + lists_prev[b:]
        prev = prev.replace('</style>', '</style>\n<style>\n' + d['css'] + '\n</style>', 1)
        open(ROOT + f'tourspages/page-{name}.html', 'w').write(prev)   # page-*: the design files keep their names
        json.dump(d, open(ROOT + f'stg-tours/out/list-{name}.json', 'w'), ensure_ascii=False)
        print(name, len(d['main']), 'chars | h1', d['main'].count('<h1'), '| h2', d['main'].count('<h2'), '| img', d['main'].count('<img'))

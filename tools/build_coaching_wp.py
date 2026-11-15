"""Build the Elementor payloads for Coaching STAGING from the approved preview pages (coachingpages/*.html).

Writes stg-coaching/out/:
  lib-6.json      kit: the brand CSS, scoped to .cc, so pages not rebuilt yet keep their old look
  lib-170.json    header: new nav (Cycling / Triathlon / Services dropdowns)
  lib-228.json    footer: new footer + the shared cookie banner (shared/consent/), which also loads the OpenWidget chat.
                  Replaces the old "Got it!" cookie bar and the old chat widget.
  page-2924.json  homepage
  page-3338.json  Individual Packages (keeps the live Elementor contact form and the Shapo testimonials widget)
  snippet-head.json  the shared consent head snippet (Elementor custom code)

Run the preview builders and tools/coaching_media.py first. Push with tools/push_coaching_wp.py.
"""
import os, re, sys, json, copy, random, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
OUT = ROOT + 'stg-coaching/out/'
os.makedirs(OUT, exist_ok=True)
C = 'https://coaching.cigalacycling.com'
M = json.load(open(ROOT + 'stg-coaching/media-webp.json'))
PAGES = {'home': 2924, 'individual-packages': 3338, 'tri-individual-packages': 3795, 'group-club-packages': 3738, 'terms-conditions': 564, 'privacy-policy': 'privacy'}   # 'privacy' = new page, created by the push
SRC = {k: open(ROOT + f'coachingpages/{k}.html').read() for k in PAGES}

rid = lambda: ''.join(random.choice('0123456789abcdef') for _ in range(7))
def between(s, a, b):
    i = s.index(a); j = s.index(b, i + len(a)); return s[i:j + len(b)]

# ---------- images and links ----------
def fix_img(m):
    tag = m.group(0); src = re.search(r'src="([^"]+)"', tag).group(1)
    if src not in M: raise SystemExit('not uploaded: ' + src + ' (run tools/coaching_media.py)')
    return tag.replace(f'src="{src}"', f'src="{M[src]["url"]}"')   # alt stays as in the preview (live alt or approved)

def fix(s):
    s = re.sub(r'<img [^>]*>', fix_img, s)
    s = re.sub(r'href="(\.\./coaching/webp/[^"]+)"', lambda m: f'href="{M[m.group(1)]["url"]}"', s)   # gallery full-size links
    s = re.sub(r'href="' + re.escape(C) + r'(/[^"]*)" target="_blank" rel="noopener"', r'href="\1"', s)   # internal links stay on this site
    return re.sub(r'href="' + re.escape(C) + r'(/[^"]*)"', r'href="\1"', s)

# ---------- CSS: every <style> block of the previews, scoped to .cc ----------
css_blocks = []
for k, s in SRC.items():
    for b in re.findall(r'<style>(.*?)</style>', s, re.S):
        if 'color-scheme:light' in b: continue     # artifact skeleton, not ours
        if b not in css_blocks: css_blocks.append(b)
P = 'html .cc'
def scope_sel(sel):
    sel = sel.strip()
    if sel in (':root', 'html', 'body', 'html, body'): return P
    if sel == '*': return P + ' *'
    return P + ' ' + sel
def scope(block):
    out, i = [], 0
    while i < len(block):
        j = block.find('{', i)
        if j < 0: out.append(block[i:]); break
        head = re.sub(r'/\*.*?\*/', '', block[i:j], flags=re.S).strip()
        if head.startswith(('@media', '@supports')):
            depth, k = 1, j + 1
            while depth:
                depth += {'{': 1, '}': -1}.get(block[k], 0); k += 1
            out.append(head + ' {' + scope(block[j + 1:k - 1]) + '}\n'); i = k; continue
        k = block.index('}', j); body = block[j + 1:k]
        if head.startswith('@'): out.append(head + ' {' + body + '}\n')
        elif head in ('body::before', '.topo', '.page') or head.startswith('.ribbon'): pass   # preview-only
        else: out.append(', '.join(scope_sel(x) for x in head.split(',')) + ' {' + body + '}\n')
        i = k + 1
    return ''.join(out)
css = ''.join(scope(re.sub(r'/\*.*?\*/', '', b, flags=re.S)) for b in css_blocks)
tile_uri = 'data:image/svg+xml,' + urllib.parse.quote(open(ROOT + 'wp/topo-tile-min.svg').read(), safe=' =:/(),.-')
css += '''
/* ---- WordPress / Elementor integration (Coaching) ---- */
body:has(.cc-page) { background: linear-gradient(rgba(8,9,10,.6),rgba(8,9,10,.6)), #08090a url("''' + tile_uri + '''") top center / auto 3000px repeat-y !important; overflow-x: hidden; }
html .cc { background: transparent; color: var(--text-2); font-family: var(--body); font-size: 15px; line-height: 1.6; }
[data-elementor-type="header"]:has(.cc) { position: sticky; top: 0; z-index: 50; }
html .cc .nav { position: relative; top: 0; }
.e-con.cc-wrap, .cc-wrap > .e-con-inner { padding: 0 !important; gap: 0 !important; max-width: none !important; }
.cc-wrap .elementor-widget-html, .cc-wrap .elementor-widget-html .elementor-widget-container, .cc-wrap .elementor-widget-shortcode { width: 100%; }
body:has(.cc-page) .site-header, body:has(.cc-page) .site-footer { display: none; }
html .cc h1, html .cc h2, html .cc h3, html .cc h4 { font-family: var(--head); font-weight: 400; text-transform: uppercase; color: var(--text); letter-spacing: .01em; line-height: 1.14; }
html .cc h1 { line-height: 1.08; }
html .cc p, html .cc li, html .cc a, html .cc span, html .cc div, html .cc button, html .cc label, html .cc td, html .cc th, html .cc blockquote { font-family: var(--body); }
html .cc .tag-line, html .cc .stat .n, html .cc .pkg-price b, html .cc .cmp thead th, html .cc .dest-h { font-family: var(--head); }
html .cc .faq h3, html .cc footer .intl h2, html .cc footer .tag-sub, html .cc .btn-h { font-family: var(--body); text-transform: none; }
html .cc footer h4 { font: 600 11px/1.4 var(--body); letter-spacing: .1em; text-transform: uppercase; color: var(--text-3); }
html .cc .nums .l { font: 600 12px/1.4 var(--body); letter-spacing: .08em; text-transform: uppercase; color: var(--text-3); }
.cc-contact > .e-con-inner { gap: 48px !important; align-items: center; }
.cc-contact > .e-con-inner > .e-con:first-child { flex: 0 0 40% !important; width: auto !important; }
.cc-contact > .e-con-inner > .e-con:last-child { flex: 1 1 0 !important; width: auto !important; min-width: 0; }
html .cc footer .in > div { min-width: 0; }
html .cc footer li { overflow-wrap: anywhere; }
html .cc button, html .cc .btn { text-transform: none; letter-spacing: .02em; }
html .cc .dd-btn { text-transform: uppercase; letter-spacing: .04em; }
html body #cc-consent button, html body #cc-chat { text-transform: none; letter-spacing: normal; font-family: Montserrat, system-ui, sans-serif; }
html .cc .menu a[aria-current="page"], html .cc .dd-btn.is-current { color: var(--text); box-shadow: inset 0 -2px 0 var(--red); }
html .cc .dd-menu a[aria-current="page"] { color: var(--text); box-shadow: inset 3px 0 0 var(--red); }
html .cc .burger nav a[aria-current="page"] { color: var(--text); box-shadow: inset 3px 0 0 var(--red); padding-left: 12px; }
/* footer links: Elementor's kit link colour (.elementor-kit-6 a) must not win over the green hover */
.elementor-kit-6 .cc footer a:hover, .elementor-kit-6 .cc .legal a:hover { color: var(--green-text) !important; text-decoration: none !important; }
.elementor-kit-6 .cc footer a, .elementor-kit-6 .cc .legal a { text-decoration: none; }
.elementor-kit-6 .cc-social a { color: var(--text-2) !important; }
.elementor-kit-6 .cc-social a:hover { color: var(--green-text) !important; }
/* Shapo testimonials widget and the live Elementor contact form, in the brand */
.cc-shapo { margin-top: 18px; }
.cc-contact.e-con { --gap: 0px; }
.cc-contact .cc-form { width: 100% !important; max-width: 100% !important; --container-widget-width: 100% !important; margin: 22px 0 0 !important; box-sizing: border-box; }
.e-con.cc-wrap.cc-contact { padding: 72px 16px 0 !important; max-width: 1232px !important; margin: 0 auto !important; gap: 48px !important; }
.cc-contact .cc-page > div > .eyebrow { margin-top: 0; }
.cc-contact .cc-form .elementor-form, .cc-contact .cc-form .elementor-field-group { max-width: 100%; }
@media (max-width: 900px) {
  .cc-contact.e-con, .cc-contact > .e-con-inner { flex-direction: column !important; gap: 24px !important; }
  .cc-contact > .e-con-inner > .e-con:first-child, .cc-contact > .e-con-inner > .e-con:last-child { flex: 0 0 auto !important; width: 100% !important; }
  .cc-contact > .e-con, .cc-contact > .e-con-inner > .e-con { width: 100% !important; --width: 100% !important; }
  .cc-contact .photo.rider { aspect-ratio: 16 / 10; }
}
.cc-form .elementor-field-group { padding: 0 0 14px !important; width: 100% !important; max-width: 100% !important; flex: 0 0 100% !important; }
.cc-form .elementor-field-label { font: 600 12px Montserrat, system-ui, sans-serif !important; letter-spacing: .08em; text-transform: uppercase; color: #8a8f98 !important; padding-bottom: 6px; }
.cc-form .elementor-field-textual { font: 400 16px/1.4 Montserrat, system-ui, sans-serif !important; color: #f7f8f8 !important; background: rgba(255,255,255,.04) !important; border: 1px solid rgba(255,255,255,.14) !important; border-radius: 8px !important; padding: 12px 14px !important; }
.cc-form .elementor-field-textual:focus { outline: 2px solid #009a44 !important; outline-offset: 1px; }
.cc-form .elementor-button { font: 600 14px Montserrat, system-ui, sans-serif !important; letter-spacing: .02em; text-transform: none !important; border: 0 !important; box-shadow: none !important; background: #009a44 !important; color: #fff !important; border-radius: 8px !important; padding: 12px 22px !important; }
.cc-form .elementor-button:hover { background: #00b350 !important; }
.cc-form .elementor-field-type-submit { width: auto !important; flex: 0 0 auto !important; }
.cc-form .elementor-message { color: #d0d6e0; font-family: Montserrat, system-ui, sans-serif; }
.cc-form { background: linear-gradient(180deg, rgba(255,255,255,.045), rgba(255,255,255,.012)), rgba(15,16,17,.92); border: 1px solid rgba(255,255,255,.08); border-radius: 12px; padding: 22px !important; margin-top: 22px; }
'''
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;500;600;700&display=swap">'

# ---------- elementor helpers ----------
def html_widget(h, **st):
    return {"id": rid(), "elType": "widget", "widgetType": "html", "settings": {"html": h, **st}, "elements": [], "isInner": False}
def wrap(elements, cls='cc-wrap', inner=False, **st):
    s = {"content_width": "full", "css_classes": cls, "padding": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": True},
         "flex_gap": {"unit": "px", "size": 0, "column": "0", "row": "0"}, **st}
    return {"id": rid(), "elType": "container", "settings": s, "elements": elements, "isInner": inner}
def blocks_of(page_html):
    """top-level sections between the header and the footer, one Elementor container each"""
    main = page_html[page_html.index('</header>') + len('</header>'):page_html.index('<footer>')].strip()
    parts = re.split(r'\n\n(?=<(?:div|section)[ >])', main)
    return [p.strip() for p in parts if p.strip()]
def page_js(page_html):
    """the page's own script (after the shared menu script)"""
    scripts = re.findall(r'<script>.*?</script>', page_html, re.S)
    return [s for s in scripts if '.dd' not in s or 'pkg-all' in s or 'g-more' in s or 'rv-row' in s]

CURJS = "<script>(function(){var p=location.pathname;document.querySelectorAll('.cc .nav a[href]').forEach(function(a){var h=a.getAttribute('href');if(h&&h.charAt(0)==='/'&&!a.classList.contains('btn')&&!a.classList.contains('brand')&&h===p){a.setAttribute('aria-current','page');var d=a.closest('.dd');if(d){d.querySelector('.dd-btn').classList.add('is-current');}}});})();</script>"
DDJS = "<script>(function(){document.querySelectorAll('.cc .dd').forEach(function(d){var b=d.querySelector('.dd-btn');b.addEventListener('click',function(){var o=d.classList.toggle('open');b.setAttribute('aria-expanded',o);});d.addEventListener('focusout',function(e){if(!d.contains(e.relatedTarget)){d.classList.remove('open');b.setAttribute('aria-expanded','false');}});});})();</script>"

home = SRC['home']
# ---------- header ----------
hdr = fix(between(home, '<header class="nav">', '</header>'))
json.dump({"meta": {"_elementor_data": json.dumps([wrap([html_widget(FONTS + '<div class="cc">' + hdr + '</div>' + CURJS + DDJS)])])}}, open(OUT + 'lib-170.json', 'w'))

# ---------- footer + shared cookie banner ----------
ftr = fix(between(home, '<footer>', '</footer>'))
ftr = ftr.replace('<a href="/privacy-policy/">Privacy Policy</a>', '<a href="/privacy-policy/">Privacy Policy</a>\n    <a href="#" data-cc-settings>Cookie settings</a>')
assert 'data-cc-settings' in ftr
sys.path.insert(0, ROOT + 'shared/consent')
from render import banner as render_banner, head_snippet
GA = 'G-E1WWZCLBRB'            # live coaching site, checked 15 Nov (coaching/TRACKING.md)
PIXEL = '1986332861692106'     # Matteo's Meta Pixel, confirmed for Coaching 15 Nov; loads only after Accept
OW = '43e5f685-37fc-4f78-9420-122fd2a3c5e3'   # OpenWidget org on the live coaching site
banner = render_banner(ga_id=GA, privacy_url='/privacy-policy/', pixel_id=PIXEL, openwidget_org=OW)
# moving topo background (shared/parallax, Matteo: same on every site); only on redesigned pages (.cc-page), like Tours
PARALLAX = open(ROOT + 'shared/parallax/parallax.html').read().strip().replace("(function(){", "(function(){if(!document.querySelector('.cc-page'))return;", 1)
assert '.cc-page' in PARALLAX
json.dump({"meta": {"_elementor_data": json.dumps([wrap([html_widget('<div class="cc">' + ftr + '</div>'), html_widget(banner), html_widget(PARALLAX)])])}}, open(OUT + 'lib-228.json', 'w'))
json.dump({"title": "Cigala consent mode default", "status": "publish",
           "meta": {"_elementor_location": "elementor_head", "_elementor_priority": 1, "_elementor_code": head_snippet()}}, open(OUT + 'snippet-head.json', 'w'))

# ---------- pages ----------
def live_widget(page_id, wtype):
    d = json.loads(json.load(open(ROOT + f'stg-coaching/backup/page-{page_id}.json'))['meta']['_elementor_data'])
    def walk(els):
        for e in els:
            if e.get('widgetType') == wtype: return e
            r = walk(e.get('elements', []))
            if r: return r
    w = copy.deepcopy(walk(d)); assert w, (page_id, wtype); return w

def build_page(key):
    src = SRC[key]; els = []; content = []
    for b in blocks_of(src):
        b = fix(b)
        content.append('<div class="cc cc-page">' + b + '</div>')
        if 'id="contact"' in b:   # any page with the contact section gets the live Elementor form
            # live Elementor form (sends to info@cigalacycling.com) instead of the preview's static form
            form = live_widget(3338, 'form')
            form['settings']['_css_classes'] = 'cc-form'
            form['settings']['email_subject'] = 'New message from the Coaching website'
            pre, post = b.split('<form', 1)
            post = post.split('</form>', 1)[1]
            photo = re.search(r'<div class="photo rider">.*?</div>', pre, re.S).group(0)
            text = pre[pre.index('<div class="eyebrow">'):]
            left = wrap([html_widget('<div class="cc cc-page">' + photo + '</div>')], 'cc-wrap', True, width={"unit": "%", "size": 42}, width_mobile={"unit": "%", "size": 100})
            right = wrap([html_widget('<div class="cc cc-page"><div>' + text + '</div></div>'), form], 'cc-wrap', True, width={"unit": "%", "size": 58}, width_mobile={"unit": "%", "size": 100})
            row = wrap([left, right], 'cc-wrap cc-contact', True, flex_direction='row', flex_direction_mobile='column',
                       flex_gap={"unit": "px", "size": 48, "column": "48", "row": "24"}, flex_align_items='center',
                       boxed_width={"unit": "px", "size": 1200}, content_width='boxed',
                       padding={"unit": "px", "top": "72", "right": "16", "bottom": "0", "left": "16", "isLinked": False}, _element_id='contact')
            els.append(wrap([row]))
            continue
        w = [html_widget('<div class="cc cc-page">' + b + '</div>')]
        # (the Shapo widget is gone: Matteo chose our own review cards + a link to the Google reviews, 15 Nov)
        els.append(wrap(w))
    for s in page_js(src): els[-1]['elements'].append(html_widget(s))
    payload = {"meta": {"_elementor_data": json.dumps(els), "_elementor_edit_mode": "builder", "_elementor_template_type": "wp-page"}, "content": '\n'.join(content)}
    if PAGES[key] == 'privacy':
        payload.update({"title": "Privacy Policy", "slug": "privacy-policy", "status": "publish"})
    json.dump(payload, open(OUT + f'page-{PAGES[key]}.json', 'w'))
    return len(els)

n = {k: build_page(k) for k in PAGES}

# ---------- kit: add the scoped CSS, keep everything else ----------
kit = copy.deepcopy(json.load(open(ROOT + 'stg-coaching/backup/lib-6.json'))['meta']['_elementor_page_settings'])
kit['custom_css'] = css
json.dump({"meta": {"_elementor_page_settings": kit}}, open(OUT + 'lib-6.json', 'w'))
print('built:', n, '| css', len(css), '| header', len(hdr), '| footer', len(ftr))

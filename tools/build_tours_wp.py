"""Build the Elementor payloads for Tours staging from the approved preview pages.

Writes stg-tours/out/:
  lib-6.json     kit: the brand CSS, scoped to .cc, so pages not rebuilt yet keep their old look
  lib-170.json   header: new nav with the Bike Tours dropdown
  lib-228.json   footer: new footer + the existing chat (OpenWidget) and cookie widgets, unchanged
  page-5212.json homepage

Run tools/build_tours_home.py first. Push with tools/push_tours_wp.py.
"""
import os, re, sys, json, copy, random, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
OUT = ROOT + 'stg-tours/out/'
os.makedirs(OUT, exist_ok=True)
L = 'https://tours.cigalacycling.com'
M = json.load(open(ROOT + 'stg-tours/media-webp.json'))
home = open(ROOT + 'tourspages/home.html').read()

def rid():
    return ''.join(random.choice('0123456789abcdef') for _ in range(7))

def between(s, a, b):
    i = s.index(a); j = s.index(b, i + len(a)); return s[i:j + len(b)]

# ---------- images: preview file -> staging WebP + alt ----------
IMG = {
    'img/home-hero.jpg': 'hero', 'img/home-custom.jpg': 'custom', 'img/home-cta.jpg': 'cta',
    'img/home-story.jpg': 'story', 'img/home-matteo.png': 'matteo', 'img/logo.png': 'logo-v2',
    'img/cigala-tours-signature.webp': 'signature',
    'img/guides-0.jpg': 'guide-flanders', 'img/guides-1.jpg': 'guide-como', 'img/guides-2.jpg': 'guide-pack',
    'img/logo-mdd.png': 'logo-mdd', 'img/logo-lombardia.png': 'logo-lombardia-v2', 'img/logo-strade.png': 'logo-strade-v3', 'img/logo-algarve.png': 'logo-algarve', 'img/logo-wrf.png': 'logo-wrf',   # previous Algarve logo (Matteo)
}
def fix_img(m):
    tag = m.group(0)
    src = re.search(r'src="([^"]+)"', tag).group(1)
    key = IMG.get(src) or (src[4:-5] if src.startswith('img/trip-') and src.endswith('.webp') else None) \
        or (src[len('img/cigala-tours-'):-5] if src.startswith('img/cigala-tours-guest-') else None)
    key = key or (src[4:-5] if src.startswith('img/flag-') else None)
    if not key: raise SystemExit('no staging image for ' + src)
    tag = tag.replace(f'src="{src}"', f'src="{M[key]["url"]}"')
    alt = re.search(r'alt="([^"]*)"', tag).group(1)
    keep_page_alt = key.startswith(('trip-', 'flag-')) or key in ('hero', 'matteo', 'signature')   # alt written for these spots in the design
    if not alt or not keep_page_alt:
        tag = re.sub(r'alt="[^"]*"', 'alt="' + M[key]['alt'].replace('"', '&quot;') + '"', tag)  # the alt the image already has on the site
    return tag

def fix(s):
    s = re.sub(r'<img [^>]*>', fix_img, s)
    # internal links stay on the site they are on (staging now, live after the push)
    s = re.sub(r'href="' + re.escape(L) + r'(/[^"]*)" target="_blank" rel="noopener"', r'href="\1"', s)
    s = s.replace('href="' + L + '/"', 'href="/"')
    s = re.sub(r'href="' + re.escape(L) + r'(/[^"]*)"', r'href="\1"', s)
    s = re.sub(r'action="' + re.escape(L) + r'(/[^"]*)"', r'action="\1"', s)
    return s

# ---------- CSS: scope every rule to .cc ----------
css = between(home, '<style>\n/* Cigala Cycling kit', '</style>')[len('<style>'):-len('</style>')]
P = 'html .cc'
def scope_sel(sel):
    sel = sel.strip()
    if sel in (':root', 'html', 'body', 'html, body'): return P
    if sel == '*': return P + ' *'
    if sel.startswith(('::', ':')): return P + ' ' + sel
    return P + ' ' + sel
def scope(block):
    out, i = [], 0
    while i < len(block):
        j = block.find('{', i)
        if j < 0: out.append(block[i:]); break
        head = block[i:j].strip()
        if head.startswith('@media') or head.startswith('@supports'):
            depth, k = 1, j + 1
            while depth:
                depth += {'{': 1, '}': -1}.get(block[k], 0); k += 1
            out.append(head + ' {' + scope(block[j + 1:k - 1]) + '}\n'); i = k; continue
        k = block.index('}', j)
        body = block[j + 1:k]
        head = re.sub(r'/\*.*?\*/', '', head, flags=re.S).strip()
        if head.startswith('@'): out.append(head + ' {' + body + '}\n')
        elif head in ('body::before', '.topo', '.page') or head.startswith('.ribbon'): pass   # preview-only
        else: out.append(', '.join(scope_sel(x) for x in head.split(',')) + ' {' + body + '}\n')
        i = k + 1
    return ''.join(out)
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
css = scope(css)
tile = open(ROOT + 'wp/topo-tile-min.svg').read()
tile_uri = 'data:image/svg+xml,' + urllib.parse.quote(tile, safe=' =:/(),.-')
css += '''
/* ---- WordPress / Elementor integration (Tours) ---- */
body:has(.cc-page), body:has(.cl-page) { background: linear-gradient(rgba(8,9,10,.6),rgba(8,9,10,.6)), #08090a url("''' + tile_uri + '''") top center / auto 3000px repeat-y !important; overflow-x: hidden; }
html .cc { background: transparent; }
[data-elementor-type="header"]:has(.cc) { position: sticky; top: 0; z-index: 50; }
html .cc .nav { position: relative; top: 0; }
.e-con.cc-wrap, .cc-wrap > .e-con-inner { padding: 0 !important; gap: 0 !important; max-width: none !important; }
.cc-wrap .elementor-widget-html, .cc-wrap .elementor-widget-html .elementor-widget-container { width: 100%; }
body:has(.cc-page) .site-header, body:has(.cc-page) .site-footer { display: none; }
html .cc h1, html .cc h2, html .cc h3, html .cc h4 { font-family: var(--head); font-weight: 400; text-transform: uppercase; color: var(--text); letter-spacing: .01em; line-height: 1.04; }
html .cc p, html .cc li, html .cc a, html .cc span, html .cc div, html .cc select, html .cc button, html .cc label { font-family: var(--body); }
html .cc h1, html .cc h2, html .cc h3, html .cc h4, html .cc .tag-line, html .cc .stat .n { font-family: var(--head); }
html .cc footer .in > div { min-width: 0; }
html .cc footer li { overflow-wrap: anywhere; }
html .cc button, html .cc .btn { text-transform: none; letter-spacing: .02em; }
html .cc .dd-btn { text-transform: uppercase; letter-spacing: .04em; }
html body #cc-consent button, html body #cc-chat { text-transform: none; letter-spacing: normal; font-family: Montserrat, system-ui, sans-serif; }
html .cc .menu a[aria-current="page"], html .cc .dd-btn.is-current { color: var(--text); box-shadow: inset 0 -2px 0 var(--red); }
html .cc .menu a[aria-current="page"], html .cc .dd-btn.is-current, html .cc .dd .dd-btn { border-radius: 0; }
html .cc .dd-btn.is-current, html .cc .dd:hover .dd-btn.is-current { background: none; }
html .cc .dd-btn { display: inline-flex; align-items: center; gap: 4px; line-height: inherit; font-size: 12.5px; }
/* square logos with their own background fill the tile (We Ride Flanders) */
html body .logos span.fill { padding: 0 !important; overflow: hidden; background: #ffe500 !important; }
html body .logos span.fill img { width: 100% !important; height: 100% !important; max-height: none !important; object-fit: cover; transform: scale(1.06); }
html .logos span.txt { width: 96px; height: 96px; padding: 8px; font-family: var(--head); font-size: 15px; line-height: 1.05; text-align: center; text-transform: uppercase; color: #111; }
/* shared social icons: Elementor's kit link colour would override them */
.elementor-kit-6 .cc-social a { color: var(--text-2); }
.elementor-kit-6 .cc-social a:hover, .elementor-kit-6 .cc-social a:active { color: var(--green-text); }
/* a little more air between lines of the uppercase titles (Matteo) */
html .cc h1, html .cl h1 { line-height: 1.08 !important; }
html .cc h2, html .cc h3, html .cl h2, html .cl h3 { line-height: 1.14 !important; }
html .cl h3.where { line-height: 1.4 !important; }
/* menu: same as cigalacycling.com (brand.css 58-69) */
html .cc .menu a, html .cc .dd-btn { border-radius: 0; background: none; box-shadow: inset 0 0 0 var(--green); transition: color .15s, box-shadow .15s; }
html .cc .menu a:hover, html .cc .menu a:active, html .cc .dd-btn:hover, html .cc .dd:focus-within .dd-btn, html .cc .dd.open .dd-btn { color: var(--green-text); background: none; box-shadow: inset 0 -2px 0 var(--green); }
html .cc .menu a[aria-current="page"], html .cc .dd-btn.is-current, html .cc .dd:hover .dd-btn.is-current { color: var(--text); background: none; box-shadow: inset 0 -2px 0 var(--red); }
html .cc .dd-menu a { border-radius: 0; background: none; box-shadow: none; transition: color .15s, box-shadow .15s; }
html .cc .dd-menu a:hover, html .cc .dd-menu a:active { color: var(--green-text); background: none; box-shadow: inset 2px 0 0 var(--green); }
html .cc .dd-menu a[aria-current="page"] { color: var(--text); box-shadow: inset 2px 0 0 var(--red); }
html .cc .burger nav a, html .cc .burger details.sub > summary { transition: color .15s; }
html .cc .burger nav a:hover, html .cc .burger nav a:active, html .cc .burger details.sub > summary:hover { color: var(--green-text); }
/* footer links: green on hover like the menu, no underline (Matteo left the choice to us) */
html .cc footer a { text-decoration: none; transition: color .15s; }
html .cc footer a:hover, html .cc footer a:active, html .cc footer a:focus-visible, html .cc footer ul a:hover { color: var(--green-text); }
html .cc footer h4 { font-family: var(--body); font-size: 11px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: var(--text-3); line-height: 1.4; }
html .cc .dd-menu a[aria-current="page"] { color: var(--text); box-shadow: inset 3px 0 0 var(--red); }
html .cc .burger details.sub > summary.is-current { box-shadow: inset 3px 0 0 var(--red); padding-left: 12px; }
html .cc .burger nav a[aria-current="page"] { color: var(--text); box-shadow: inset 3px 0 0 var(--red); padding-left: 12px; }
'''
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;500;600;700&display=swap">'

# ---------- elementor helpers ----------
def html_widget(h):
    return {"id": rid(), "elType": "widget", "widgetType": "html", "settings": {"html": h}, "elements": [], "isInner": False}

def wrap(elements):
    st = {"content_width": "full", "css_classes": "cc-wrap", "padding": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": True}, "flex_gap": {"unit": "px", "size": 0, "column": "0", "row": "0"}}
    return {"id": rid(), "elType": "container", "settings": st, "elements": elements, "isInner": False}

# ---------- JS split: menu (header) / finder (homepage) ----------
js = between(home, '<script>\n(function () {\n  var f = document.getElementById', '</script>')
CURJS = "<script>(function(){var p=location.pathname;document.querySelectorAll('.cc .nav a[href]').forEach(function(a){var h=a.getAttribute('href');if(h&&h.charAt(0)==='/'&&!a.classList.contains('btn')&&!a.classList.contains('brand')&&h===p){a.setAttribute('aria-current','page');var d=a.closest('.dd');if(d){d.querySelector('.dd-btn').classList.add('is-current');}var u=a.closest('details.sub');if(u){u.open=true;u.querySelector('summary').classList.add('is-current');}}});})();</script>"
dd_js = "<script>(function(){document.querySelectorAll('.cc .dd').forEach(function(d){var b=d.querySelector('.dd-btn');b.addEventListener('click',function(){var o=d.classList.toggle('open');b.setAttribute('aria-expanded',o);});d.addEventListener('focusout',function(e){if(!d.contains(e.relatedTarget)){d.classList.remove('open');b.setAttribute('aria-expanded','false');}});});})();</script>"
finder_js = re.sub(r"\n  document\.querySelectorAll\('\.dd'\).*?\n  \}\);\n", '\n', js, flags=re.S)
assert 'dd-btn' not in finder_js

# ---------- header ----------
hdr = fix(between(home, '<header class="nav">', '</header>'))
json.dump({"meta": {"_elementor_data": json.dumps([wrap([html_widget(FONTS + '<div class="cc">' + hdr + '</div>' + CURJS + dd_js)])])}}, open(OUT + 'lib-170.json', 'w'))

# ---------- footer: new design + existing chat and cookie widgets ----------
ftr = fix(between(home, '<footer>', '</footer>'))
# tours list order comes from the preview (MENU_TOURS)
# consent banner + "Chat with us" button: same as cigalacycling.com (wp/consent-banner.html), Tours version.
# Tours has Google Analytics G-QRF16ZZVDB and no Meta Pixel. gtag.js only loads after Accept.
# Shared Cigala cookie banner (shared/consent/, README there). Tours IDs checked on the live site 15 Nov:
# GA4 G-QRF16ZZVDB, OpenWidget org 43e5f685-...; Meta Pixel added on Matteo's confirmation (15 Nov), loads only after Accept.
sys.path.insert(0, ROOT + 'shared/consent')
from render import banner as render_banner, head_snippet
GA = 'G-QRF16ZZVDB'
PIXEL = '1986332861692106'   # Matteo's single Meta Pixel, confirmed for Tours on 15 Nov (same on all Cigala sites)
banner = render_banner(ga_id=GA, privacy_url='/privacy-policy/', pixel_id=PIXEL, openwidget_org='43e5f685-37fc-4f78-9420-122fd2a3c5e3')   # Tours' own privacy page
ftr = ftr.replace('<a href="/terms-conditions/">Refund/cancellation policy &amp; terms</a>', '<a href="/terms-conditions/">Refund/cancellation policy &amp; terms</a>\n    <a href="/privacy-policy/">Privacy Policy</a>\n    <a href="#" data-cc-settings>Cookie settings</a>')
assert 'data-cc-settings' in ftr
ftr = ftr.replace('>Refund/cancellation policy &amp; terms</a>', '>Refund/Cancellation Policy &amp; Terms</a>')   # capitals (Matteo)
ftr = ftr.replace('★ Google reviews', '<span class="gstar">★</span> Google reviews')   # gold star, like the Retail site (Matteo 15 Nov)
css += '\nhtml .cc .gstar { color: #f0bf00; }\n'
# topo background parallax: the lines drift slower than the page, so you see them move (off for reduced motion)
PARALLAX = "<script>(function(){if(!document.querySelector('.cc-page,.cl-page')||matchMedia('(prefers-reduced-motion: reduce)').matches)return;var b=document.body,q=0;function u(){q=0;b.style.setProperty('background-position','0 0, center '+(window.scrollY*0.4).toFixed(1)+'px','important');}addEventListener('scroll',function(){if(!q){q=1;requestAnimationFrame(u);}},{passive:true});u();})();</script>"

# Newsletter (Matteo 15 Nov: same sign-up as cigalacycling.com and Coaching, one newsletter for all sites):
# footer band wp/nl-band.html + pop-up wp/nl-popup.html, used as they are, posting to the Tours Brevo form.
# Off until TOURS_NL_URL is set (the share link of Matteo's Brevo form on the "tours.cigalacycling.com" list, + ?isAjax=1).
TOURS_NL_URL = 'https://c20401b9.sibforms.com/serve/MUIFAIbkCsq9ZvLkP_z6BAzvk_HXMj0FmU12UW_FL7rdnXYZPfkTPvoo0NQrsMFXdArQaS1g48pseXMdwaQ9evslAasHA6tfJXRb5FU12EEHctxV3gGFqzOA2kp2dcG0jkObzljbSAaeZ65sepCFudotu-EGqXPHhDwZ3J3my8LJnugvlyZtlQWxLZHbS5Hk0voDhkyOt-XN1Or8?isAjax=1'   # Brevo form, list tours.cigalacycling.com (Matteo 15 Nov); CORS checked for staging and live
ftr_widgets = [html_widget('<div class="cc">' + ftr + '</div>' + PARALLAX), html_widget(banner)]
if TOURS_NL_URL:
    nlband = open(ROOT + 'wp/nl-band.html').read()
    nlpop = open(ROOT + 'wp/nl-popup.html').read()
    nlpop = re.sub(r"var URL='https://[^']+';", "var URL='" + TOURS_NL_URL + "';", nlpop); assert TOURS_NL_URL in nlpop
    # Tours wording (Matteo 15 Nov: the Tours sign-up talks about tours); the note keeps 'one newsletter for all our websites'
    TOURS_NL = [(r'<p class="nl-eyebrow">[^<]*</p>', '<p class="nl-eyebrow">Tour news</p>'),
                (r'<p class="nl-t"( id="nl-pop-t")?>[^<]*</p>', lambda m: f'<p class="nl-t"{m.group(1) or ""}>Ride with us in 2027</p>'),
                (r'<p class="nl-d">[^<]*</p>', '<p class="nl-d">New tour dates, early-bird offers, route guides and news from our bike tours across Europe.</p>')]
    for a, b in TOURS_NL:
        nlband, n1 = re.subn(a, b, nlband); nlpop, n2 = re.subn(a, b, nlpop); assert n1 and n2, a
    ftr_widgets[0] = html_widget('<div class="cc">' + nlband + ftr + '</div>' + PARALLAX)
    ftr_widgets.append(html_widget(nlpop))
    # Tours: the .cc text rule would turn the band title into Montserrat; and the pop-up must sit above the chat widget
    css += '\n/* ---- newsletter (shared wp/nl-*) ---- */\nhtml .cc .nl-band .nl-t { font-family: Anton, Impact, "Arial Narrow", sans-serif; font-weight: 400; }\nhtml .cc .nl-band { border-bottom: 0 !important; }\nhtml .cc .nl-band .nl-band-in { padding-block: 40px !important; }\nhtml .cc .nl-band + footer { margin-top: 0 !important; }\n#nl-pop { z-index: 2147483647 !important; }\n'
json.dump({"meta": {"_elementor_data": json.dumps([wrap(ftr_widgets)])}}, open(OUT + 'lib-228.json', 'w'))

# head snippet (Elementor custom code 9279): the shared one. The consent-default line goes first in WPCode Header (Matteo).
head_code = head_snippet()
json.dump({"meta": {"_elementor_location": "elementor_head", "_elementor_priority": 1, "_elementor_code": head_code}}, open(OUT + 'snippet-9279.json', 'w'))

# ---------- homepage ----------
main = home[home.index('</header>') + len('</header>'):home.index('<footer>')]
main = fix(main.strip())
blocks = re.split(r'\n(?=<(?:div class="hero|div class="in stats-wrap|section)[ >])', '\n' + main)
blocks = [b.strip() for b in blocks if b.strip()]
els = [wrap([html_widget('<div class="cc cc-page">' + b + '</div>')]) for b in blocks]
els[-1]['elements'].append(html_widget(finder_js))
cj = re.search(r"<script>\(function\(\)\{var l=document\.querySelectorAll\('\.stats \.stat \.n'\).*?</script>", home, re.S)   # count-up numbers (Matteo 15 Nov)
assert cj, 'count-up script missing from tourspages/home.html'
els[-1]['elements'].append(html_widget(cj.group(0)))
# Matteo 16 Nov: a subtle, livelier homepage: section titles and tour cards rise in as they come into view, and the signature writes itself
HOME_DYN = ("""<script>(function(){if(!('IntersectionObserver' in window)||matchMedia('(prefers-reduced-motion: reduce)').matches)return;var d=document.documentElement;d.classList.add('hdyn-ok');
var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){o.unobserve(e.target);e.target.classList.add('in-view');}});},{threshold:.15});
document.querySelectorAll('.cc-page section .head, .cc-page .tour').forEach(function(x){var g=x.parentElement?[].indexOf.call(x.parentElement.children,x):0;if(x.classList.contains('tour'))x.style.setProperty('--d',(g%3)*90+'ms');o.observe(x);});
var s=document.querySelectorAll('.cc img.signature');if(s.length){d.classList.add('sig-ok');var q=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){q.unobserve(e.target);e.target._sig.classList.add('go');}});},{threshold:.5});s.forEach(function(x){x.loading='eager';var t=x.nextElementSibling||x.parentElement;t._sig=x;q.observe(t);});}})();</script>""")
els[-1]['elements'].append(html_widget(HOME_DYN))
content = '\n'.join('<div class="cc cc-page">' + b + '</div>' for b in blocks)
json.dump({"meta": {"_elementor_data": json.dumps(els), "_elementor_edit_mode": "builder"}, "content": content}, open(OUT + 'page-5212.json', 'w'))

# ---------- kit: only add the scoped CSS, keep everything else ----------
kit = copy.deepcopy(json.load(open(ROOT + 'stg-tours/backup/lib-6.json'))['meta']['_elementor_page_settings'])
# trip-list pages (tools/build_tours_list.py) bring their own CSS, scoped to .cl
import glob
_seen = set()
for f in sorted(glob.glob(ROOT + 'stg-tours/out/list-*.json')):
    c = json.load(open(f))['css']
    if c in _seen: continue   # all list pages share one stylesheet
    _seen.add(c); css += '\n/* ---- trip-list pages (.cl) ---- */\n' + c
# contact forms (Contact 461, Custom tours 1576; tools/tours_forms.py adds the class): the Coaching .cc-form rules, read from
# tools/build_coaching_wp.py so both sites stay identical (Matteo 15 Nov: every contact form looks like Coaching's)
FORM_CSS = '\n'.join(l for l in open(ROOT + 'tools/build_coaching_wp.py').read().split('\n') if l.startswith(('.cc-form ', '.cc-form{', '.cc-form {')))
assert FORM_CSS.count('.cc-form') >= 9, 'Coaching form CSS not found'
css += '\n/* ---- contact forms, same as Coaching ---- */\n' + FORM_CSS + '\n'
kit['custom_css'] = css
json.dump({"meta": {"_elementor_page_settings": kit}}, open(OUT + 'lib-6.json', 'w'))
print('built: home blocks', len(blocks), '| css', len(css), '| header', len(hdr), '| footer', len(ftr))

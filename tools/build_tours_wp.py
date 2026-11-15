"""Build the Elementor payloads for Tours staging from the approved preview pages.

Writes stg-tours/out/:
  lib-6.json     kit: the brand CSS, scoped to .cc, so pages not rebuilt yet keep their old look
  lib-170.json   header: new nav with the Bike Tours dropdown
  lib-228.json   footer: new footer + the existing chat (OpenWidget) and cookie widgets, unchanged
  page-5212.json homepage

Run tools/build_tours_home.py first. Push with tools/push_tours_wp.py.
"""
import os, re, json, copy, random, urllib.parse

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
    'img/logo-mdd.png': 'logo-mdd', 'img/logo-lombardia.png': 'logo-lombardia', 'img/logo-strade.png': 'logo-strade', 'img/logo-algarve.png': 'logo-algarve',
}
def fix_img(m):
    tag = m.group(0)
    src = re.search(r'src="([^"]+)"', tag).group(1)
    key = IMG.get(src) or (src[4:-5] if src.startswith('img/trip-') and src.endswith('.webp') else None) \
        or (src[len('img/cigala-tours-'):-5] if src.startswith('img/cigala-tours-guest-') else None)
    if not key: raise SystemExit('no staging image for ' + src)
    tag = tag.replace(f'src="{src}"', f'src="{M[key]["url"]}"')
    alt = re.search(r'alt="([^"]*)"', tag).group(1)
    keep_page_alt = key.startswith('trip-') or key in ('hero', 'matteo', 'signature')   # alt written for these spots in the design
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
body:has(.cc-page) { background: linear-gradient(rgba(8,9,10,.6),rgba(8,9,10,.6)), #08090a url("''' + tile_uri + '''") top center / auto 3000px repeat-y !important; overflow-x: hidden; }
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
html .cc .dd-menu a[aria-current="page"] { color: var(--text); box-shadow: inset 3px 0 0 var(--red); }
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
CURJS = "<script>(function(){var p=location.pathname;document.querySelectorAll('.cc .nav a[href]').forEach(function(a){var h=a.getAttribute('href');if(h&&h.charAt(0)==='/'&&!a.classList.contains('btn')&&!a.classList.contains('brand')&&h===p){a.setAttribute('aria-current','page');var d=a.closest('.dd');if(d){d.querySelector('.dd-btn').classList.add('is-current');}}});})();</script>"
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
GA = 'G-QRF16ZZVDB'
banner = open(ROOT + 'wp/consent-banner.html').read()
def brep(a, b):
    global banner
    assert banner.count(a) == 1, a[:70]
    banner = banner.replace(a, b)
# banner text: identical on every Cigala site (Matteo, 15 Nov)
brep("var GA='G-955J6LHQ2P', PX='1986332861692106';", "var GA='" + GA + "', PX='';")
brep("    if(window.fbq)return;", "    if(!PX||window.fbq)return;")
brep("    if(typeof gtag==='function'){gtag('consent','update',{ad_storage:'granted',ad_user_data:'granted',ad_personalization:'granted',analytics_storage:'granted'});gtag('config',GA);}",
     "    window.dataLayer=window.dataLayer||[];if(typeof gtag!=='function'){window.gtag=function(){dataLayer.push(arguments);};}\n"
     "    gtag('consent','update',{ad_storage:'granted',ad_user_data:'granted',ad_personalization:'granted',analytics_storage:'granted'});\n"
     "    if(!document.querySelector('script[src*=\"gtag/js?id='+GA+'\"]')){var g=document.createElement('script');g.async=true;g.src='https://www.googletagmanager.com/gtag/js?id='+GA;document.head.appendChild(g);gtag('js',new Date());}\n"
     "    gtag('config',GA);")
ftr = ftr.replace('<a href="/terms-conditions/">Refund/cancellation policy &amp; terms</a>', '<a href="/terms-conditions/">Refund/cancellation policy &amp; terms</a>\n    <a href="#" data-cc-settings>Cookie settings</a>')
assert 'data-cc-settings' in ftr
json.dump({"meta": {"_elementor_data": json.dumps([wrap([html_widget('<div class="cc">' + ftr + '</div>'), html_widget(banner)])])}}, open(OUT + 'lib-228.json', 'w'))

# head snippet (Elementor custom code 9279): consent default denied; returning visitors who accepted get GA loaded
head_code = ("<script>window.dataLayer=window.dataLayer||[];if(typeof window.gtag!=='function'){window.gtag=function(){dataLayer.push(arguments);};}"
    "gtag('consent','default',{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:'denied',wait_for_update:500});"
    "(function(){var GA='" + GA + "',c=null;try{c=localStorage.getItem('cc_consent');}catch(e){}"
    "if(c==='granted'){gtag('consent','update',{ad_storage:'granted',ad_user_data:'granted',ad_personalization:'granted',analytics_storage:'granted'});"
    "if(!document.querySelector('script[src*=\"gtag/js?id='+GA+'\"]')){var g=document.createElement('script');g.async=true;g.src='https://www.googletagmanager.com/gtag/js?id='+GA;document.head.appendChild(g);gtag('js',new Date());gtag('config',GA);}}"
    "else{window['ga-disable-'+GA]=true;}})();</script>")
json.dump({"meta": {"_elementor_location": "elementor_head", "_elementor_priority": 1, "_elementor_code": head_code}}, open(OUT + 'snippet-9279.json', 'w'))

# ---------- homepage ----------
main = home[home.index('</header>') + len('</header>'):home.index('<footer>')]
main = fix(main.strip())
blocks = re.split(r'\n(?=<(?:div class="hero|div class="in stats-wrap|section)[ >])', '\n' + main)
blocks = [b.strip() for b in blocks if b.strip()]
els = [wrap([html_widget('<div class="cc cc-page">' + b + '</div>')]) for b in blocks]
els[-1]['elements'].append(html_widget(finder_js))
content = '\n'.join('<div class="cc cc-page">' + b + '</div>' for b in blocks)
json.dump({"meta": {"_elementor_data": json.dumps(els), "_elementor_edit_mode": "builder"}, "content": content}, open(OUT + 'page-5212.json', 'w'))

# ---------- kit: only add the scoped CSS, keep everything else ----------
kit = copy.deepcopy(json.load(open(ROOT + 'stg-tours/backup/lib-6.json'))['meta']['_elementor_page_settings'])
kit['custom_css'] = css
json.dump({"meta": {"_elementor_page_settings": kit}}, open(OUT + 'lib-6.json', 'w'))
print('built: home blocks', len(blocks), '| css', len(css), '| header', len(hdr), '| footer', len(ftr))

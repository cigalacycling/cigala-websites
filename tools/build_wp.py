# Builds Elementor data for cigalacycling.com staging from the approved preview pages.
# Writes JSON payloads to scratchpad/wp/out/ ; push_wp.py sends them.
import re, json, copy, urllib.parse, random, string
random.seed(20261115)  # repeatable Elementor element IDs, so rebuilds only change what really changed
S = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))) + '/'
H = S + 'home/'
OUT = S + 'wp/out/'
import os; os.makedirs(OUT, exist_ok=True)
media = json.load(open(S + 'stg/media.json'))
IMG = {k: v['url'] for k, v in media.items()}
# WebP versions (q90 from the largest originals); same keys as the preview's img/ names
W = json.load(open(S + 'stg/media-webp.json'))
IMG.update({
    'logo.png': W['cigala-cycling-logo']['url'],
    'coaching.jpg': W['cigala-coaching-riders']['url'],
    'tours.jpg': W['cigala-tours-riders-cyprus-card']['url'],
    'retail.jpg': W['cigala-retail-smart-bike']['url'],
    'matteo-white.png': W['matteo-cigala-white-jersey']['url'],
    'contact.jpg': W['cigala-group-black-kit']['url'],
    'team-white.jpg': W['cigala-team-white-jerseys-1200']['url'] + '" srcset="' + W['cigala-team-white-jerseys-1200']['url'] + ' 1200w, ' + W['cigala-team-white-jerseys']['url'] + ' 2400w" sizes="100vw',
})

def rid():
    return ''.join(random.choice('0123456789abcdef') for _ in range(7))

def read(fn):
    return open(H + fn).read()

def between(s, a, b, start=0):
    i = s.index(a, start); j = s.index(b, i + len(a))
    return s[i:j + len(b)]

def fix_links(s):
    s = s.replace('href="./"', 'href="/"')
    s = s.replace('href="about.html"', 'href="/about/"').replace('href="contact.html"', 'href="/contact/"').replace('href="terms.html"', 'href="/terms-conditions/"').replace('href="privacy.html"', 'href="/privacy-policy/"')
    for k, u in IMG.items():
        s = s.replace(f'src="img/{k}"', f'src="{u}"')
    s = re.sub(r'\s*target="_blank" rel="noopener"', lambda m: m.group(0), s)
    return s

def main_of(fn):
    s = read(fn)
    i = s.index('</header>') + len('</header>')
    j = s.index('<footer>')
    return fix_links(s[i:j].strip())

# ---------- CSS ----------
css = open(S + 'brand.css').read()
extra = re.search(r"EXTRA='''(.*?)'''", open(S + 'tools/build.py').read(), re.S).group(1)
css = css + extra
import sys as _sys; _sys.path.insert(0, S + 'shared/social'); from social import SOCIAL_CSS
css = css + SOCIAL_CSS + '\n.elementor-kit-6 .cc-social a { color: var(--text-2); }\n.elementor-kit-6 .cc-social a:hover, .elementor-kit-6 .cc-social a:active { color: var(--green-text); }\n'
css = re.sub(r'/\* preview ribbon \*/.*?\.ribbon b \{[^}]*\}', '', css, flags=re.S)
css = re.sub(r'\.topo \{[^}]*\}', '', css)
css = css.replace('.page { position: relative; z-index: 1; }', '')
tile = open(S + 'wp/topo-tile-min.svg').read()
tile_uri = 'data:image/svg+xml,' + urllib.parse.quote(tile, safe=' =:/(),.-')
css = css.replace('html, body { background: var(--bg); color: var(--text-2); font-family: var(--body); }',
  'html, body { background: var(--bg); color: var(--text-2); font-family: var(--body); }\n'
  'body { background: linear-gradient(rgba(8,9,10,.6),rgba(8,9,10,.6)), #08090a url("' + tile_uri + '") top center / auto 3000px repeat-y !important; }')
css += '''
/* WordPress / Elementor integration */
body { overflow-x: hidden; }
[data-elementor-type="header"] { position: sticky; top: 0; z-index: 50; }
footer[data-elementor-type="footer"] { margin-top: 0 !important; border-top: 0 !important; background: none !important; }
footer[data-elementor-type="footer"] footer { margin-top: 64px; }
.elementor-kit-6 footer ul a { color: var(--text-2); }
.elementor-kit-6 footer ul a:hover, .elementor-kit-6 footer ul a:active { color: var(--green-text); text-decoration: none; }
@media (max-width: 640px) { footer[data-elementor-type="footer"] footer { margin-top: 52px; } }
.elementor-widget-html, .elementor-widget-html .elementor-widget-container { width: 100%; }
.e-con.cc-wrap, .cc-wrap > .e-con-inner { padding: 0 !important; gap: 0 !important; max-width: none !important; }
.site-header, .site-footer { display: none; }
a:focus-visible, button:focus-visible { outline: 2px solid var(--green); outline-offset: 2px; }
/* contact form (Elementor form widget) */
.cc-form .elementor-field-group { margin-bottom: 0; padding: 0 0 14px !important; }
.cc-form label.elementor-field-label { font: 600 12px/1.4 var(--body); letter-spacing: .08em; text-transform: uppercase; color: var(--text-3); margin-bottom: 6px; }
.cc-form .elementor-field { font: 16px/1.4 var(--body) !important; color: var(--text) !important; background: rgba(255,255,255,.04) !important; border: 1px solid var(--border-strong) !important; border-radius: 8px !important; padding: 12px 14px !important; }
.cc-form .elementor-field:focus { outline: 2px solid var(--green) !important; outline-offset: 1px; }
.cc-form .elementor-button { background: var(--green) !important; color: #fff !important; border: 0 !important; border-radius: 8px !important; font: 600 14px var(--body) !important; letter-spacing: .02em; text-transform: none !important; padding: 12px 22px !important; }
.cc-form .elementor-button:hover { background: var(--green-hi) !important; }
.cc-form .elementor-message { color: var(--green-text); }
.cc-formcol > .elementor-element, .cc-formcol .elementor-widget-form, .cc-form { width: 100% !important; max-width: 100% !important; align-self: stretch !important; }
.cc-form .elementor-form-fields-wrapper { width: 100%; }
.cc-formcol { background: var(--panel-grad), var(--panel); border: 1px solid var(--border); border-radius: var(--r); padding: clamp(20px, 3vw, 32px) !important; }
'''
open(OUT + 'brand.css', 'w').write(css)

# ---------- element helpers ----------
def html_widget(h):
    return {"id": rid(), "elType": "widget", "widgetType": "html", "settings": {"html": h}, "elements": [], "isInner": False}

def wrap(elements, inner=False, settings=None):
    st = {"content_width": "full", "css_classes": "cc-wrap", "padding": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": True}, "flex_gap": {"unit": "px", "size": 0, "column": "0", "row": "0"}}
    if settings: st.update(settings)
    return {"id": rid(), "elType": "container", "settings": st, "elements": elements, "isInner": inner}

def page_from_html(h):
    # one container + html widget per top-level block, so Matteo can find sections in Elementor
    blocks = re.split(r'\n(?=<(?:div class="hero|section)[ >])', '\n' + h)
    blocks = [b.strip() for b in blocks if b.strip()]
    return [wrap([html_widget(b)]) for b in blocks]

pages = {}
pages[10] = page_from_html(main_of('index.html'))
pages[271] = page_from_html(main_of('about.html'))
pages[564] = page_from_html(main_of('terms.html'))
pages[724] = page_from_html(main_of('privacy.html'))  # Privacy Policy (created 15 Nov 2026)

# contact: real Elementor form
cm = main_of('contact.html')
form_panel = between(cm, '<div class="panel">', '</form>\n    </div>')
i0=cm.index('<div class="panel info">'); i1=cm.index('</section>', i0); seg=cm[i0:i1]; seg=seg[:seg.rstrip().rindex('</div>')].rstrip(); seg=seg[:seg.rindex('</div>')+6]; info_panel=seg
hero = cm[:cm.index('<section')]
rest = cm[cm.index('</section>') + len('</section>'):]
orig = json.loads(json.load(open(S + 'stg/backup/page-461.json'))['meta']['_elementor_data'])
form = copy.deepcopy(orig[0]['elements'][2]['elements'][0])
st = form['settings']
for k in list(st):
    if (k.startswith(('button_', 'field_', 'label_', 'html_', 'mark_required_color', 'column_gap', 'row_gap', 'message_', 'success_message_color', 'error_message_color', 'inline_message_color')) and k not in ('button_text', 'button_width', 'button_size', 'button_align')):
        del st[k]
for k in list(st):
    if k.startswith(('_margin', '_element_width', '_element_custom_width', '_flex_size', '_z_index', '_padding', '_position', '_offset')): del st[k]
st['button_text'] = 'Send >'   # same as the Coaching form
st['button_width'] = '100'
st['button_align'] = 'start'
st['_css_classes'] = 'cc-form'
for fld in st['form_fields']:
    fld['width'] = '100'; fld['required'] = 'true'
    if fld.get('custom_id') == 'message': fld['rows'] = 4
    # same as Coaching: no visible labels, a * in each placeholder so every field is clearly compulsory
    if fld.get('placeholder') and not fld['placeholder'].endswith('*'): fld['placeholder'] += ' *'
_ph = {'custom_id': 'phone', 'field_type': 'tel', 'required': 'true', 'field_label': 'Phone', 'placeholder': 'Phone (with country code) *', 'width': '100', '_id': 'c1ph0ne'}
_ix = [i for i, f in enumerate(st['form_fields']) if f.get('custom_id') == 'email'][0]
if not any(f.get('custom_id') == 'phone' for f in st['form_fields']): st['form_fields'].insert(_ix + 1, _ph)
st['mark_required'] = 'yes'
for k in list(st):
    if isinstance(st[k], str) and 'staging.cigalacycling.com' in st[k]:
        st[k] = st[k].replace('email@staging.cigalacycling.com', 'noreply@cigalacycling.com').replace('info@staging.cigalacycling.com', 'info@cigalacycling.com').replace('staging.cigalacycling.com', 'cigalacycling.com')
st['show_labels'] = ''   # labels hidden, like Coaching (screen readers still get them)
formcol = wrap([form], inner=True, settings={"content_width": "full", "css_classes": "cc-formcol", "width": {"unit": "%", "size": 58}, "width_mobile": {"unit": "%", "size": 100}, "padding": {"unit": "px", "top": "24", "right": "24", "bottom": "24", "left": "24", "isLinked": True}})
infocol = wrap([html_widget(info_panel)], inner=True, settings={"width": {"unit": "%", "size": 42}, "width_mobile": {"unit": "%", "size": 100}})
grid = {"id": rid(), "elType": "container", "settings": {"content_width": "boxed", "boxed_width": {"unit": "px", "size": 1200}, "flex_direction": "row", "flex_direction_mobile": "column", "flex_gap": {"unit": "px", "size": 16, "column": "16", "row": "16"}, "flex_align_items": "flex-start", "padding": {"unit": "px", "top": "40", "right": "16", "bottom": "0", "left": "16", "isLinked": False}}, "elements": [formcol, infocol], "isInner": False}
pages[461] = page_from_html(hero.strip()) + [grid] + page_from_html(rest.strip())

def content_html(els):
    out = []
    def walk(n):
        for e in n:
            if e.get('widgetType') == 'html': out.append(e['settings']['html'])
            walk(e.get('elements', []))
    walk(els); return '\n'.join(out)

for pid, els in pages.items():
    json.dump({"meta": {"_elementor_data": json.dumps(els), "_elementor_edit_mode": "builder"}, "content": content_html(els)}, open(OUT + f'page-{pid}.json', 'w'))

# header / footer templates
idx = read('index.html')
hdr = fix_links(between(idx, '<header class="nav">', '</header>')).replace(' aria-current="page"', '')
ftr = fix_links(between(idx, '<footer>', '</footer>'))
CURJS = """<script>(function(){var p=location.pathname;document.querySelectorAll('.nav a[href]').forEach(function(a){var h=a.getAttribute('href');if(h&&h.charAt(0)==='/'&&!a.classList.contains('btn')&&h===p){a.setAttribute('aria-current','page');}});})();</script>"""
hdr = hdr + CURJS
scripts = json.load(open(S + 'stg/footer-scripts.json'))
ow = [x for x in scripts if 'openwidget' in x.lower()][0]
ck = [x for x in scripts if 'cookieOptions' in x][0]
ck = ck.replace('cookieOptions.btnTxtColor = "#000000"', 'cookieOptions.btnTxtColor = "#ffffff"').replace('cookieOptions.btnColor = "#f1d600"', 'cookieOptions.btnColor = "#009a44"').replace('cookieOptions.popupColor = "#000000"', 'cookieOptions.popupColor = "#0f1011"')
import sys; sys.path.insert(0, S + 'shared/consent'); from render import banner as render_banner
banner = render_banner(ga_id='G-955J6LHQ2P', privacy_url='/privacy-policy/')
ftr = ftr.replace('<a href="/privacy-policy/">Privacy Policy</a>', '<a href="/privacy-policy/">Privacy Policy</a>\n    <a href="#" data-cc-settings>Cookie settings</a>')
assert 'data-cc-settings' in ftr
nlband = open(S + 'wp/nl-band.html').read()
nlpop = open(S + 'wp/nl-popup.html').read()
assert ftr.startswith('<footer>')
ftr = '<footer>\n  ' + nlband + ftr[len('<footer>'):]
parallax = open(S + 'shared/parallax/parallax.html').read()
json.dump({"meta": {"_elementor_data": json.dumps([wrap([html_widget(ftr + parallax), html_widget(banner), html_widget(nlpop)])])}}, open(OUT + 'lib-228.json', 'w'))
json.dump({"meta": {"_elementor_data": json.dumps([wrap([html_widget(hdr)])])}}, open(OUT + 'lib-170.json', 'w'))

# kit settings
kit = json.load(open(S + 'stg/backup/lib-6.json'))['meta']['_elementor_page_settings']
kit = copy.deepcopy(kit)
kit['system_colors'] = [{"_id": "primary", "title": "Primary", "color": "#009A44"}, {"_id": "secondary", "title": "Secondary", "color": "#E10600"}, {"_id": "text", "title": "Text", "color": "#D0D6E0"}, {"_id": "accent", "title": "Accent", "color": "#34C46A"}]
kit['custom_colors'] = [{"_id": "cc" + str(i), "title": t, "color": c} for i, (t, c) in enumerate([("Background", "#08090A"), ("Panel", "#0F1011"), ("Heading", "#F7F8F8"), ("Muted", "#8A8F98"), ("Red text", "#FF3D33"), ("Gravel", "#B9895A"), ("Gold", "#F0BF00"), ("Green hover", "#00B350")])]
kit['system_typography'] = [
  {"_id": "primary", "title": "Primary", "typography_typography": "custom", "typography_font_family": "Anton", "typography_font_weight": "400", "typography_text_transform": "uppercase"},
  {"_id": "secondary", "title": "Secondary", "typography_typography": "custom", "typography_font_family": "Anton", "typography_font_weight": "400", "typography_text_transform": "uppercase"},
  {"_id": "text", "title": "Text", "typography_typography": "custom", "typography_font_family": "Montserrat", "typography_font_weight": "400", "typography_font_size": {"unit": "px", "size": 15, "sizes": []}, "typography_line_height": {"unit": "em", "size": 1.6, "sizes": []}},
  {"_id": "accent", "title": "Accent", "typography_typography": "custom", "typography_font_family": "Montserrat", "typography_font_weight": "600"}]
kit['body_background_background'] = 'classic'
kit['body_background_color'] = '#08090A'
kit['body_color'] = '#D0D6E0'
kit['body_typography_typography'] = 'custom'
kit['body_typography_font_family'] = 'Montserrat'
kit['link_normal_color'] = '#F7F8F8'
kit['link_hover_color'] = '#FFFFFF'
kit['button_background_color'] = '#009A44'
kit['button_text_color'] = '#FFFFFF'
kit['button_hover_background_color'] = '#00B350'
kit['button_border_radius'] = {"unit": "px", "top": "8", "right": "8", "bottom": "8", "left": "8", "isLinked": True}
kit['custom_css'] = css
json.dump({"meta": {"_elementor_page_settings": kit}}, open(OUT + 'lib-6.json', 'w'))
print('built', {k: len(v) for k, v in pages.items()}, 'css', len(css))

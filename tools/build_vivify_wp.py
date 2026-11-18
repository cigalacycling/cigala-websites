"""Push the Vivify preview (vivify/site/*.html, from tools/build_vivify.py) into Marine's WordPress draft as Elementor pages.

  python3 -I tools/build_vivify.py && python3 -I tools/build_vivify_wp.py [file.html ...]

- Each page: Elementor Canvas template (no theme header), one container holding one HTML widget per section:
  CSS + header first, footer last, so Marine can find each section in Elementor.
- Images point at the WebP files already in the media library (vivify/wp-media.json, tools/vivify_media.py).
- Links: x.html -> /x/, index.html -> /, live https://www.vivifysports.com/post/... -> /post/.../ (posts get imported).
- Titles and meta descriptions are set in Yoast separately (tools/vivify_yoast.py). The preview's <head> is not pushed.
State (file -> page id) in vivify/wp-pages.json, so re-running updates the same pages.
"""
import os, re, sys, json, subprocess, random, string
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
V = ROOT + 'vivify/'
SITE = 'https://basic-darkslategray-cod-55.hostingersite.com'
API = SITE + '/wp-json/wp/v2/pages'
LIVE = 'https://www.vivifysports.com'
MEDIA = json.load(open(V + 'wp-media.json'))
STATE = V + 'wp-pages.json'
st = json.load(open(STATE)) if os.path.exists(STATE) else {}
SKIP = {'post-carbohydrate-fueling-endurance-sports.html',   # posts are imported as WordPress posts
        'blog.html'}   # /blog/ lists posts automatically: tools/vivify_blog_wp.py
CSS = open(V + 'site/vivify.css').read() + r"""
/* WordPress / Hello Elementor / Elementor overrides */
.vv-root .e-con,.vv-root .e-con-inner{padding:0!important;gap:0!important;--padding-top:0;--padding-bottom:0}
.elementor-widget:not(:last-child){margin-block-end:0!important}
.elementor-element:has(> header.site),.elementor-element:has(> .elementor-widget-container > header.site){position:sticky;top:0;z-index:50}
body.admin-bar .elementor-element:has(header.site){top:32px}
body{background-color:#0C2226}
.btn:hover,.btn:focus{text-decoration:none}
.btn-primary:hover,.btn-primary:focus{background:var(--aqua-hover);color:var(--on-aqua)}
.filters button:hover,.filters button:focus{background:rgba(25,68,75,.9);color:var(--text)}
.filters button[aria-pressed=true]:hover{background:var(--aqua);color:var(--on-aqua)}
button.btn{border:1px solid transparent}
/* Google reviews (Trustindex) on the dark site */
.greviews .ti-widget .ti-review-item>.ti-inner{border-radius:12px!important}
/* Contact Form 7 (contact page) */
.wpcf7 form.form p{margin:0}
.wpcf7 form.form{padding:36px}
@media (max-width:560px){.wpcf7 form.form{padding:26px 22px}}
/* Elementor's Text Editor widget brings the kit font (Roboto); use the site's */
.vv-root .elementor-widget-text-editor{font-family:Montserrat,system-ui,sans-serif;font-weight:400;color:var(--text-2);font-size:15px;line-height:1.7}
.wpcf7 .wpcf7-form-control-wrap{display:block}
.wpcf7 input.wpcf7-submit{font:600 14px/1 Montserrat,sans-serif;letter-spacing:.04em;text-transform:uppercase;padding:16px 24px;border-radius:8px;border:0;background:var(--aqua);color:var(--on-aqua);cursor:pointer;width:auto}
.wpcf7 input.wpcf7-submit:hover{background:var(--aqua-hover)}
.wpcf7-not-valid-tip{color:#ffb3ad;font-size:13px;margin-top:6px}
.wpcf7 form .wpcf7-response-output{margin:4px 0 0;padding:12px 14px;border-radius:8px;color:var(--text);border-color:var(--border-strong)!important}
.wpcf7 form.sent .wpcf7-response-output{border-color:var(--lime)!important}
.wpcf7-spinner{background-color:var(--aqua)}
"""
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">'

def rid():
    return ''.join(random.choice(string.hexdigits[:16]) for _ in range(7))

def html_widget(h):
    return {"id": rid(), "elType": "widget", "widgetType": "html", "settings": {"html": h}, "elements": [], "isInner": False}

def container(elements):
    return {"id": rid(), "elType": "container", "settings": {"content_width": "full", "css_classes": "vv-root",
            "padding": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": True},
            "flex_gap": {"unit": "px", "size": 0, "column": "0", "row": "0"}}, "elements": elements, "isInner": False}

def slug(f):
    return 'home' if f == 'index.html' else f[:-5]

def fix(h):
    def img(m):
        n = m.group(1)
        assert n in MEDIA, n
        return 'src="' + MEDIA[n]['url'] + '"'
    h = re.sub(r'src="img/([^"]+)"', img, h)
    h = re.sub(r'href="img/([^"]+)"', lambda m: 'href="' + MEDIA[m.group(1)]['url'] + '"', h)
    h = re.sub(r'href="index\.html(#[^"]*)?"', lambda m: 'href="/' + (m.group(1) or '') + '"', h)
    h = re.sub(r'href="post-carbohydrate-fueling-endurance-sports\.html"', 'href="/post/carbohydrate-fueling-endurance-sports/"', h)
    h = re.sub(r'href="([a-z0-9-]+)\.html(#[^"]*)?"', lambda m: f'href="/{m.group(1)}/{m.group(2) or ""}"', h)
    h = re.sub(r'href="' + re.escape(LIVE) + r'/post/([a-z0-9-]+)"', r'href="/post/\1/"', h)
    h = re.sub(r'href="' + re.escape(LIVE) + r'/(recipies|about|contact)"', r'href="/\1/"', h)
    return h

def page_data(f):
    s = open(V + 'site/' + f).read()
    title = re.search(r'<title>(.*?)</title>', s, re.S).group(1)
    ld = ''.join(re.findall(r'<script type="application/ld\+json">.*?</script>', s, re.S))
    body = re.search(r'<body>(.*)</body>', s, re.S).group(1)
    body = fix(body)
    header = re.search(r'<a class="skip".*?</header>', body, re.S).group(0)
    footer = re.search(r'<footer class="site">.*?</footer>', body, re.S).group(0)
    main = re.search(r'<main id="main">(.*)</main>', body, re.S).group(1)
    blocks = re.split(r'\n(?=<(?:section|style|script)[ >])', '\n' + main)
    blocks = [b.strip() for b in blocks if b.strip()]
    first = FONTS + '<style>' + CSS + '</style>' + ld + header + '<main id="main"></main>'
    # main landmark: keep one <main> around content? Elementor wraps widgets, so mark the first section instead
    first = first.replace('<main id="main"></main>', '<span id="main"></span>')
    def widget(b):
        # the contact form is a Contact Form 7 shortcode: the Text Editor widget runs shortcodes, the HTML widget does not
        if '[trustindex' in b or '[contact-form-7' in b:   # Google reviews shortcode: Text Editor widget runs shortcodes
            b = re.sub(r'>\s+<', '><', b.replace('\n', ' '))
            return {"id": rid(), "elType": "widget", "widgetType": "text-editor", "settings": {"editor": b}, "elements": [], "isInner": False}
        if '<form class="form panel"' in b:
            b = re.sub(r'<form class="form panel".*?</form>', '[contact-form-7 id="349" html_class="form panel" title="Contact"]', b, flags=re.S)
            b = re.sub(r'>\s+<', '><', b.replace('\n', ' '))   # one line, so wpautop adds no stray <p>/<br>
            return {"id": rid(), "elType": "widget", "widgetType": "text-editor", "settings": {"editor": b}, "elements": [], "isInner": False}
        return html_widget(b)
    els = [html_widget(first)] + [widget(b) for b in blocks] + [html_widget(footer)]
    return title, [container(els)], '\n'.join([header, main, footer])

def push(f):
    title, els, content = page_data(f)
    name = re.sub(r'\s*\|.*$', '', re.sub(r'&amp;', '&', title)).strip()
    if f == 'index.html': name = 'Home'
    body = {'title': name, 'slug': slug(f), 'status': 'publish', 'template': 'elementor_canvas', 'content': content,
            'meta': {'_elementor_data': json.dumps(els), '_elementor_edit_mode': 'builder', '_elementor_template_type': 'wp-page'}}
    url = API + (f'/{st[f]}' if f in st else '')
    r = subprocess.run(['curl', '-sS', '-m', '120', '-X', 'POST', url, '-H', 'Content-Type: application/json', '--data-binary', '@-'],
                       input=json.dumps(body), capture_output=True, text=True)
    try: j = json.loads(r.stdout)
    except Exception: print('FAIL', f, r.stdout[:300]); return
    if 'id' not in j: print('FAIL', f, j.get('code'), j.get('message')); return
    st[f] = j['id']; json.dump(st, open(STATE, 'w'), indent=1)
    print(j['id'], j['link'], j.get('template'))

if __name__ == '__main__':
    files = sys.argv[1:] or sorted(f for f in os.listdir(V + 'site') if f.endswith('.html') and f not in SKIP)
    for f in files:
        push(f)
    # Elementor's element cache would keep serving the old page
    subprocess.run(['curl', '-sS', '-m', '60', '-X', 'DELETE', SITE + '/wp-json/elementor/v1/cache'], capture_output=True)

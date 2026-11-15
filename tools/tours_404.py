"""Tours 404 page (Elementor template 7275, type error-404) in the new design, with the live wording.
Backup of the original: stg-tours/backup/lib-7275.json.  Usage: python3 -I tools/tours_404.py
"""
import os, sys, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from push_tours_wp import req, B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
M = json.load(open(ROOT + 'stg-tours/media-webp.json'))
img = M['cta']
rid = lambda: ''.join(random.choice('0123456789abcdef') for _ in range(7))
html = f'''<div class="cl cl-page"><div class="hero phero e404">
  <img src="{img['url']}" alt="{img['alt']}">
  <div class="in">
    <div class="pill-eyebrow">Page not found</div>
    <h1>404 — Wrong turn</h1>
    <div class="bar"></div>
    <p class="lede">The road you're looking for doesn't exist, but there are plenty of better ones to explore.</p>
    <div class="ctas"><a class="btn btn-go" href="/trips/">Explore our tours →</a><a class="btn btn-ghost" href="/destinations/">Explore our destinations</a></div>
    <p class="e404-links"><a href="/guides/">Cycling guides</a> · <a href="/trips/private-trips/">Custom tours</a> · <a href="/contact/">Contact us</a></p>
  </div>
</div></div>
<style>
html .cl .e404 {{ min-height: 70vh; display: flex; align-items: center; }}
html .cl .e404 .in {{ padding-block: 120px 80px; width: 100%; }}
html .cl .e404-links {{ margin-top: 22px; font-size: 14px; color: var(--text-2); }}
html .cl .e404-links a {{ color: var(--green-text); text-decoration: none; font-weight: 600; }}
html .cl .e404-links a:hover {{ color: #fff; }}
</style>'''
els = [{"id": rid(), "elType": "container", "settings": {"content_width": "full", "css_classes": "cc-wrap",
        "padding": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": True}},
        "elements": [{"id": rid(), "elType": "widget", "widgetType": "html", "settings": {"html": html}, "elements": [], "isInner": False}], "isInner": False}]
code, r = req(f'{B}/wp/v2/elementor_library/7275', json.dumps({"meta": {"_elementor_data": json.dumps(els), "_elementor_edit_mode": "builder"}}).encode(), 'POST')
print('404 template', code)
code, r = req(f'{B}/elementor/v1/cache', method='DELETE'); print('elementor cache', code)

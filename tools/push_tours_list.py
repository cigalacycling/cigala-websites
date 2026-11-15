"""Create or update a Tours trip-list page on STAGING from stg-tours/out/list-<slug>.json
(made by tools/build_tours_list.py), and set its Rank Math title and description.

Usage: python3 -I tools/push_tours_list.py road-trips
Page IDs are kept in stg-tours/pages.json. Run tools/build_tours_wp.py + push lib-6 for the CSS.
"""
import os, re, sys, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from push_tours_wp import req, B   # staging-only request helper (asserts the host)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
L = 'https://tours.cigalacycling.com'
M = json.load(open(ROOT + 'stg-tours/media-webp.json'))
IDS = ROOT + 'stg-tours/pages.json'
ids = json.load(open(IDS)) if os.path.exists(IDS) else {}

def rid(): return ''.join(random.choice('0123456789abcdef') for _ in range(7))
def widget(h): return {"id": rid(), "elType": "widget", "widgetType": "html", "settings": {"html": h}, "elements": [], "isInner": False}
def wrap(els): return {"id": rid(), "elType": "container", "settings": {"content_width": "full", "css_classes": "cc-wrap", "padding": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": True}, "flex_gap": {"unit": "px", "size": 0, "column": "0", "row": "0"}}, "elements": els, "isInner": False}

IMG = {'img/dest-private-custom-tours.jpg': 'custom', 'img/logo-mdd.png': 'logo-mdd', 'img/logo-lombardia.png': 'logo-lombardia',
       'img/logo-strade.png': 'logo-strade', 'img/logo-algarve.png': 'logo-algarve'}
def fix_img(m):
    tag = m.group(0); src = re.search(r'src="([^"]+)"', tag).group(1)
    key = IMG.get(src) or (src[len('img/cigala-tours-'):-5] if src.startswith('img/cigala-tours-') else None)
    if not key or key not in M: raise SystemExit('no staging image for ' + src)
    tag = tag.replace(f'src="{src}"', f'src="{M[key]["url"]}"')
    if not re.search(r'alt="[^"]+"', tag):   # empty alt -> the alt the image has on the site
        tag = re.sub(r'alt="[^"]*"', 'alt="' + M[key]['alt'].replace('"', '&quot;') + '"', tag)
    return tag

def fix(s):
    s = re.sub(r'<img [^>]*>', fix_img, s)
    s = re.sub(r'href="' + re.escape(L) + r'(/[^"]*)" target="_blank" rel="noopener"', r'href="\1"', s)
    s = re.sub(r'href="' + re.escape(L) + r'(/[^"]*)"', r'href="\1"', s)
    return s

slug = sys.argv[1]
d = json.load(open(ROOT + f'stg-tours/out/list-{slug}.json'))
main = fix(d['main'])
blocks = [b.strip() for b in re.split(r'\n(?=<(?:div class="hero|section)[ >])', '\n' + main) if b.strip()]
els = [wrap([widget('<div class="cl cl-page">' + b + '</div>')]) for b in blocks]
body = {"title": d['title'], "slug": d['slug'], "parent": d['parent'], "status": "publish", "template": "",
        "content": '\n'.join('<div class="cl cl-page">' + b + '</div>' for b in blocks),
        "meta": {"_elementor_data": json.dumps(els), "_elementor_edit_mode": "builder", "_elementor_template_type": "wp-page"}}
if slug not in ids:   # look for an existing page first, so a re-run never makes a duplicate
    code, r = req(f'{B}/wp/v2/pages?slug={d["slug"]}&status=publish,draft&context=edit&_fields=id,parent')
    found = [p for p in json.loads(r) if p['parent'] == d['parent']] if code == 200 else []
    if found: ids[slug] = found[0]['id']
if slug in ids:
    code, r = req(f'{B}/wp/v2/pages/{ids[slug]}', json.dumps(body).encode(), 'POST')
else:
    code, r = req(f'{B}/wp/v2/pages', json.dumps(body).encode(), 'POST')
    if code == 201: ids[slug] = json.loads(r)['id']
json.dump(ids, open(IDS, 'w'), indent=1)
print('page', slug, code, ids.get(slug), '' if code in (200, 201) else r[:300])
pid = ids[slug]
code, r = req(f'{B}/rankmath/v1/updateMeta', json.dumps({"objectType": "post", "objectID": pid, "meta": {"rank_math_title": d['seo_title'], "rank_math_description": d['seo_description']}}).encode(), 'POST')
print('rank math meta', code, r[:200])
code, r = req(f'{B}/elementor/v1/cache', method='DELETE'); print('elementor cache', code)

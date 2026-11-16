"""Guide categories (Matteo 16 Nov: "can we have the guides divided in categories"). Tags, not categories: the guide URLs
are /guides/<slug>/ (category in the permalink), so a new category could change URLs. Tags never touch URLs.
The Guides page filter (Elementor taxonomy filter in build_tours_guides.py) shows them. STAGING only.
    python3 -I tools/tours_guide_tags.py
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from push_tours_wp import req, B
TAGS = {   # tag name -> guides (a guide can be in more than one)
 'Destinations': 'cycling-lake-como lake-garda-cycling-secret croatia-adriatic-coast-cycling-guide ireland-cycling-guide cycling-girona-inside-the-pro-pelotons-favorite-town '
                 'mallorca-cycling-guide calpe-cycling-guide algarve-cycling-guide swiss-alps-cycling-guide slovenia-cycling-guide puglia-cycling-guide sicily-cycling-guide '
                 'sardinia-cycling-guide corsica-cycling-guide greece-cycling-guide canary-islands-cycling-guide azores-cycling-guide austrian-alps-cycling-guide '
                 'cycling-in-italy-complete-guide cycling-in-france-complete-guide cycling-in-spain-complete-guide cycling-flanders italy-coast-to-coast-a-cycling-traverse raid-alps-custom-tour',
 'Climbs': 'stelvio-pass-cycling-guide col-du-galibier-cycling-guide cycling-in-the-pyrenees-best-climbs alpe-dhuez-cycling-guide best-time-to-ride-dolomites',
 'Events & Gran Fondos': 'strade-bianche-guide cycling-flanders cycling-lake-como',
 'Gravel': 'gravel-cycling-cyprus the-tuscany-gravel-tour-riding-the-tuscany-trail what-to-pack-gravel-cycling-tour road-vs-gravel-bike-holiday strade-bianche-guide',
 'Planning & kit': 'what-to-pack-cycling-holiday what-to-pack-gravel-cycling-tour how-to-prepare-cycling-holiday fitness-levels-which-tour road-vs-gravel-bike-holiday best-time-to-ride-dolomites',
}
SLUG = {'Events & Gran Fondos': 'events', 'Planning & kit': 'planning'}
H = json.loads(req(B + '/wp/v2/tags?per_page=100&_fields=id,name,slug')[1])
ids = {}
for name in TAGS:
    t = next((x for x in H if x['name'].replace('&amp;', '&') == name), None)
    if not t:
        c, r = req(B + '/wp/v2/tags', data=json.dumps({'name': name, 'slug': SLUG.get(name, name.lower())}).encode(), method='POST'); t = json.loads(r)
    ids[name] = t['id']
posts = json.loads(req(B + '/wp/v2/posts?per_page=100&_fields=id,slug,tags')[1])
want = {}
for name, sl in TAGS.items():
    for s in sl.split(): want.setdefault(s, set()).add(ids[name])
for p in posts:
    if p['slug'] not in want: print('no tag:', p['slug']); continue
    if set(p['tags']) != want[p['slug']]:
        c, _ = req(B + f'/wp/v2/posts/{p["id"]}', data=json.dumps({'tags': sorted(want[p['slug']])}).encode(), method='POST'); print(p['slug'], c)
print(ids)

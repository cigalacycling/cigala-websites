"""Single post template 4028 in the Tours guide style (Matteo 16 Nov 2026), Coaching STAGING only:
- the author line (ACF author_name heading 2a7c116) moves above the title and gets the class cc-post-author (red eyebrow, "By …");
- the excerpt and the post content go into one inner container, cc-post-body (the boxed panel; CSS in tools/build_coaching_wp.py).
Backup before the change: stg-coaching/backup/lib-4028-before-tours-style.json. Safe to re-run (does nothing twice).
  python3 -I tools/coaching_post_template.py
"""
import json, os, random, subprocess
HOST = 'staging.coaching.cigalacycling.com'; B = f'https://{HOST}/wp-json'
MAIN, AUTHOR, TITLE, DIVIDER, IMAGE, EXCERPT, CONTENT = '47a5de1', '2a7c116', 'c5abdfb', '3dde2cd', 'e443361', 'c9d2efc', '5065624'
def req(url, body=None, method='GET'):
    assert url.startswith(f'https://{HOST}/')
    a = ['curl', '-sS', '-m', '90', '-X', method, url]
    if body is not None: a += ['-H', 'Content-Type: application/json', '--data-binary', json.dumps(body)]
    return json.loads(subprocess.run(a, capture_output=True, text=True).stdout or 'null')
ed = json.loads(req(f'{B}/wp/v2/elementor_library/4028?context=edit&_fields=meta')['meta']['_elementor_data'])
main = next(x for x in ed if x['id'] == MAIN)
kids = {x['id']: x for x in main['elements']}
if any(x.get('settings', {}).get('css_classes', '').endswith('cc-post-body') for x in main['elements']):
    print('already done'); raise SystemExit
assert all(k in kids for k in (AUTHOR, TITLE, DIVIDER, IMAGE, EXCERPT, CONTENT)), list(kids)
kids[AUTHOR]['settings']['_css_classes'] = 'cc-post-author'
body = {'id': ''.join(random.choice('0123456789abcdef') for _ in range(7)), 'elType': 'container', 'isInner': True, 'elements': [kids[EXCERPT], kids[CONTENT]],
        'settings': {'content_width': 'full', 'flex_direction': 'column', 'css_classes': 'cc-post-body',
                     'flex_gap': {'unit': 'px', 'size': 0, 'column': '0', 'row': '0'}}}
rest = [x for x in main['elements'] if x['id'] not in (AUTHOR, TITLE, DIVIDER, IMAGE, EXCERPT, CONTENT)]
main['elements'] = [kids[AUTHOR], kids[TITLE], kids[DIVIDER], kids[IMAGE], body] + rest
r = req(f'{B}/wp/v2/elementor_library/4028?_fields=id', {'meta': {'_elementor_data': json.dumps(ed)}}, 'POST')
print('template 4028 updated', r)

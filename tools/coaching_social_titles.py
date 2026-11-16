"""Coaching STAGING, Matteo 16 Nov 2026:
1. "2026" -> "2027" in the SEO title and social title of /blog/cycling-coach-ireland/ (only the year changes).
2. Nine posts were copies of that post and kept its social title, description and image (Yoast "opengraph"/"twitter" fields),
   so a shared link showed "Cycling Coach Ireland… (2026 Guide)". Those fields are cleared on the nine, so each post's own
   SEO title, meta description and featured image are used when shared. Google results don't change.
Yoast's own fields aren't in the REST API, so a temporary snippet exposes them, then it is deleted (Code Snippets stays on).
Old values: stg-coaching/backup/social-fields-before.json.
  python3 -I tools/coaching_social_titles.py
"""
import json, os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
HOST = 'staging.coaching.cigalacycling.com'
B = f'https://{HOST}/wp-json'
KEYS = ['_yoast_wpseo_title', '_yoast_wpseo_metadesc', '_yoast_wpseo_opengraph-title', '_yoast_wpseo_opengraph-description', '_yoast_wpseo_opengraph-image',
        '_yoast_wpseo_opengraph-image-id', '_yoast_wpseo_twitter-title', '_yoast_wpseo_twitter-description', '_yoast_wpseo_twitter-image', '_yoast_wpseo_twitter-image-id']
SOCIAL = KEYS[2:]
MAIN = 5797
COPIES = {6284: 'ai-cycling-coaching', 6239: 'strade-bianche', 6234: 'dolomites', 6230: 'whistler', 6226: 'belgian-waffle-ride', 6224: 'w200',
          6217: 'fred-whitton', 6087: 'lactate-gels', 5952: 'what-is-ftp'}
def req(url, body=None, method='GET'):
    assert url.startswith(f'https://{HOST}/')
    a = ['curl', '-sS', '-m', '90', '-X', method, url]
    if body is not None: a += ['-H', 'Content-Type: application/json', '--data-binary', json.dumps(body)]
    return json.loads(subprocess.run(a, capture_output=True, text=True).stdout or 'null')
code = ("add_action('init', function () { foreach (" + repr(KEYS).replace('[', 'array(').replace(']', ')') + " as $k) register_post_meta('post', $k, "
        "array('type' => 'string', 'single' => true, 'show_in_rest' => true, 'auth_callback' => function () { return current_user_can('edit_posts'); })); });")
tmp = req(f'{B}/code-snippets/v1/snippets', {'name': 'TEMP: Yoast social fields in REST (Claude)', 'scope': 'global', 'active': True, 'code': code}, 'POST')
try:
    before = {}
    for pid in [MAIN] + list(COPIES):
        before[pid] = {k: v for k, v in req(f'{B}/wp/v2/posts/{pid}?context=edit&_fields=meta')['meta'].items() if k in KEYS}
    if not os.path.exists(ROOT + 'stg-coaching/backup/social-fields-before.json'):   # keep the first (original) backup
        json.dump(before, open(ROOT + 'stg-coaching/backup/social-fields-before.json', 'w'), indent=1, ensure_ascii=False)
    m = before[MAIN]
    upd = {k: m[k].replace('2026', '2027') for k in ('_yoast_wpseo_title', '_yoast_wpseo_metadesc', '_yoast_wpseo_opengraph-title', '_yoast_wpseo_opengraph-description', '_yoast_wpseo_twitter-title', '_yoast_wpseo_twitter-description') if m.get(k) and '2026' in m[k]}   # text only: image URLs contain /uploads/2026/
    print('main post, changing:', upd)
    if upd: req(f'{B}/wp/v2/posts/{MAIN}?_fields=id', {'meta': upd}, 'POST')
    for pid, name in COPIES.items():
        clear = {k: '' for k in SOCIAL if before[pid].get(k)}
        print(name, 'clearing', sorted(clear))
        if clear: req(f'{B}/wp/v2/posts/{pid}?_fields=id', {'meta': clear}, 'POST')
finally:
    print('temp snippet deleted', req(f'{B}/code-snippets/v1/snippets/{tmp["id"]}', None, 'DELETE') is not None)

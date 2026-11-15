"""Matteo 15 Nov 2026 ("vivify articles yes"): Marine's articles copied from vivifysports.com point their canonical
to the original article, so Google doesn't see duplicate content. Staging only.
Yoast's canonical field isn't in the REST API, so a temporary Code Snippets snippet registers it, the 7 canonicals are
written, then the snippet is deleted and Code Snippets is switched off again (the values stay in post meta).
  python3 -I tools/coaching_vivify_canonical.py <snippet-id>
"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
B = 'https://staging.coaching.cigalacycling.com/wp-json'
def req(url, body=None, method='GET'):
    a = ['curl', '-sS', '-m', '60', '-X', method, url]
    if body is not None: a += ['-H', 'Content-Type: application/json', '--data-binary', json.dumps(body)]
    r = subprocess.run(a, capture_output=True, text=True); return json.loads(r.stdout or 'null')
P = json.load(open(ROOT + 'stg-coaching/vivify-posts.json'))['posts']
for slug, p in P.items():
    r = req(f'{B}/wp/v2/posts/{p["id"]}?_fields=id,meta', {'meta': {'_yoast_wpseo_canonical': p['source']}}, 'POST')
    print(slug, '->', (r.get('meta') or {}).get('_yoast_wpseo_canonical'))
if len(sys.argv) > 1:
    print('delete snippet', req(f'{B}/code-snippets/v1/snippets/{sys.argv[1]}', None, 'DELETE') is not None)
    print(req(f'{B}/wp/v2/plugins/code-snippets/code-snippets?_fields=plugin,status', {'status': 'inactive'}, 'POST'))
for slug, p in P.items():
    h = req(f'{B}/wp/v2/posts/{p["id"]}?_fields=yoast_head_json')
    print('check', slug, (h.get('yoast_head_json') or {}).get('canonical'))

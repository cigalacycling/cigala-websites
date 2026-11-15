"""Push stg-coaching/out/*.json to Coaching STAGING only, then clear the Elementor cache.

Usage: python3 -I tools/push_coaching_wp.py [lib-6 lib-170 lib-228 page-2924 page-3338 snippet-head ...]
With no arguments it pushes every file in stg-coaching/out/.
snippet-head is created once (Elementor custom code); its ID is then kept in stg-coaching/snippet-head-id.txt.
The proxy adds the staging application password; there are no secrets here.
"""
import os, sys, json, time, ssl, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
HOST = 'staging.coaching.cigalacycling.com'   # never the live host
B = f'https://{HOST}/wp-json'
OUT = ROOT + 'stg-coaching/out/'
SNIP = ROOT + 'stg-coaching/snippet-head-id.txt'
ctx = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')

def req(url, data=None, method='GET'):
    assert url.startswith(f'https://{HOST}/')
    for i in range(30):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, data=data, method=method, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}), context=ctx, timeout=180)
            return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code in (502, 503, 504): time.sleep(3); continue
            return e.code, e.read()
        except Exception:
            time.sleep(3)
    raise RuntimeError('unreachable ' + url)

if __name__ == '__main__':
    names = sys.argv[1:] or sorted(f[:-5] for f in os.listdir(OUT) if f.endswith('.json'))
    for n in names:
        body = open(OUT + f'{n}.json', 'rb').read()
        if n == 'snippet-head':
            if os.path.exists(SNIP):
                code, r = req(f'{B}/wp/v2/elementor_snippet/{open(SNIP).read().strip()}', body, 'POST')
            else:
                code, r = req(f'{B}/wp/v2/elementor_snippet', body, 'POST')
                if code in (200, 201): open(SNIP, 'w').write(str(json.loads(r)['id']))
        elif n == 'page-privacy':   # new page: created once, then updated; ID kept in stg-coaching/page-privacy-id.txt
            f = ROOT + 'stg-coaching/page-privacy-id.txt'
            if os.path.exists(f):
                code, r = req(f'{B}/wp/v2/pages/{open(f).read().strip()}', body, 'POST')
            else:
                code, r = req(f'{B}/wp/v2/pages', body, 'POST')
                if code in (200, 201): open(f, 'w').write(str(json.loads(r)['id']))
        elif n.startswith('page-new-'):   # new pages: created once, then updated; IDs in stg-coaching/new-pages.json
            f = ROOT + 'stg-coaching/new-pages.json'; ids = json.load(open(f)) if os.path.exists(f) else {}
            d = json.loads(body); parent = d.pop('parent_slug', None)
            if parent: d['parent'] = ids[parent]   # the parent is pushed first
            body = json.dumps(d).encode()
            if d['slug'] in ids:
                code, r = req(f'{B}/wp/v2/pages/{ids[d["slug"]]}', body, 'POST')
            else:
                code, r = req(f'{B}/wp/v2/pages', body, 'POST')
                if code in (200, 201): ids[d['slug']] = json.loads(r)['id']; json.dump(ids, open(f, 'w'), indent=1)
        else:
            kind, pid = n.split('-', 1)
            code, r = req(f'{B}/wp/v2/{ {"lib": "elementor_library", "page": "pages"}[kind] }/{pid}', body, 'POST')
        print(n, code, '' if code in (200, 201) else r[:300])
    code, _ = req(f'{B}/elementor/v1/cache', method='DELETE')
    print('elementor cache', code)

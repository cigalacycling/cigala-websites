"""Push stg-tours/out/*.json to Tours STAGING only, then clear the Elementor cache.

Usage: python3 -I tools/push_tours_wp.py [lib-6 lib-170 lib-228 page-5212 ...]
With no arguments it pushes every file in stg-tours/out/.
The proxy adds the staging application password; there are no secrets here.
"""
import os, sys, json, time, ssl, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
HOST = 'staging.tours.cigalacycling.com'   # never the live host
B = f'https://{HOST}/wp-json'
ctx = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')

def req(url, data=None, method='GET'):
    assert url.startswith(f'https://{HOST}/')
    for i in range(30):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, data=data, method=method, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}), context=ctx, timeout=120)
            return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code in (502, 503, 504): time.sleep(3); continue
            return e.code, e.read()
        except Exception:
            time.sleep(3)   # proxy could not connect yet (DNS still spreading)
    raise RuntimeError('unreachable ' + url)

names = sys.argv[1:] or sorted(f[:-5] for f in os.listdir(ROOT + 'stg-tours/out') if f.endswith('.json'))
for n in names:
    kind, pid = n.split('-', 1)
    path = {'lib': 'elementor_library', 'page': 'pages'}[kind]
    code, body = req(f'{B}/wp/v2/{path}/{pid}', open(ROOT + f'stg-tours/out/{n}.json', 'rb').read(), 'POST')
    print(n, code, '' if code == 200 else body[:300])
code, body = req(f'{B}/elementor/v1/cache', method='DELETE')
print('elementor cache', code)

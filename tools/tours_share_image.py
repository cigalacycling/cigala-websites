"""Upload the Tours 1200x630 social share image to Tours STAGING media
(brand-assets/share/cigala-cycling-tours-share.jpg, rendered from brand-assets/share/tours-share.html)
and record its id in stg-tours/media-webp.json as 'share'.
JPG on purpose: some apps (WhatsApp, LinkedIn, older Facebook scrapers) don't show WebP link previews.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from push_tours_wp import B, ctx
import time, urllib.request, urllib.error

def req(url, data=None, headers=None, method=None):
    for i in range(20):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers, method=method), context=ctx, timeout=120).read()
        except urllib.error.HTTPError as e:
            if e.code in (502, 503, 504): time.sleep(3); continue
            raise RuntimeError(f'{e.code} {url}: {e.read()[:300]}')
        except Exception:
            time.sleep(3)
    raise RuntimeError('unreachable ' + url)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
MAP = ROOT + 'stg-tours/media-webp.json'
FN = 'cigala-cycling-tours-share.jpg'
ALT = 'Cigala Cycling Tours riders celebrating with their bikes on the coast in Cyprus: guided cycling tours and holidays across Europe'
m = json.load(open(MAP))
if 'share' not in m:
    raw = open(ROOT + 'brand-assets/share/' + FN, 'rb').read()
    r = json.loads(req(B + '/wp/v2/media', data=raw, method='POST', headers={'Content-Type': 'image/jpeg', 'Content-Disposition': f'attachment; filename="{FN}"', 'User-Agent': 'Mozilla/5.0'}))
    req(B + f'/wp/v2/media/{r["id"]}', data=json.dumps({'alt_text': ALT, 'title': 'Cigala Cycling Tours share image'}).encode(), method='POST', headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    m['share'] = {'id': r['id'], 'url': r['source_url'], 'alt': ALT}
    json.dump(m, open(MAP, 'w'), indent=1)
print(m['share'])

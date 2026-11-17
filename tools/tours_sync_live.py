"""Copy Tours pages from STAGING to LIVE after go-live (Matteo 16 Nov: fixes on staging first, then the same on live).
For each page id given: back up the live page (live/backup/tours/<type>-<id>-<time>.json), upload to live any staging
media file the page uses that live doesn't have, rewrite staging URLs to live, write _elementor_data, clear Elementor's cache.
    python3 -I tools/tours_sync_live.py pages:2597 [elementor_library:6 ...]
"""
import sys, json, re, time, urllib.request, urllib.error, urllib.parse, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
S, L = 'https://staging.tours.cigalacycling.com', 'https://tours.cigalacycling.com'
H = {'User-Agent': 'Mozilla/5.0'}
def req(url, data=None, method=None, headers=None):
    for i in range(10):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, data=data, method=method, headers={**H, **(headers or {})}), timeout=180)
            return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code in (502, 503, 504): time.sleep(3); continue
            return e.code, e.read()
def jget(url): return json.loads(req(url)[1])
def exists(u): return req(urllib.parse.quote(u, safe=':/?=&%'), method='HEAD')[0] == 200
for arg in sys.argv[1:]:
    t, pid = arg.split(':')
    sd = jget(f'{S}/wp-json/wp/v2/{t}/{pid}?context=edit&_fields=id,meta')['meta']
    ld = jget(f'{L}/wp-json/wp/v2/{t}/{pid}?context=edit&_fields=id,meta,modified_gmt')
    bk = ROOT + f'live/backup/tours/{t}-{pid}-{time.strftime("%Y%m%d-%H%M%S")}.json'; json.dump(ld, open(bk, 'w'))
    data = sd.get('_elementor_data') or ''
    ps = sd.get('_elementor_page_settings')   # the kit (elementor_library 6) keeps the site CSS here
    pjs = json.dumps(ps) if ps else ''
    data_all = data + pjs
    urls = sorted(set(re.findall(r'https:\\?/\\?/staging\.tours\.cigalacycling\.com\\?/wp-content\\?/uploads\\?/[^"\'\s\\)]+', data_all)))
    for u in urls:
        su = u.replace('\\/', '/'); lu = su.replace(S, L)
        if exists(lu): continue
        code, raw = req(urllib.parse.quote(su, safe=':/?=&%'))
        fn = su.rsplit('/', 1)[1]; ct = {'webp': 'image/webp', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'svg': 'image/svg+xml'}.get(fn.rsplit('.', 1)[-1].lower(), 'application/octet-stream')
        c2, r2 = req(L + '/wp-json/wp/v2/media', data=raw, method='POST', headers={'Content-Type': ct, 'Content-Disposition': f'attachment; filename="{fn}"'})
        new = json.loads(r2)['source_url']
        if new != lu: data = data.replace(u, new.replace('/', '\\/') if '\\/' in u else new); pjs = pjs.replace(u, new.replace('/', '\\/') if '\\/' in u else new)
        print('  media', fn, c2, '' if new == lu else '-> ' + new)
    data = data.replace(S.replace('/', '\\/'), L.replace('/', '\\/')).replace(S, L)
    pjs = pjs.replace(S.replace('/', '\\/'), L.replace('/', '\\/')).replace(S, L)
    meta = {}
    if data: meta['_elementor_data'] = data
    if pjs: meta['_elementor_page_settings'] = json.loads(pjs)
    c, r = req(f'{L}/wp-json/wp/v2/{t}/{pid}', data=json.dumps({'meta': meta}).encode(), method='POST', headers={'Content-Type': 'application/json'})
    print(arg, c, 'backup', bk.replace(ROOT, ''))
c, r = req(L + '/wp-json/elementor/v1/cache', method='DELETE'); print('elementor cache', c)

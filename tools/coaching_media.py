"""Upload every image used by the Coaching previews (coachingpages/*.html) to Coaching STAGING.

The preview images are already WebP q90 from the largest originals (tools/extract_site.py, tools/build_coaching_*.py),
so they are uploaded as they are, with the alt text the preview gives them.
Writes stg-coaching/media-webp.json  {preview path: {id, url, alt}}. Re-running skips files already uploaded.
The proxy adds the staging application password; there are no secrets here.
"""
import os, re, sys, json, time, ssl, html, glob, urllib.request, urllib.error, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
HOST = 'staging.coaching.cigalacycling.com'   # never the live host
B = f'https://{HOST}/wp-json/wp/v2'
MAP = ROOT + 'stg-coaching/media-webp.json'
ctx = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')

def req(url, data=None, headers=None, method=None, tries=20):
    assert url.startswith(f'https://{HOST}/')
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers or {'User-Agent': 'Mozilla/5.0'}, method=method), context=ctx, timeout=180)
            return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (502, 503, 504): time.sleep(3); continue
            raise RuntimeError(f'{e.code} {url}: {e.read()[:300]}')
        except Exception:
            time.sleep(3)
    raise RuntimeError('unreachable ' + url)

def used_images(pages):
    """preview src -> alt, for every <img> in the given preview pages"""
    out = {}
    for p in pages:
        t = open(ROOT + 'coachingpages/' + p).read()
        for tag in re.findall(r'<img\b[^>]*>', t):
            src = re.search(r'src="([^"]+)"', tag).group(1); alt = html.unescape(re.search(r'alt="([^"]*)"', tag).group(1))
            if src.startswith(('http', 'data:')): continue
            out.setdefault(src, alt)
        # full-size images opened by a link around a thumbnail (Athlete Hub examples, 17 Nov): alt from the thumbnail
        for href, inner in re.findall(r'<a\b[^>]*href="(img/[^"]+\.webp)"[^>]*>(.*?)</a>', t, re.S):
            m = re.search(r'alt="([^"]*)"', inner)
            if m: out.setdefault(href, html.unescape(m.group(1)))
    return out

def local(src):
    return ROOT + 'coachingpages/' + src if not src.startswith('../') else ROOT + src[3:]

def upload(pages):
    done = json.load(open(MAP)) if os.path.exists(MAP) else {}
    todo = {s: a for s, a in used_images(pages).items() if s not in done}
    for n, (src, alt) in enumerate(todo.items(), 1):
        path = local(src); assert os.path.exists(path), path
        ext = path.rsplit('.', 1)[1].lower()
        ctype = {'webp': 'image/webp', 'svg': 'image/svg+xml', 'png': 'image/png', 'jpg': 'image/jpeg'}[ext]
        if ext == 'svg': continue   # the topo tile is inlined in the kit CSS, not uploaded
        fn = 'cigala-coaching-' + os.path.basename(path).replace('2026_06_', '').replace('2026_07_', '').replace('2026_08_', '').replace('2026_10_', '')
        r = json.loads(req(B + '/media', data=open(path, 'rb').read(), method='POST',
                           headers={'Content-Type': ctype, 'Content-Disposition': f'attachment; filename="{fn}"', 'User-Agent': 'Mozilla/5.0'}))
        req(B + f'/media/{r["id"]}', data=json.dumps({'alt_text': alt}).encode(), method='POST',
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
        done[src] = {'id': r['id'], 'url': r['source_url'], 'alt': alt}
        json.dump(done, open(MAP, 'w'), indent=1, ensure_ascii=False)
        print(f'{n}/{len(todo)}', src, '->', r['id'])
    print(len(done), 'images in', MAP)
    return done

if __name__ == '__main__':
    upload(sys.argv[1:] or [os.path.basename(p) for p in sorted(glob.glob(ROOT + 'coachingpages/*.html'))])

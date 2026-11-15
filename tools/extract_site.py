# Pulls the content of a live site into <out>/ for the redesign (read-only, live is never changed).
#   python3 -I tools/extract_site.py coaching.cigalacycling.com coaching
# Needs <out>/baseline.json from tools/crawl.py. Writes:
#   <out>/html/<slug>.html   raw page HTML      <out>/text/<slug>.txt  headings, copy, links, images (tools/extract.py)
#   <out>/css/post-*.css     Elementor page CSS (background images)
#   <out>/img/               originals (gitignored, re-downloadable)   <out>/webp/  WebP q90, long edge max 2560
#   <out>/images.json        every image: original URL, alt text, background or not, pages using it
import sys, os, re, json, glob, subprocess
from PIL import Image, ImageOps
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); host, out = sys.argv[1], os.path.join(R, sys.argv[2])
for d in ('html', 'text', 'css', 'img', 'webp'): os.makedirs(f'{out}/{d}', exist_ok=True)
get = lambda u, f: subprocess.run(['curl', '-sS', '-m', '90', '-A', 'Mozilla/5.0 (content-extract)', '-w', '%{http_code}', '-o', f, u], capture_output=True, text=True).stdout.strip()
orig = lambda u: re.sub(r'-\d+x\d+(?=\.\w+$)', '', u.split('?')[0])
pages = [r for r in json.load(open(f'{out}/baseline.json')) if r['status'] == 200]
imgs, css = {}, {}
def add(u, slugs, alt=None, bg=False):
    e = imgs.setdefault(orig(u), {'alt': set(), 'pages': set(), 'bg': False}); e['pages'] |= set(slugs); e['bg'] |= bg
    if alt is not None: e['alt'].add(alt)
for r in pages:
    slug = r['url'].split(host + '/')[1].strip('/').replace('/', '_') or 'home'; h = f'{out}/html/{slug}.html'
    get(r['url'], h)
    open(f'{out}/text/{slug}.txt', 'w').write(subprocess.run(['python3', '-I', os.path.join(R, 'tools/extract.py'), h], capture_output=True, text=True).stdout)
    t = open(h, errors='replace').read()
    for tag in re.findall(r'<img\b[^>]*>', t):
        s = re.search(r'\s(?:data-src|src)="([^"]+)"', tag); a = re.search(r'\salt="([^"]*)"', tag)
        if s and not s.group(1).startswith('data:'): add(s.group(1), [slug], a.group(1) if a else None)
    for m in re.finditer(r'url\((["\']?)(https?://[^)"\']+\.(?:jpe?g|png|webp|gif|svg))\1\)', t): add(m.group(2), [slug], bg=True)
    for c in re.findall(rf'href=["\'](https://{re.escape(host)}/wp-content/uploads/elementor/css/post-\d+\.css)', t): css.setdefault(c, set()).add(slug)
for c, slugs in css.items():
    f = f'{out}/css/' + c.rsplit('/', 1)[1]; get(c, f)
    for u in re.findall(r'url\(["\']?([^)"\']+\.(?:jpe?g|png|webp|gif|svg))', open(f, errors='replace').read()):
        u = 'https:' + u if u.startswith('//') else u
        if u.startswith('http'): add(u, slugs, bg=True)
man = []
for u, e in sorted(imgs.items()):
    name = u.split('/wp-content/uploads/')[-1].replace('/', '_'); f = f'{out}/img/{name}'
    o = {'file': name, 'url': u, 'status': int(get(u, f) or 0), 'alt': sorted(e['alt']), 'background': e['bg'], 'pages': sorted(e['pages'])}
    if o['status'] != 200:
        if os.path.exists(f): os.remove(f)
        o['file'] = o['webp'] = None
    elif not name.lower().endswith('.svg'):
        im = ImageOps.exif_transpose(Image.open(f)); o['original_size'] = list(im.size)
        if im.mode not in ('RGB', 'RGBA'): im = im.convert('RGBA' if im.mode in ('LA', 'P') or 'transparency' in im.info else 'RGB')
        if max(im.size) > 2560: im.thumbnail((2560, 2560), Image.LANCZOS)
        o['webp'] = name.rsplit('.', 1)[0] + ('' if name.lower().endswith(('.jpg', '.jpeg')) else '-' + name.rsplit('.', 1)[1].lower()) + '.webp'; o['webp_size'] = list(im.size)
        im.save(f'{out}/webp/' + o['webp'], 'WEBP', quality=90, method=6)
    man.append(o)
json.dump(man, open(f'{out}/images.json', 'w'), indent=1, ensure_ascii=False)
print(len(pages), 'pages,', len(man), 'images,', sum(o['status'] != 200 for o in man), 'failed')

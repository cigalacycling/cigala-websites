"""Put Marine's approved e-book on her WordPress site, with a hidden download page for buyers.

  python3 tools/vivify_ebook.py && python3 tools/vivify_ebook_upload.py

- Uploads vivify/ebook/Breakfasts-to-Ignite-Your-Potential.pdf to the media library. The file name carries a random
  token so it can't be guessed. Re-running replaces it: the old file is deleted and the new one uploaded.
- Cover preview: page 1 of the PDF as WebP q90.
- Download page: slug ebook-download-<token>, not in the menu, noindex (Yoast). Marine sets her Stripe payment
  link to redirect there after payment ("After payment" -> "Don't show confirmation page" -> this URL).
State in vivify/wp-ebook.json.
"""
import os, sys, json, secrets, subprocess, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
V = ROOT + 'vivify/'
SITE = 'https://basic-darkslategray-cod-55.hostingersite.com'
MEDIA = SITE + '/wp-json/wp/v2/media'
PDF = V + 'ebook/Breakfasts-to-Ignite-Your-Potential.pdf'
STATE = V + 'wp-ebook.json'
st = json.load(open(STATE)) if os.path.exists(STATE) else {}
st.setdefault('token', secrets.token_hex(4))
T = st['token']
SLUG = f'ebook-download-{T}'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def curl(*a, data=None):
    r = subprocess.run(['curl', '-sS', '-m', '300', *a], input=data, capture_output=True, text=isinstance(data, str) or data is None)
    return json.loads(r.stdout)

def upload(path, name, mime, alt='', title=''):
    j = curl('-X', 'POST', MEDIA, '-H', f'Content-Disposition: attachment; filename="{name}"', '-H', f'Content-Type: {mime}', '--data-binary', '@' + path)
    assert 'id' in j, j
    if alt or title:
        curl('-X', 'POST', f"{MEDIA}/{j['id']}", '-H', 'Content-Type: application/json', '--data-binary', '@-',
             data=json.dumps({'alt_text': alt, 'title': title}))
    return j['id'], j['source_url']

def replace(key, path, name, mime, alt='', title=''):
    if key in st:
        curl('-X', 'DELETE', f"{MEDIA}/{st[key]['id']}?force=true")
    i, u = upload(path, name, mime, alt, title)
    st[key] = {'id': i, 'url': u}
    json.dump(st, open(STATE, 'w'), indent=1)

# 1. files
replace('pdf', PDF, f'Vivify-Sports-Breakfasts-to-Ignite-Your-Potential-{T}.pdf', 'application/pdf', title='Breakfasts to Ignite Your Potential (e-book)')
tmp = os.environ.get('TMPDIR', '/tmp') + '/vivify-cover'
subprocess.run(['pdftoppm', '-r', '110', '-png', '-f', '1', '-l', '1', '-singlefile', PDF, tmp], check=True)
subprocess.run([sys.executable, '-c', f"from PIL import Image; Image.open('{tmp}.png').save('{tmp}.webp', quality=90)"], check=True)
replace('cover', tmp + '.webp', 'breakfasts-to-ignite-your-potential-cover.webp', 'image/webp',
        alt='Cover of the Vivify Sports e-book Breakfasts to Ignite Your Potential, with chia puddings, blueberry pancakes and a berry smoothie')

# 2. page, built with the site's own header/footer
b = load('b', ROOT + 'tools/build_vivify.py')
f = SLUG + '.html'
b.PAGES[f] = '/' + SLUG
b.NEW[f] = ('/' + SLUG, 'Your e-book: Breakfasts to Ignite Your Potential | Vivify Sports', 'Download your Vivify Sports breakfast recipe e-book.')
pdf, cover = st['pdf']['url'], st['cover']['url']
body = f"""
<section class="page-hero" style="padding-bottom:24px"><div class="wrap"><span class="eyebrow">Thank you for your order</span><h1>Your e-book is ready</h1><span class="bar" style="margin:16px auto 0"></span></div></section>
<section style="padding-top:8px"><div class="wrap g2" style="align-items:center">
 <div class="portrait" style="max-width:420px;margin:0 auto"><img src="{cover}" alt="Cover of the Vivify Sports e-book Breakfasts to Ignite Your Potential" width="910" height="1286"></div>
 <div><span class="eyebrow">E-Book</span><h2>Breakfasts to Ignite Your Potential</h2><span class="bar"></span>
  <p>Thank you for buying Marine's breakfast e-book: 38 recipes for energy, recovery and performance, with ingredients, method and calories, protein, carbs and fat for every recipe.</p>
  <p>Tap the button to download your PDF. Save it to your phone or computer so you always have it to hand. A receipt from Stripe is also on its way to your email.</p>
  <div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:22px">
   <a class="btn btn-primary" href="{pdf}" download>Download the e-book (PDF)</a>
   <a class="btn" href="blog.html">More recipes on the blog</a></div>
  <p class="muted" style="margin-top:22px;font-size:14px">Any problem with the download? <a href="contact.html">Contact Marine</a> and she will send it to you.</p>
 </div></div></section>"""
html = b.shell(f, body)
open(V + 'site/' + f, 'w').write(html)

w = load('w', ROOT + 'tools/build_vivify_wp.py')
w.push(f)
pid = w.st[f]
# Yoast: noindex, out of the sitemap; title/meta like the other pages
curl('-X', 'POST', f'{SITE}/wp-json/wp/v2/pages/{pid}', '-H', 'Content-Type: application/json', '--data-binary', '@-',
     data=json.dumps({'meta': {'_yoast_wpseo_meta-robots-noindex': '1', '_yoast_wpseo_meta-robots-nofollow': '1'}}))
curl('-X', 'POST', SITE + '/wp-json/yoast/v1/bulk_editor/update_search', '-H', 'Content-Type: application/json', '--data-binary', '@-',
     data=json.dumps({'items': [{'id': pid, 'seo_title': b.NEW[f][1]}, {'id': pid, 'meta_description': b.NEW[f][2]}]}))
subprocess.run(['curl', '-sS', '-m', '60', '-X', 'DELETE', SITE + '/wp-json/elementor/v1/cache'], capture_output=True)
st['page'] = {'id': pid, 'url': f'{SITE}/{SLUG}/'}
json.dump(st, open(STATE, 'w'), indent=1)
print(json.dumps(st, indent=1))

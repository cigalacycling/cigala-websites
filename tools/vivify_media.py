"""Upload Vivify's WebP images (vivify/webp/) to Marine's WordPress draft with their alt text.
State in vivify/wp-media.json (file -> id, url), so re-running skips images already uploaded.
  python3 -I tools/vivify_media.py
"""
import os, json, subprocess, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
V = ROOT + 'vivify/'
H = 'https://basic-darkslategray-cod-55.hostingersite.com/wp-json/wp/v2/media'
STATE = V + 'wp-media.json'
st = json.load(open(STATE)) if os.path.exists(STATE) else {}
man = json.load(open(V + 'images.json'))
# alt: first live alt that is not a file name; fall back to the alt the build uses
ALT_FIX = {'0e1488-70faaa082bbd4ad4b8d8f16a5bc3': 'Cyclist riding a lakeside road above a lake',
           '0e1488-a687b5ba8de7467fa18ece35f8a9': 'Yoga pose on a clifftop by the sea at sunset',
           '0e1488-5ffa2e2730204ef0bae918a9e4ae': 'Marine Lenehan, MSc Sports Nutritionist and founder of Vivify Sports',
           '0e1488-356941ca85c445f1834a69b48ccf': 'TrainingPeaks logo', '0e1488-a23fdd6bc1854f5a83c28cb05ea9': 'MyFitnessPal logo',
           '0e1488-e926906d84424b06892a7eb7a3b6': 'Cigala Cycling logo', '0e1488-44c2783c595b4fcba972291cd77f': 'Wicklow 200 logo',
           '0e1488-ec0a5dbc8a4642d7918c7e2a1037': 'Bryan McKinney logo', '0e1488-159617aec27442889d7671a684e6': 'vivify sports logo ',
           '0e1488-fc2524470e9740249b245fb18b25': 'Yoga alliance certified '}
def alt_for(e, name):
    for k, v in ALT_FIX.items():
        if name.startswith(k): return v
    for a in e['alts']:
        if a and not re.search(r'\.(jpe?g|png|webp)$', a.strip(), re.I): return a.strip()
    return ''
ok = 0
for mid, e in man.items():
    name = os.path.basename(e['webp'])
    if name in st or not os.path.exists(V + 'webp/' + name): continue
    r = subprocess.run(['curl', '-sS', '-m', '120', '-X', 'POST', H, '-H', f'Content-Disposition: attachment; filename="{name}"',
                        '-H', 'Content-Type: image/webp', '--data-binary', '@' + V + 'webp/' + name], capture_output=True, text=True)
    try: j = json.loads(r.stdout)
    except Exception: print('FAIL', name, r.stdout[:200]); continue
    if 'id' not in j: print('FAIL', name, j.get('code'), j.get('message')); continue
    alt = alt_for(e, name)
    subprocess.run(['curl', '-sS', '-m', '60', '-X', 'POST', f"{H}/{j['id']}", '-H', 'Content-Type: application/json',
                    '--data-binary', json.dumps({'alt_text': alt, 'title': alt or name})], capture_output=True)
    st[name] = {'id': j['id'], 'url': j['source_url'], 'alt': alt}
    json.dump(st, open(STATE, 'w'), indent=1); ok += 1
print('uploaded', ok, '| total on site', len(st))

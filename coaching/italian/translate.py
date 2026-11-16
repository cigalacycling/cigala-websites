# Italian versions of the six coaching PDFs.
# Collects every visible text node (and alt/title text) of the English HTML, replaces it with the Italian in it.json,
# and writes <name>-IT.html next to the English file. Run with --list to print strings that have no translation yet.
# Usage: python3 -I coaching/italian/translate.py [--list]
import json, os, re, sys, html as H
HERE = os.path.dirname(os.path.abspath(__file__))
C = os.path.dirname(HERE)
DOCS = ['nutrition-guide/guide.html', 'supplement-list/supplements.html',
        'training-sheets/Gym-Circuit-Winter-First-Month.html', 'training-sheets/Gym-Circuit-Winter-Second-Third-Month.html',
        'training-sheets/Gym-Circuit-In-Season.html', 'training-sheets/Stretches-and-Core.html']
TR = json.load(open(os.path.join(HERE, 'it.json'))) if os.path.exists(os.path.join(HERE, 'it.json')) else {}
SKIP = re.compile(r'^[\s\d.,:;+\-–—%/×•·→↓"”’\'()]*$|^(\+353[\d ]+|0\d\d [\d ]+|[\w.]+@[\w.]+|(www\.)?[\w-]+\.com[/\w-]*|https?://\S+)$')
missing = []
# fixes the text-node swap can't make: split cover title, pie labels in the script, Italian number formats
POST = {
    '>Integratore<br>Integratori<': '>Lista<br>Integratori<',
    "labs=[['Fruit &','veg.'],['Grains'],['Protein']]": "labs=[['Frutta e','verdura'],['Cereali'],['Proteine']]",
    '>1.6 – 2.3<': '>1,6 – 2,3<',
    '</style>': '\n/* Italian runs longer: a little less space around headings */\nh3{margin:15px 0 4px}h3+.bar{margin:9px 0 10px}.sec{margin-bottom:10px}.sec .bar{margin:12px 0 10px}.cover .by .role{letter-spacing:.08em}.mantra{font-size:17px}\n</style>', '>1,500 – 8,000<': '>1.500 – 8.000<',
}
def tr(s):
    k = ' '.join(s.split())
    if not k or SKIP.match(k): return s
    if k in TR: 
        lead = s[:len(s) - len(s.lstrip())]; trail = s[len(s.rstrip()):]
        return lead + TR[k] + trail
    missing.append(k); return s
def tr_attr(m):
    return f'{m.group(1)}="{H.escape(tr(H.unescape(m.group(2))), quote=True)}"'
for d in DOCS:
    src = open(os.path.join(C, d)).read()
    out, i = [], 0
    # split off <style> and <script> blocks (not translated as text; pie labels handled below)
    parts = re.split(r'(<style>.*?</style>|<script>.*?</script>)', src, flags=re.S)
    res = []
    for p in parts:
        if p.startswith('<style>') or p.startswith('<script>'):
            res.append(p); continue
        segs = re.split(r'(<[^>]+>)', p)
        for s in segs:
            if s.startswith('<'):
                s = re.sub(r'\b(alt|title|aria-label)="([^"]*)"', tr_attr, s)
                res.append(s)
            else:
                res.append(H.escape(tr(H.unescape(s)), quote=False) if s.strip() else s)
    out = ''.join(res).replace('<html lang="en-GB">', '<html lang="it">')
    for a, b in POST.items():
        out = out.replace(a, b)
    if '--list' not in sys.argv:
        open(os.path.join(C, d.replace('.html', '-IT.html')), 'w').write(out)
seen = []
for m in missing:
    if m not in seen: seen.append(m)
if '--list' in sys.argv:
    json.dump(seen, open(os.path.join(HERE, 'todo.json'), 'w'), ensure_ascii=False, indent=0)
print('untranslated:', len(seen))

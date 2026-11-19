"""List the English text pieces of the Vivify pages that have no French/Italian translation yet.

  python3 tools/vivify_i18n_extract.py > vivify/i18n-todo.json

Skips what stays in English on purpose: client review quotes and names, blog card titles/excerpts (posts are English),
<script>/<style>, and pages that are not translated (blog.html: the post list is dynamic; posts; the e-book download page).
"""
import os, re, sys, json, html, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
V = ROOT + 'vivify/'
sys.path.insert(0, V)
import i18n

SKIP_PAGES = ('blog.html',)
def pages():
    return sorted(os.path.basename(f) for f in glob.glob(V + 'site/*.html')
                  if not os.path.basename(f).startswith(('post-', 'ebook-download')) and os.path.basename(f) not in SKIP_PAGES)

KEEP_EN = [r'<blockquote>.*?</blockquote>', r'<a class="bcard[^"]*".*?</a>', r'<(p|h2) class="name">.*?</\1>',
           r'<script\b.*?</script>', r'<style\b.*?</style>', r'<div class="who">.*?</div></div>']

def texts(h):
    for rx in KEEP_EN:
        h = re.sub(rx, ' ', h, flags=re.S)
    for tok in re.split(r'(<[^>]+>)', h):
        if tok.startswith('<'): continue
        key = re.sub(r'\s+', ' ', html.unescape(tok)).strip()
        if len(key) > 1 and re.search('[A-Za-z]{2}', key):
            yield key

if __name__ == '__main__':
    todo = {}
    for f in pages():
        for t in texts(open(V + 'site/' + f).read()):
            if t not in i18n.TR and t not in i18n.KEEP and t not in todo and not re.fullmatch(r'.*\| Vivify Sports|[\d\s·hmkm′.:]+', t):
                todo[t] = f
    json.dump(todo, sys.stdout, indent=0, ensure_ascii=False)
    sys.stderr.write(f'{len(pages())} pages, {len(todo)} pieces, {sum(len(t.split()) for t in todo)} words\n')

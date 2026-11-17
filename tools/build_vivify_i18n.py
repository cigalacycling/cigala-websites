"""French and Italian pages for Marine's WordPress site, from the built English pages + vivify/i18n.py.

  python3 -I tools/build_vivify.py && python3 -I tools/build_vivify_i18n.py

- Text nodes are translated (vivify/i18n.py TR); untranslated text (names, plan names, reviews, blog titles) stays.
- Writes vivify/site/fr/*.html and vivify/site/it/*.html, then pushes them as WordPress pages:
  /fr/ (language home) with children /fr/<slug>/, same for /it/.
- Links to the other translated pages go to the same language; everything else goes to the English page.
- Contact form: a French and an Italian Contact Form 7 form (ids in vivify/wp-forms.json).
- Yoast title + meta from i18n.META.
State in vivify/wp-pages-i18n.json.
"""
import os, re, sys, json, html, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
V = ROOT + 'vivify/'
sys.path.insert(0, ROOT + 'tools'); sys.path.insert(0, V)
import i18n
import build_vivify_wp as W
import importlib.util
spec = importlib.util.spec_from_file_location('bv', ROOT + 'tools/build_vivify.py'); BV = importlib.util.module_from_spec(spec); spec.loader.exec_module(BV)
LANGS = {'fr': 0}   # Marine 17 Nov: Italian removed for now (translations kept in vivify/i18n.py; pages set to draft)
STATE = V + 'wp-pages-i18n.json'
st = json.load(open(STATE)) if os.path.exists(STATE) else {}
FORMS = V + 'wp-forms.json'
forms = json.load(open(FORMS)) if os.path.exists(FORMS) else {'en': 349}
CF7 = W.SITE + '/wp-json/contact-form-7/v1/contact-forms'

def tr_text(h, i):
    """translate text nodes; <script> and <style> blocks are left untouched (their code can contain "<")"""
    parts = re.split(r'(<script\b.*?</script>|<style\b.*?</style>)', h, flags=re.S | re.I)
    out = []
    for n, part in enumerate(parts):
        if n % 2:
            out.append(part); continue
        for tok in re.split(r'(<[^>]+>)', part):
            if tok.startswith('<') or not tok.strip():
                out.append(tok); continue
            key = re.sub(r'\s+', ' ', html.unescape(tok)).strip()
            if key in i18n.TR:
                lead = tok[:len(tok) - len(tok.lstrip())]; trail = tok[len(tok.rstrip()):]
                out.append(lead + html.escape(i18n.TR[key][i], quote=False) + trail)
            else:
                out.append(tok)
    return ''.join(out)

def path(lang, f):
    slug = i18n.PAGES[f][LANGS[lang]]
    return f'/{lang}/' + (slug + '/' if slug else '')

def translate_page(lang, f):
    i = LANGS[lang]
    s = open(V + 'site/' + f).read()
    # links to translated pages stay in this language
    for g in i18n.PAGES:
        s = s.replace(f'href="{g}"', f'href="{path(lang, g)}"').replace(f'href="{g}#', f'href="{path(lang, g)}#')
    s = re.sub(r'<li class="lang".*?</li>', lambda m: BV.lang_switch(lang + '/' + f, lang), s, flags=re.S)
    s = s.replace('<html lang="en">', f'<html lang="{lang}">')
    return tr_text(s, i)

def cf7_form(lang):
    """French / Italian copy of the English contact form; created once, then updated (context=save is required)"""
    i = LANGS[lang]
    L = {'fr': ('Envoyer un message', 'Nom', 'E-mail', 'Je suis intéressé(e) par', ['Coaching nutritionnel', 'Plan de ravitaillement', 'Ateliers et conférences', 'Yoga', 'E-book', 'Autre'],
                'Message', 'Votre sport, vos objectifs et vos prochaines épreuves', 'Envoyer', 'Merci ! Marine vous répondra très vite.', 'Demande site (FR)'),
         'it': ('Invia un messaggio', 'Nome', 'E-mail', 'Mi interessa', ['Coaching nutrizionale', 'Piano di alimentazione in gara', 'Workshop e conferenze', 'Yoga', 'E-book', 'Altro'],
                'Messaggio', 'Il tuo sport, i tuoi obiettivi e le prossime gare', 'Invia', 'Grazie! Marine ti risponderà al più presto.', 'Richiesta dal sito (IT)')}[lang]
    eyebrow, nm, em, interest, opts, msg, ph, send, ok, subj = L
    form = (f'<span class="eyebrow" style="margin:0">{eyebrow}</span>\n'
            f'<div class="two"><div><label for="f-n">{nm}</label>[text* your-name id:f-n autocomplete:name]</div>'
            f'<div><label for="f-e">{em}</label>[email* your-email id:f-e autocomplete:email]</div></div>\n'
            f'<div><label for="f-s">{interest}</label>[select your-service id:f-s ' + ' '.join(f'"{o}"' for o in opts) + ']</div>\n'
            f'<div><label for="f-m">{msg}</label>[textarea* your-message id:f-m placeholder "{ph}"]</div>\n'
            f'[submit class:btn class:btn-primary "{send}"]')
    mail = {'active': '1', 'recipient': 'marine@vivifysports.com', 'sender': '[_site_title] <wordpress@[_site_domain]>',
            'subject': f'{subj}: [your-service] - [your-name]', 'additional_headers': 'Reply-To: [your-email]',
            'body': 'From: [your-name] <[your-email]>\nInterested in: [your-service]\nLanguage: ' + lang.upper() + '\n\n[your-message]\n\n--\n[_site_url]'}
    url = CF7 + (f'/{forms[lang]}' if lang in forms else '')
    args = ['curl', '-sS', '-X', 'POST', url, '--data-urlencode', 'context=save', '--data-urlencode', f'title=Contact ({lang.upper()})',
            '--data-urlencode', f'locale={"fr_FR" if lang == "fr" else "it_IT"}', '--data-urlencode', 'form=' + form,
            '--data-urlencode', 'messages[mail_sent_ok]=' + ok]
    for k, v in mail.items(): args += ['--data-urlencode', f'mail[{k}]={v}']
    d = json.loads(subprocess.run(args, capture_output=True, text=True).stdout)
    if d.get('id'): forms[lang] = d['id']; json.dump(forms, open(FORMS, 'w'), indent=1)
    return forms.get(lang)

def api(method, url, body):
    return json.loads(subprocess.run(['curl', '-sS', '-m', '120', '-X', method, url, '-H', 'Content-Type: application/json', '--data-binary', '@-'],
                                     input=json.dumps(body), capture_output=True, text=True).stdout)

def push(lang, f, parent):
    os.makedirs(V + f'site/{lang}', exist_ok=True)
    out = V + f'site/{lang}/{f}'
    h = translate_page(lang, f)
    open(out, 'w').write(h)
    title, els, content = W.page_data(f'{lang}/{f}')
    if f == 'contact.html':   # the language's own form
        s = json.dumps(els).replace('[contact-form-7 id=\\"349\\"', f'[contact-form-7 id=\\"{forms[lang]}\\"')
        els = json.loads(s)
    name = i18n.META[lang][f][0].split('|')[0].strip()
    slug = i18n.PAGES[f][LANGS[lang]] or lang
    body = {'title': name, 'slug': slug, 'status': 'publish', 'template': 'elementor_canvas', 'content': content,
            'meta': {'_elementor_data': json.dumps(els), '_elementor_edit_mode': 'builder', '_elementor_template_type': 'wp-page'}}
    if parent: body['parent'] = parent
    key = f'{lang}/{f}'
    j = api('POST', W.API + (f'/{st[key]}' if key in st else ''), body)
    if 'id' not in j: print('FAIL', key, j.get('code'), j.get('message')); return None
    st[key] = j['id']; json.dump(st, open(STATE, 'w'), indent=1)
    print(j['id'], j['link'])
    return j['id']

def yoast():
    items = []
    for key, pid in st.items():
        lang, f = key.split('/', 1)
        if lang not in LANGS: continue
        t, d = i18n.META[lang][f]
        items += [{'id': pid, 'seo_title': t}, {'id': pid, 'meta_description': d}]
    out = subprocess.run(['curl', '-sS', '-X', 'POST', W.SITE + '/wp-json/yoast/v1/bulk_editor/update_search', '-H', 'Content-Type: application/json',
                          '--data-binary', json.dumps({'items': items})], capture_output=True, text=True).stdout
    res = json.loads(out).get('results', [])
    print('yoast', len(res), 'items,', sum(not r['success'] for r in res), 'failed')

if __name__ == '__main__':
    for lang in LANGS:
        cf7_form(lang)
        home = push(lang, 'index.html', 0)
        for f in i18n.PAGES:
            if f != 'index.html': push(lang, f, home)
    yoast()
    subprocess.run(['curl', '-sS', '-X', 'DELETE', W.SITE + '/wp-json/elementor/v1/cache'], capture_output=True)

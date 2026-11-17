"""Add "Share your rides" (Matteo approved 17 Nov) just before the Training library section of each shared hub, in place.
Usage: share.py [--live]. Skips a hub that already has it."""
import sys, json
live = '--live' in sys.argv
sys.argv = ['x'] + (['--live'] if live else []); sys.path.insert(0, r'C:\Users\matte\vekta\athlete-hub\cigala-websites\tools')
import coaching_athlete_area as c
LIB = {'en': 'Training library', 'it': 'Biblioteca di allenamento', 'pt': 'Biblioteca de treino', 'sl': 'Knjižnica za trening'}
T = {
 'en': ('Share your rides', 'Proud of a session? Share it and tag us, we love seeing your work.',
        ['Open the <b>Vekta app</b> and tap a session you’ve done.', 'Tap <b>Share</b> (top right) and pick Instagram, Facebook or wherever you post.', 'Tag <b>@cigalacycling</b>. We’ll share the best ones.'],
        'Follow us for training tips, rider stories and race weeks.'),
 'it': ('Condividi le tue uscite', 'Fiero di un allenamento? Condividilo e taggaci, ci piace vedere il tuo lavoro.',
        ['Apri l’<b>app Vekta</b> e tocca un allenamento che hai fatto.', 'Tocca <b>Condividi</b> (in alto a destra) e scegli Instagram, Facebook o dove pubblichi.', 'Tagga <b>@cigalacycling</b>. Condivideremo i migliori.'],
        'Seguici per consigli di allenamento, storie dei nostri atleti e settimane di gara.'),
 'pt': ('Partilha os teus treinos', 'Orgulhoso de um treino? Partilha-o e marca-nos, adoramos ver o teu trabalho.',
        ['Abre a <b>app Vekta</b> e toca num treino que fizeste.', 'Toca em <b>Partilhar</b> (canto superior direito) e escolhe Instagram, Facebook ou onde publicas.', 'Marca <b>@cigalacycling</b>. Vamos partilhar os melhores.'],
        'Segue-nos para dicas de treino, histórias de atletas e semanas de prova.'),
 'sl': ('Deli svoje vožnje', 'Ponosen na trening? Deli ga in nas označi, radi vidimo tvoje delo.',
        ['Odpri <b>aplikacijo Vekta</b> in tapni trening, ki si ga opravil.', 'Tapni <b>Deli</b> (zgoraj desno) in izberi Instagram, Facebook ali kjer objavljaš.', 'Označi <b>@cigalacycling</b>. Najboljše bomo delili.'],
        'Sledi nam za nasvete o treningu, zgodbe kolesarjev in tekmovalne tedne.'),
}
LINKS = [('Instagram', 'https://www.instagram.com/cigalacycling/'), ('Facebook', 'https://www.facebook.com/CigalaCycling/'),
         ('TikTok', 'https://www.tiktok.com/@cigalacycling'), ('YouTube', 'https://www.youtube.com/@cigalacycling')]

def block(lang):
    h, lede, steps, follow = T[lang]
    return (c.h2(h) + c.para(lede)
            + '<!-- wp:list {"ordered":true} --><ol class="wp-block-list">' + ''.join(f'<!-- wp:list-item --><li>{s}</li><!-- /wp:list-item -->' for s in steps) + '</ol><!-- /wp:list -->'
            + c.buttons(*[c.btn(n, u, True) for n, u in LINKS])
            + c.para(f'<em>{follow}</em>'))

bk = c.ROOT + ('live-coaching' if live else 'stg-coaching') + '/backup/'
for p in c.req(f'{c.B}/wp/v2/cc_athlete?status=private&per_page=100&context=edit&_fields=id,meta,content'):
    if not (p.get('meta') or {}).get('cc_shared'): continue
    lang = p['meta'].get('cc_lang') or 'en'; raw = p['content']['raw']
    if '@cigalacycling</b>' in raw: print(p['id'], lang, 'already there'); continue
    i = raw.find(f'<h2 class="wp-block-heading">{LIB[lang]}</h2>')
    j = raw.rfind('<!-- wp:heading -->', 0, i) if i >= 0 else -1
    if j < 0: print(p['id'], lang, 'library heading not found: skipped'); continue
    json.dump({'id': p['id'], 'raw': raw}, open(bk + f'shared-hub-{p["id"]}-before-share-2026-11-17.json', 'w', encoding='utf-8'), ensure_ascii=False)
    r = c.req(f'{c.B}/wp/v2/cc_athlete/{p["id"]}', {'content': raw[:j] + block(lang) + raw[j:]}, 'POST')
    print(p['id'], lang, 'added' if '@cigalacycling</b>' in ((r.get('content') or {}).get('raw', '') if isinstance(r, dict) else '') else 'CHECK ' + str(r)[:200])

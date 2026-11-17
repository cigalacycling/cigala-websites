"""Shared hubs, Matteo 17 Nov (second pass): video routines as small cards inside the Training library; "Share your rides"
at the bottom, Instagram only, no follow line. Starts from each hub as it was before the first videos/share edit
(backup *-before-videos-2026-11-17.json, only the rename in it), so the earlier big players and share block go.
Usage: hub_extras.py [--live]"""
import sys, json, os
live = '--live' in sys.argv
sys.argv = ['x'] + (['--live'] if live else []); sys.path.insert(0, r'C:\Users\matte\vekta\athlete-hub\cigala-websites\tools')
import coaching_athlete_area as c
LIB = {'en': 'Training library', 'it': 'Biblioteca di allenamento', 'pt': 'Biblioteca de treino', 'sl': 'Knjižnica za trening'}
H3 = {'en': 'Video routines', 'it': 'Routine in video', 'pt': 'Rotinas em vídeo', 'sl': 'Video rutine'}
PL = [('https://www.youtube.com/playlist?list=PL5DQPV2sc_0WTgEJlbBZpJXFOjgDktpnz', {'en': 'Core &amp; Strength Routine', 'it': 'Routine core e forza', 'pt': 'Rotina de core e força', 'sl': 'Rutina za core in moč'}),
      ('https://www.youtube.com/playlist?list=PL5DQPV2sc_0VdvMQZYo-Qaxv6Ual0Fbm7', {'en': 'Stretch Routine', 'it': 'Routine di stretching', 'pt': 'Rotina de alongamentos', 'sl': 'Rutina raztezanja'})]
T = {
 'en': ('Share your rides', 'Proud of a session? Share it on Instagram and tag us, we love seeing your work.',
        ['Open the <b>Vekta app</b> and tap a session you’ve done.', 'Tap <b>Share</b> (top right) and choose <b>Instagram</b>.', 'Tag <b>@cigalacycling</b> in your story or post. We’ll share the best ones.']),
 'it': ('Condividi le tue uscite', 'Fiero di un allenamento? Condividilo su Instagram e taggaci, ci piace vedere il tuo lavoro.',
        ['Apri l’<b>app Vekta</b> e tocca un allenamento che hai fatto.', 'Tocca <b>Condividi</b> (in alto a destra) e scegli <b>Instagram</b>.', 'Tagga <b>@cigalacycling</b> nella storia o nel post. Condivideremo i migliori.']),
 'pt': ('Partilha os teus treinos', 'Orgulhoso de um treino? Partilha-o no Instagram e marca-nos, adoramos ver o teu trabalho.',
        ['Abre a <b>app Vekta</b> e toca num treino que fizeste.', 'Toca em <b>Partilhar</b> (canto superior direito) e escolhe <b>Instagram</b>.', 'Marca <b>@cigalacycling</b> na story ou no post. Vamos partilhar os melhores.']),
 'sl': ('Deli svoje vožnje', 'Ponosen na trening? Deli ga na Instagramu in nas označi, radi vidimo tvoje delo.',
        ['Odpri <b>aplikacijo Vekta</b> in tapni trening, ki si ga opravil.', 'Tapni <b>Deli</b> (zgoraj desno) in izberi <b>Instagram</b>.', 'Označi <b>@cigalacycling</b> v zgodbi ali objavi. Najboljše bomo delili.']),
}
def videos(lang):
    return (f'<!-- wp:heading {{"level":3}} --><h3 class="wp-block-heading">{H3[lang]}</h3><!-- /wp:heading -->'
            + c.buttons(*[c.btn(t[lang], u, True) for u, t in PL]))
def share(lang):
    h, lede, steps = T[lang]
    return (c.h2(h) + c.para(lede)
            + '<!-- wp:list {"ordered":true} --><ol class="wp-block-list">' + ''.join(f'<!-- wp:list-item --><li>{s}</li><!-- /wp:list-item -->' for s in steps) + '</ol><!-- /wp:list -->'
            + c.buttons(c.btn(HOW[lang], 'https://www.instagram.com/reel/DeyoyBDI1Rl/', True),   # Vekta's own reel showing session sharing (linked, not copied)
                        c.btn('Instagram', 'https://www.instagram.com/cigalacycling/', True)))
HOW = {'en': 'See how it works (Vekta video)', 'it': 'Guarda come funziona (video Vekta)', 'pt': 'Vê como funciona (vídeo Vekta)', 'sl': 'Poglej, kako deluje (video Vekta)'}

bk = c.ROOT + ('live-coaching' if live else 'stg-coaching') + '/backup/'
for p in c.req(f'{c.B}/wp/v2/cc_athlete?status=private&per_page=100&context=edit&_fields=id,meta,content'):
    if not (p.get('meta') or {}).get('cc_shared'): continue
    lang = p['meta'].get('cc_lang') or 'en'
    base_f = bk + f'shared-hub-{p["id"]}-before-videos-2026-11-17.json'
    if not os.path.exists(base_f): print(p['id'], lang, 'no base backup: skipped'); continue
    raw = json.load(open(base_f, encoding='utf-8'))['raw']
    i = raw.find(f'<h2 class="wp-block-heading">{LIB[lang]}</h2>')
    j = raw.find('<!-- wp:heading -->', i + 10) if i >= 0 else -1
    if j < 0: print(p['id'], lang, 'library not found: skipped'); continue
    # Matteo 17 Nov (third pass): videos above Nutrition (the last h3 in the library), Share your rides above the blog (the last h2, "Worth reading")
    v = raw.rfind('<!-- wp:heading {"level":3} -->', i, j)
    w = raw.rfind('<!-- wp:heading -->')
    if v < 0 or w <= j: print(p['id'], lang, 'layout not as expected: skipped'); continue
    new = raw[:v] + videos(lang) + raw[v:w] + share(lang) + raw[w:]
    json.dump({'id': p['id'], 'raw': p['content']['raw']}, open(bk + f'shared-hub-{p["id"]}-before-extras-v2-2026-11-17.json', 'w', encoding='utf-8'), ensure_ascii=False)
    r = c.req(f'{c.B}/wp/v2/cc_athlete/{p["id"]}', {'content': new}, 'POST')
    s = (r.get('content') or {}).get('raw', '') if isinstance(r, dict) else ''
    print(p['id'], lang, 'ok' if ('PL5DQPV2sc_0VdvMQZYo' in s and '@cigalacycling</b>' in s and 'iframe' not in s and 'tiktok' not in s) else 'CHECK ' + str(r)[:200])

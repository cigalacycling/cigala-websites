"""Athlete area on Coaching STAGING (Matteo, 16 Nov 2026): one login per athlete, removed when they finish.
  python3 -I tools/coaching_athlete_area.py [--hub] [--availability] [--live]   (--availability adds the new athlete-area parts: availability, rider form + hub lock, goals & events, passwords; --hub rewrites the shared hub page; only before Matteo edits it himself)
Switches Code Snippets on, pushes coaching/athlete-area/athlete-area.php as a snippet (ID kept in stg-coaching/athlete-snippet-id.txt),
creates the /athletes/ page and the "Shared hub (all athletes)" page once. Re-running updates the snippet only.
The proxy adds the staging application password; there are no secrets here.
"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
LIVE = '--live' in sys.argv   # live since 16 Nov 2026 evening (Matteo gave live access): test on staging first, back up, then --live
if LIVE and ('--hub' in sys.argv or '--availability' in sys.argv): raise SystemExit('--hub/--availability on live only with Matteo\'s explicit go: run them by hand')
HOST = 'coaching.cigalacycling.com' if LIVE else 'staging.coaching.cigalacycling.com'
B = f'https://{HOST}/wp-json'
SNIP = ROOT + ('live-coaching' if LIVE else 'stg-coaching') + '/athlete-snippet-id.txt'

def laptop_auth():   # Matteo's laptop (17 Nov 2026): no proxy there, so the application password comes from vekta\.env (never printed)
    env = os.path.normpath(ROOT + '../../.env')
    if not os.path.exists(env): return None
    kv = dict(l.strip().split('=', 1) for l in open(env, encoding='utf-8') if '=' in l and not l.lstrip().startswith('#'))
    u, p = (kv.get('CC_HUB_USER'), kv.get('CC_HUB_APP_PASSWORD')) if LIVE else (kv.get('CC_STG_USER'), kv.get('CC_STG_APP_PASSWORD'))
    if not (u and p): raise SystemExit('Add ' + ('CC_HUB_USER / CC_HUB_APP_PASSWORD' if LIVE else 'CC_STG_USER / CC_STG_APP_PASSWORD') + ' to ' + env)
    return u.strip() + ':' + p.strip()
AUTH = laptop_auth()

def req(url, body=None, method='GET'):
    assert url.startswith(f'https://{HOST}/')
    a = ['curl', '-sS', '-m', '90', '-X', method, url]
    if AUTH:   # laptop: Windows curl (Python's OpenSSL rejects the new Let's Encrypt chain); the password goes in a temp config file, never on the command line
        import tempfile
        fd, cfg = tempfile.mkstemp(suffix='.curl')
        with os.fdopen(fd, 'w') as f: f.write('user = "' + AUTH.replace('\\', '\\\\').replace('"', '\\"') + '"\n')
        a += ['-K', cfg]
        try:
            if body is not None: a += ['-H', 'Content-Type: application/json', '--data-binary', '@-']
            r = subprocess.run(a, capture_output=True, input=json.dumps(body).encode() if body is not None else None)
        finally: os.remove(cfg)
        out = r.stdout.decode('utf-8', 'replace')
        try: return json.loads(out or 'null')
        except ValueError: raise SystemExit('bad response: ' + out[:300])
    if body is not None: a += ['-H', 'Content-Type: application/json', '--data-binary', '@-']   # from stdin: the snippet is too big for an argument
    r = subprocess.run(a, capture_output=True, text=True, input=json.dumps(body) if body is not None else None)
    try: return json.loads(r.stdout or 'null')
    except ValueError: raise SystemExit('bad response: ' + r.stdout[:300])

def btn(text, url, outline=False, ext=True):
    st = ' {"className":"is-style-outline"}' if outline else ''
    cls = ' is-style-outline' if outline else ''
    tgt = ' target="_blank" rel="noreferrer noopener"' if ext else ''
    return (f'<!-- wp:button{st} --><div class="wp-block-button{cls}"><a class="wp-block-button__link wp-element-button" href="{url}"{tgt}>{text}</a></div><!-- /wp:button -->')

def h2(t): return f'<!-- wp:heading --><h2 class="wp-block-heading">{t}</h2><!-- /wp:heading -->'
def para(t): return f'<!-- wp:paragraph --><p>{t}</p><!-- /wp:paragraph -->'
def buttons(*b, cls=''):
    if cls: return f'<!-- wp:buttons {{"className":"{cls}"}} --><div class="wp-block-buttons {cls}">' + ''.join(b) + '</div><!-- /wp:buttons -->'
    return '<!-- wp:buttons --><div class="wp-block-buttons">' + ''.join(b) + '</div><!-- /wp:buttons -->'
def links(items):
    li = ''.join(f'<!-- wp:list-item --><li><a href="{u}">{t}</a></li><!-- /wp:list-item -->' for t, u in items)
    return f'<!-- wp:list --><ul class="wp-block-list">{li}</ul><!-- /wp:list -->'
# Matteo 16 Nov: no Training zones or FTP test here (his athletes work with Critical Power and already have their zones)
TOOLS = [('Carbs per hour', '/tools/carbs-per-hour-calculator/'),
         ('Critical Power', '/tools/critical-power-calculator/'),
         ('Sweat rate', '/tools/sweat-rate-calculator/'), ('Climb time', '/tools/climb-time-calculator/'),
         ('Gear &amp; speed', '/tools/gear-speed-calculator/'), ('Swim pace (CSS)', '/tools/swim-pace-calculator/')]
READ = [('Training', [('The power of Zone 2 training', '/blog/zone-2-training/'), ('Critical Power', '/blog/critical-power/'),
                      ('What is W Prime?', '/blog/w-prime/'), ('Critical Power testing: how to get reliable data', '/blog/critical-power-testing/'),
                      ('Strength training for cyclists', '/blog/strength-training-for-cyclists/'), ('How to calibrate a power meter', '/blog/calibrate-a-power-meter/')]),
        ('Fuelling', [('How many carbs per hour?', '/blog/carbs-per-hour-endurance-fueling/'), ('What to eat and drink on the bike', '/blog/cycling-nutrition-what-to-eat-and-drink-on-the-bike/'),
                      ('Hydration tips', '/blog/hydration-tips/'), ('Avoid bonking on the bike', '/blog/why-do-you-bonk-on-the-bike/')]),
        ('Recovery', [('How to maximise your recovery', '/blog/how-to-maximse-your-recovery/'), ('Why am I so tired after exercise?', '/blog/fatigue-after-exercise-endurance-athletes/'),
                      ('Heart rate variability (HRV)', '/blog/heart-rate-variability-hrv/')]),
        ('Race week', [('Tapering', '/blog/tapering/'), ('Potentiation in warm-ups', '/blog/the-importance-of-potentiation-in-warm-ups/'),
                       ('Tips for not getting dropped', '/blog/tips-for-not-getting-dropped-cigala-cycling-coaching/'), ('Tips for gravel racing', '/blog/tips-for-gravel-racing/')])]
# the PDFs every athlete gets (made in the "New session" chat, Matteo-approved). Uploaded once into the shared hub's private folder;
# the media IDs are kept in stg-coaching/athlete-hub-files.json. (title shown on the card, file in the repo)
GUIDES = [('Strength and core', [('Stretches &amp; Core', 'coaching/training-sheets/Cigala-Cycling-Stretches-and-Core.pdf'),
                                 ('Gym Circuit: Winter, first month', 'coaching/training-sheets/Cigala-Cycling-Gym-Circuit-Winter-First-Month.pdf'),
                                 ('Gym Circuit: Winter, second and third month', 'coaching/training-sheets/Cigala-Cycling-Gym-Circuit-Winter-Second-Third-Month.pdf'),
                                 ('Gym Circuit: In season', 'coaching/training-sheets/Cigala-Cycling-Gym-Circuit-In-Season.pdf')]),
          ('Nutrition, with Marine Lenehan', [('Nutritional Guide', 'coaching/nutrition-guide/Cigala-Cycling-x-Vivify-Sports-Nutritional-Guide.pdf'),
                                              ('Supplement List', 'coaching/supplement-list/Cigala-Cycling-x-Vivify-Sports-Supplement-List.pdf')])]
FILES = ROOT + 'stg-coaching/athlete-hub-files.json'
def file_block(mid, url, title):
    return (f'<!-- wp:file {{"id":{mid},"href":"{url}"}} --><div class="wp-block-file"><a href="{url}">{title}</a>'
            f'<a href="{url}" class="wp-block-file__button wp-element-button" download>Download</a></div><!-- /wp:file -->')
def guides_html():
    ids = json.load(open(FILES)) if os.path.exists(FILES) else {}
    out = ''
    for g, items in GUIDES:
        blocks = ''.join(file_block(ids[f]['id'], ids[f]['url'], t) for t, f in items if f in ids)
        if blocks: out += f'<!-- wp:heading {{"level":3}} --><h3 class="wp-block-heading">{g}</h3><!-- /wp:heading -->' + blocks
    return out or para('Core routine, exercises and gym sessions: the PDFs will be here soon.')
def upload_guides(hub_id):
    ids = json.load(open(FILES)) if os.path.exists(FILES) else {}
    for _, items in GUIDES:
        for t, f in items:
            if f in ids: continue
            r = subprocess.run(['curl', '-sS', '-m', '300', '-X', 'POST', f'{B}/wp/v2/media', '-F', f'file=@{ROOT + f};type=application/pdf',
                                '-F', f'post={hub_id}', '-F', 'title=' + t.replace('&amp;', '&')], capture_output=True, text=True)
            d = json.loads(r.stdout); assert d.get('id'), r.stdout[:300]
            assert '/athletes/?cc_file=' in d['source_url'], 'not in the private folder: ' + d['source_url']
            ids[f] = {'id': d['id'], 'url': d['source_url']}; print('uploaded', f, d['id'])
            json.dump(ids, open(FILES, 'w'), indent=1)
HUB = lambda: (h2('Quick links')
       + buttons(btn('Book a catch-up call', 'https://cal.com/matteocigala/15min'), btn('Nutrition consult with Marine', 'https://www.vivifysports.com/nutritionalcoaching'),
                 btn('WhatsApp Matteo', 'https://wa.me/353834777697', True), btn('Community on Skool', 'https://www.skool.com/cigala-cycling-collective-1115', True))
       + para('The Skool community is free for coaching clients. No invitation yet? <a href="mailto:matteo@cigalacycling.com?subject=Skool%20invitation">Email me</a> and I will send it (please check your spam folder too, sometimes it ends up there).')
       + h2('Your training apps')
       + para('Your plan is in Vekta and syncs to your Garmin, Wahoo or Zwift.')   # Matteo 16 Nov: Vekta only
       + buttons(btn('Open my Vekta calendar', 'https://app.joinvekta.com/me/calendar', True))   # Matteo 16 Nov: straight to the calendar
       + h2('Training library')
       + guides_html()
       + h2('Training tools')
       + buttons(*[btn(t, u, True, False) for t, u in TOOLS], cls='ath-tools')
       + h2('Worth reading')
       + '<!-- wp:heading {"level":3} --><h3 class="wp-block-heading">New on the blog</h3><!-- /wp:heading --><!-- wp:shortcode -->[cc_latest_posts lang="en"]<!-- /wp:shortcode -->'
       + ''.join(f'<!-- wp:heading {{"level":3}} --><h3 class="wp-block-heading">{g}</h3><!-- /wp:heading -->' + links(items) for g, items in READ))


# ---------- the Italian hub (Matteo 16 Nov: Italian athletes see everything in Italian) ----------
# Same sections. The PDFs are the English ones, marked "(in inglese)", until the Italian versions are ready (their paths go in
# GUIDES_IT; the two co-branded with Marine need her approval first). The tools pages are in English, with Italian labels here.
GUIDES_IT = [('Forza e core', [('Stretching e Core', 'coaching/training-sheets/Cigala-Cycling-Stretches-and-Core.pdf'),
                               ('Circuito palestra: inverno, primo mese', 'coaching/training-sheets/Cigala-Cycling-Gym-Circuit-Winter-First-Month.pdf'),
                               ('Circuito palestra: inverno, secondo e terzo mese', 'coaching/training-sheets/Cigala-Cycling-Gym-Circuit-Winter-Second-Third-Month.pdf'),
                               ('Circuito palestra: in stagione', 'coaching/training-sheets/Cigala-Cycling-Gym-Circuit-In-Season.pdf')]),
             ('Alimentazione, con Marine Lenehan', [('Guida nutrizionale', 'coaching/nutrition-guide/Cigala-Cycling-x-Vivify-Sports-Nutritional-Guide.pdf'),
                                                    ('Lista integratori', 'coaching/supplement-list/Cigala-Cycling-x-Vivify-Sports-Supplement-List.pdf')])]
def guides_html_it():
    ids = json.load(open(FILES)) if os.path.exists(FILES) else {}
    out = ''
    for g, items in GUIDES_IT:
        blocks = ''
        for t, f in items:
            it = f[:-4] + '-IT.pdf'   # the Italian file once it exists and is uploaded; until then the English one
            if it in ids: blocks += file_block(ids[it]['id'], ids[it]['url'], t)
            elif f in ids: blocks += file_block(ids[f]['id'], ids[f]['url'], t + ' (in inglese)')
        if blocks: out += f'<!-- wp:heading {{"level":3}} --><h3 class="wp-block-heading">{g}</h3><!-- /wp:heading -->' + blocks
    return out or para('Core, esercizi e palestra: i PDF arriveranno qui a breve.')
TOOLS_IT = [('Carboidrati per ora', '/tools/carbs-per-hour-calculator/'),
            ('Critical Power', '/tools/critical-power-calculator/'),
            ('Tasso di sudorazione', '/tools/sweat-rate-calculator/'), ('Tempo in salita', '/tools/climb-time-calculator/'),
            ('Rapporti e velocitÃ ', '/tools/gear-speed-calculator/'), ('Passo nuoto (CSS)', '/tools/swim-pace-calculator/')]
READ_IT = [('Allenamento', [('Zone di potenza e Critical Power, spiegate semplici', '/blog/zone-di-potenza-critical-power-ciclismo/'),
                             ('Come migliorare in salita', '/blog/come-migliorare-in-salita-ciclismo/'),
                             ('Allenamento invernale: rulli, palestra e uscite', '/blog/allenamento-invernale-ciclismo-rulli/'),
                             ('Ciclismo dopo i 40 anni', '/blog/ciclismo-dopo-i-40-anni/')]),
           ('Gare e granfondo', [('Granfondo: ritmo e alimentazione il giorno della gara', '/blog/granfondo-ritmo-alimentazione-giorno-gara/'),
                                 ('Come prepararsi alla Gran Fondo Strade Bianche', '/blog/preparazione-gran-fondo-strade-bianche/'),
                                 ('Come allenarsi per la Maratona dles Dolomites', '/blog/preparazione-maratona-dles-dolomites/')])] + \
          [({'Training': 'Allenamento', 'Fuelling': 'Alimentazione', 'Recovery': 'Recupero', 'Race week': 'Settimana di gara'}[g] + ' (in inglese)', items) for g, items in READ]
def upload_guides_it(hub_it_id):   # the Italian PDFs (made in the "New session" chat), into the Italian hub's private folder
    ids = json.load(open(FILES)) if os.path.exists(FILES) else {}
    for _, items in GUIDES_IT:
        for t, f in items:
            it = f[:-4] + '-IT.pdf'
            if it in ids or not os.path.exists(ROOT + it): continue
            r = subprocess.run(['curl', '-sS', '-m', '300', '-X', 'POST', f'{B}/wp/v2/media', '-F', f'file=@{ROOT + it};type=application/pdf',
                                '-F', f'post={hub_it_id}', '-F', 'title=' + t], capture_output=True, text=True)
            d = json.loads(r.stdout); assert d.get('id'), r.stdout[:300]
            assert '/athletes/?cc_file=' in d['source_url'], 'not in the private folder: ' + d['source_url']
            ids[it] = {'id': d['id'], 'url': d['source_url']}; print('uploaded', it, d['id'])
            json.dump(ids, open(FILES, 'w'), indent=1)
HUB_IT = lambda: (h2('Link rapidi')
       + buttons(btn('Prenota una call di aggiornamento', 'https://cal.com/matteocigala/15min'), btn('Consulenza nutrizionale con Marine', 'https://www.vivifysports.com/nutritionalcoaching'),
                 btn('WhatsApp Matteo', 'https://wa.me/353834777697', True), btn('Community su Skool', 'https://www.skool.com/cigala-cycling-collective-1115', True))
       + para('La community su Skool Ã¨ gratuita per gli atleti che seguo. Non hai ancora ricevuto lâ€™invito? <a href="mailto:matteo@cigalacycling.com?subject=Invito%20Skool">Scrivimi</a> e te lo mando (controlla anche lo spam, a volte finisce lÃ¬).')
       + h2('Le tue app di allenamento')
       + para('Il tuo piano Ã¨ su Vekta e si sincronizza con Garmin, Wahoo o Zwift.')
       + buttons(btn('Apri il mio calendario Vekta', 'https://app.joinvekta.com/me/calendar', True))
       + h2('Biblioteca di allenamento')
       + guides_html_it()
       + h2('Strumenti di allenamento')
       + buttons(*[btn(t, u, True, False) for t, u in TOOLS_IT], cls='ath-tools')
       + h2('Da leggere')
       + '<!-- wp:heading {"level":3} --><h3 class="wp-block-heading">Nuovi sul blog</h3><!-- /wp:heading --><!-- wp:shortcode -->[cc_latest_posts lang="it"]<!-- /wp:shortcode -->'
       + ''.join(f'<!-- wp:heading {{"level":3}} --><h3 class="wp-block-heading">{g}</h3><!-- /wp:heading -->' + links(items) for g, items in READ_IT))


# ---------- Portuguese and Slovenian hubs (Matteo 17 Nov: every athlete sees the whole hub in their language) ----------
# Same sections as the English hub. PDFs, blog articles and tool pages are in English, so they are marked as such.
# Draft translations by Claude: a native speaker should glance at them.
HUB_T = {
 'pt': {'Quick links': 'Links rÃ¡pidos', 'Book a catch-up call': 'Marcar uma chamada', 'Nutrition consult with Marine': 'Consulta de nutriÃ§Ã£o com a Marine',
        'Community on Skool': 'Comunidade no Skool',
        'skool': 'A comunidade no Skool Ã© gratuita para os atletas que treino. Ainda nÃ£o recebeste o convite? <a href="mailto:matteo@cigalacycling.com?subject=Skool%20invitation">Envia-me um email</a> e eu mando-to (vÃª tambÃ©m a pasta de spam, Ã s vezes vai parar lÃ¡).',
        'Your training apps': 'As tuas apps de treino', 'vekta': 'O teu plano estÃ¡ no Vekta e sincroniza com o teu Garmin, Wahoo ou Zwift.', 'Open my Vekta calendar': 'Abrir o meu calendÃ¡rio Vekta',
        'Training guides': 'Biblioteca de treino', 'Strength and core': 'ForÃ§a e core', 'Nutrition, with Marine Lenehan': 'NutriÃ§Ã£o, com a Marine Lenehan',
        'Stretches &amp; Core': 'Alongamentos e core', 'Gym Circuit: Winter, first month': 'Circuito de ginÃ¡sio: inverno, primeiro mÃªs',
        'Gym Circuit: Winter, second and third month': 'Circuito de ginÃ¡sio: inverno, segundo e terceiro mÃªs', 'Gym Circuit: In season': 'Circuito de ginÃ¡sio: em Ã©poca',
        'Nutritional Guide': 'Guia de nutriÃ§Ã£o', 'Supplement List': 'Lista de suplementos', 'in English': 'em inglÃªs',
        'Training tools': 'Ferramentas de treino', 'Carbs per hour': 'Hidratos por hora', 'Critical Power': 'Critical Power', 'Sweat rate': 'Taxa de suor', 'Climb time': 'Tempo de subida',
        'Gear &amp; speed': 'MudanÃ§as e velocidade', 'Swim pace (CSS)': 'Ritmo de nataÃ§Ã£o (CSS)',
        'Worth reading': 'Vale a pena ler', 'New on the blog': 'Novo no blog', 'Training': 'Treino', 'Fuelling': 'AlimentaÃ§Ã£o', 'Recovery': 'RecuperaÃ§Ã£o', 'Race week': 'Semana de prova',
        'soon': 'Core, exercÃ­cios e ginÃ¡sio: os PDF vÃ£o estar aqui em breve.'},
 'sl': {'Quick links': 'Hitre povezave', 'Book a catch-up call': 'Rezerviraj klic', 'Nutrition consult with Marine': 'Prehranski posvet z Marine',
        'Community on Skool': 'Skupnost na Skoolu',
        'skool': 'Skupnost na Skoolu je za Å¡portnike, ki jih treniram, brezplaÄna. Povabila Å¡e nimaÅ¡? <a href="mailto:matteo@cigalacycling.com?subject=Skool%20invitation">PoÅ¡lji mi email</a> in ti ga poÅ¡ljem (preveri tudi mapo z neÅ¾eleno poÅ¡to, vÄasih pristane tam).',
        'Your training apps': 'Tvoje aplikacije za trening', 'vekta': 'Tvoj naÄrt je v Vekti in se sinhronizira z Garminom, Wahoojem ali Zwiftom.', 'Open my Vekta calendar': 'Odpri moj koledar v Vekti',
        'Training guides': 'KnjiÅ¾nica za trening', 'Strength and core': 'MoÄ in core', 'Nutrition, with Marine Lenehan': 'Prehrana, z Marine Lenehan',
        'Stretches &amp; Core': 'Raztezanje in core', 'Gym Circuit: Winter, first month': 'KroÅ¾ni trening v fitnesu: zima, prvi mesec',
        'Gym Circuit: Winter, second and third month': 'KroÅ¾ni trening v fitnesu: zima, drugi in tretji mesec', 'Gym Circuit: In season': 'KroÅ¾ni trening v fitnesu: med sezono',
        'Nutritional Guide': 'Prehranski vodnik', 'Supplement List': 'Seznam prehranskih dopolnil', 'in English': 'v angleÅ¡Äini',
        'Training tools': 'Orodja za trening', 'Carbs per hour': 'Ogljikovi hidrati na uro', 'Critical Power': 'Critical Power', 'Sweat rate': 'Stopnja potenja', 'Climb time': 'ÄŒas vzpona',
        'Gear &amp; speed': 'Prestave in hitrost', 'Swim pace (CSS)': 'Tempo plavanja (CSS)',
        'Worth reading': 'Vredno branja', 'New on the blog': 'Novo na blogu', 'Training': 'Trening', 'Fuelling': 'Prehrana', 'Recovery': 'Regeneracija', 'Race week': 'Teden tekme',
        'soon': 'Core, vaje in fitnes: PDF-ji bodo kmalu tukaj.'},
 # Slovak (Matteo 18 Nov 2026, Katka Bratekova): draft by Claude, a native speaker should glance at it
 'sk': {'Quick links': 'Rýchle odkazy', 'Book a catch-up call': 'Rezervuj si hovor', 'Nutrition consult with Marine': 'Konzultácia o výžive s Marine',
        'Community on Skool': 'Komunita na Skoole',
        'skool': 'Komunita na Skoole je pre športovcov, ktorých trénujem, zadarmo. Ešte ti neprišla pozvánka? <a href="mailto:matteo@cigalacycling.com?subject=Skool%20invitation">Pošli mi e-mail</a> a pošlem ti ju (pozri sa aj do spamu, niekedy skončí tam).',
        'Your training apps': 'Tvoje tréningové aplikácie', 'vekta': 'Tvoj plán je vo Vekte a synchronizuje sa s tvojím Garminom, Wahoo alebo Zwiftom.', 'Open my Vekta calendar': 'Otvoriť môj kalendár vo Vekte',
        'Training guides': 'Tréningová knižnica', 'Strength and core': 'Sila a core', 'Nutrition, with Marine Lenehan': 'Výživa, s Marine Lenehan',
        'Stretches &amp; Core': 'Strečing a core', 'Gym Circuit: Winter, first month': 'Kruhový tréning v posilňovni: zima, prvý mesiac',
        'Gym Circuit: Winter, second and third month': 'Kruhový tréning v posilňovni: zima, druhý a tretí mesiac', 'Gym Circuit: In season': 'Kruhový tréning v posilňovni: počas sezóny',
        'Nutritional Guide': 'Sprievodca výživou', 'Supplement List': 'Zoznam doplnkov výživy', 'in English': 'v angličtine',
        'Training tools': 'Tréningové nástroje', 'Carbs per hour': 'Sacharidy za hodinu', 'Critical Power': 'Critical Power', 'Sweat rate': 'Miera potenia', 'Climb time': 'Čas stúpania',
        'Gear &amp; speed': 'Prevody a rýchlosť', 'Swim pace (CSS)': 'Plavecké tempo (CSS)',
        'Worth reading': 'Oplatí sa prečítať', 'New on the blog': 'Nové na blogu', 'Training': 'Tréning', 'Fuelling': 'Jedlo a pitie', 'Recovery': 'Regenerácia', 'Race week': 'Pretekový týždeň',
        'soon': 'Core, cviky a posilňovňa: PDF súbory tu budú čoskoro.'}}
def upload_guides_lang(hub_id, L, files_json=None):   # the translated PDFs (<name>-PT.pdf / -SL.pdf) into that language's hub, privately
    fj = files_json or FILES; ids = json.load(open(fj)) if os.path.exists(fj) else {}
    for _, items in GUIDES:
        for t, f in items:
            tr = f[:-4] + '-' + L.upper() + '.pdf'
            if tr in ids or not os.path.exists(ROOT + tr): continue
            r = subprocess.run(['curl', '-sS', '-m', '300', '-X', 'POST', f'{B}/wp/v2/media', '-F', f'file=@{ROOT + tr};type=application/pdf',
                                '-F', f'post={hub_id}', '-F', 'title=' + HUB_T[L][t]], capture_output=True, text=True)
            d = json.loads(r.stdout); assert d.get('id'), r.stdout[:300]
            assert '/athletes/?cc_file=' in d['source_url'], 'not in the private folder: ' + d['source_url']
            ids[tr] = {'id': d['id'], 'url': d['source_url']}; print('uploaded', tr, d['id'])
            json.dump(ids, open(fj, 'w'), indent=1)
def hub_lang(L, files_json=None):
    T = HUB_T[L]; en = ' (' + T['in English'] + ')'
    ids = json.load(open(files_json or FILES)) if os.path.exists(files_json or FILES) else {}
    g = ''
    for grp, items in GUIDES:
        def one(t, f):
            tr = f[:-4] + '-' + L.upper() + '.pdf'
            if tr in ids: return file_block(ids[tr]['id'], ids[tr]['url'], T[t])   # translated guide
            return file_block(ids[f]['id'], ids[f]['url'], T[t] + en) if f in ids else ''
        blocks = ''.join(one(t, f) for t, f in items)
        if blocks: g += f'<!-- wp:heading {{"level":3}} --><h3 class="wp-block-heading">{T[grp]}</h3><!-- /wp:heading -->' + blocks
    return (h2(T['Quick links'])
       + buttons(btn(T['Book a catch-up call'], 'https://cal.com/matteocigala/15min'), btn(T['Nutrition consult with Marine'], 'https://www.vivifysports.com/nutritionalcoaching'),
                 btn('WhatsApp Matteo', 'https://wa.me/353834777697', True), btn(T['Community on Skool'], 'https://www.skool.com/cigala-cycling-collective-1115', True))
       + para(T['skool'])
       + h2(T['Your training apps']) + para(T['vekta'])
       + buttons(btn(T['Open my Vekta calendar'], 'https://app.joinvekta.com/me/calendar', True))
       + h2(T['Training guides']) + (g or para(T['soon']))
       + h2(T['Training tools'])
       + buttons(*[btn(T[t], u, True, False) for t, u in TOOLS], cls='ath-tools')
       + h2(T['Worth reading'])
       + f'<!-- wp:heading {{"level":3}} --><h3 class="wp-block-heading">{T["New on the blog"]}{en}</h3><!-- /wp:heading --><!-- wp:shortcode -->[cc_latest_posts lang="en"]<!-- /wp:shortcode -->'
       + ''.join(f'<!-- wp:heading {{"level":3}} --><h3 class="wp-block-heading">{T[grp]}{en}</h3><!-- /wp:heading -->' + links(items) for grp, items in READ))

if __name__ == '__main__':
    print('code snippets', req(f'{B}/wp/v2/plugins/code-snippets/code-snippets?_fields=plugin,status', {'status': 'active'}, 'POST'))
    code = open(ROOT + 'coaching/athlete-area/athlete-area.php').read()
    assert code.startswith('<?php\n'); code = code[len('<?php\n'):]
    if '--availability' in sys.argv:   # the availability card (README "Athlete area: availability"); only once Matteo says go
        for f in ('hub-i18n.php', 'availability-i18n.php', 'availability.php', 'form-legal.php', 'form-legal-it.php', 'onboarding-i18n.php', 'onboarding.php', 'goals.php', 'passwords.php', 'reports.php', 'pc-api.php', 'ideas.php', 'gocardless.php', 'notes.php', 'photo.php', 'push.php', 'results.php', 'news.php', 'vekta-inbox.php', 'blood.php', 'food.php', 'mealplan.php', 'nutrition-plus.php', 'today.php', 'coach-pages.php', 'week.php'):
            extra = open(ROOT + 'coaching/athlete-area/' + f).read()
            assert extra.startswith('<?php\n'); code += '\n' + extra[len('<?php\n'):].replace("if (!defined('ABSPATH')) return;", '', 1)
    body = {'name': 'Cigala athlete area (one login per athlete)', 'desc': 'Built by tools/coaching_athlete_area.py from coaching/athlete-area/athlete-area.php in the cigala-websites repo. Do not edit here.',
            'code': code, 'scope': 'global', 'active': True, 'priority': 10}
    if os.path.exists(SNIP):
        r = req(f'{B}/code-snippets/v1/snippets/{open(SNIP).read().strip()}', body, 'PUT')
    else:
        r = req(f'{B}/code-snippets/v1/snippets', body, 'POST')
        if r and r.get('id'): open(SNIP, 'w').write(str(r['id']))
    print('snippet', r.get('id'), 'active', r.get('active'), (r.get('code_error') or ''))
    # /athletes/ page: the shortcode inside the site header and footer
    pg = req(f'{B}/wp/v2/pages?slug=athletes&status=publish,draft,private&context=edit&_fields=id,link')
    if not pg:
        pg = [req(f'{B}/wp/v2/pages', {'title': 'Athlete area', 'slug': 'athletes', 'status': 'publish', 'template': 'elementor_header_footer',
                                         'content': '<!-- wp:shortcode -->[cc_athletes]<!-- /wp:shortcode -->',
                                         'meta': {}}, 'POST')]
    print('page', pg[0].get('id'), pg[0].get('link'))
    shared = [p for p in (req(f'{B}/wp/v2/cc_athlete?status=private&per_page=100&context=edit&_fields=id,title,meta') or []) if isinstance(p, dict) and (p.get('meta') or {}).get('cc_shared')]
    hub = [p for p in shared if (p['meta'].get('cc_lang') or 'en') == 'en']
    hub_it = [p for p in shared if p['meta'].get('cc_lang') == 'it']
    if not hub:
        hub = [req(f'{B}/wp/v2/cc_athlete', {'title': 'Shared hub (all athletes)', 'status': 'private', 'content': HUB(), 'meta': {'cc_shared': True}}, 'POST')]
    elif '--hub' in sys.argv:   # upload the guides, then rewrite the shared hub from HUB above (overwrites edits made in WordPress)
        upload_guides(hub[0]['id'])
        req(f'{B}/wp/v2/cc_athlete/{hub[0]["id"]}', {'content': HUB()}, 'POST')
    print('hub', hub[0].get('id'), hub[0].get('message', ''))
    if not hub_it:
        hub_it = [req(f'{B}/wp/v2/cc_athlete', {'title': 'Shared hub (Italian athletes)', 'status': 'private', 'content': HUB_IT(), 'meta': {'cc_shared': True, 'cc_lang': 'it'}}, 'POST')]
    elif '--hub' in sys.argv:
        upload_guides_it(hub_it[0]['id'])
        req(f'{B}/wp/v2/cc_athlete/{hub_it[0]["id"]}', {'content': HUB_IT()}, 'POST')
    print('hub it', hub_it[0].get('id'), hub_it[0].get('message', ''))
    if '--availability' in sys.argv:   # the Portuguese, Slovenian and Slovak hubs go with hub-i18n.php
        for L, name in (('pt', 'Portuguese'), ('sl', 'Slovenian'), ('sk', 'Slovak')):
            hl = [p for p in shared if p['meta'].get('cc_lang') == L]
            if not hl:
                hl = [req(f'{B}/wp/v2/cc_athlete', {'title': f'Shared hub ({name} athletes)', 'status': 'private', 'content': hub_lang(L), 'meta': {'cc_shared': True, 'cc_lang': L}}, 'POST')]
            elif '--hub' in sys.argv:
                upload_guides_lang(hl[0]['id'], L)
                req(f'{B}/wp/v2/cc_athlete/{hl[0]["id"]}', {'content': hub_lang(L)}, 'POST')
            print('hub', L, hl[0].get('id'), hl[0].get('message', ''))

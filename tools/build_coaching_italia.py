"""/preparatore-di-ciclismo-italia/ rebuilt in the style of the UK/USA/Canada pages (Matteo 15 Nov), in Italian.

Kept (SEO, CLAUDE.md): URL, Yoast title/description, the first H1, every live H2 wording except the approved changes
(2025 -> 2026 IN NUMERI, as on every page; the reviews H2 -> LEGGI I NOSTRI CASI STUDIO, as on the English country
pages), the live copy (intro, why list, packages and their features, events, regions, all 6 FAQ questions and answers),
the live images with their live alt text, and the live payment links (Shopify for Base, GoCardless for Avanzato/Premium).
Changed: package cards with buy buttons (Premium: waiting list, as on every page), how it works in steps, the athlete
calendar, case studies, reviews strip, contact form. The live reviews were real testimonials shown under invented
Italian names (the same quotes appear under other names on the UK/USA/Canada pages): replaced by real testimonials,
translated from English, with the athletes' real names.
  python3 tools/build_coaching_italia.py
"""
import os, sys, re, io, contextlib, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_common import *
import build_coaching_generic as G
with contextlib.redirect_stdout(io.StringIO()):
    import build_coaching_packages as P
    import build_coaching_country as CN

NAME, PATH = 'preparatore-di-ciclismo-italia', '/preparatore-di-ciclismo-italia/'
T = open(ROOT + f'coaching/text/{NAME}.txt').read()
L = T.split('\n')
SRC = open(ROOT + f'coaching/html/{NAME}.html', encoding='utf-8').read()
txt = lambda s: ' '.join(H.unescape(re.sub(r'<[^>]+>', ' ', s)).split())
md = lambda s: re.sub(r'\*\*([^*]+?)\*\*', r'<b>\1</b>', E(s.replace('**\n\n**', '').strip()).replace('&amp;', '&').replace('&', '&amp;')).replace('&amp;amp;', '&amp;')
def block(h, stop=('H2:', 'H1:')):
    out, on = [], False
    for l in L:
        if l.startswith(h): on = True; continue
        if on and l.startswith(stop): break
        if on: out.append(l)
    return out
P_ = lambda ls: [l[3:].strip() for l in ls if l.startswith('P: ')]
LI = lambda ls: [l[4:].strip().replace('**', '').strip() if l.count('**') % 2 else l[4:].strip() for l in ls if l.startswith('LI: ')]

intro = P_(L[1:10])
why = LI(block("H2: Perche' atleti"))
ev = block('H2: Gli Eventi'); ev_p, ev_li = P_(ev), LI(ev)
rg = block('H2: Seguiamo ciclisti'); rg_p, rg_li = P_(rg), LI(rg)
rg_li += ['**Puglia** — Bari, Lecce', '**Sicilia** — Palermo, Catania', '**Sardegna** — Cagliari, Sassari']   # Matteo 15 Nov: the south and the islands too
nums = re.findall(r'H3: (.+)\nH4: (.+)', '\n'.join(block('H2: 2025 IN NUMERI', ('H2:', 'H1:'))))
faq_live = []
fl = block('H2: DOMANDE FREQUENTI', ('H1:',))
for i, l in enumerate(fl):
    if l.startswith('TXT: '): faq_live.append((l[5:].strip(), []))
    elif l.startswith('P: ') and faq_live: faq_live[-1][1].append(l[3:].strip())
assert len(faq_live) == 6, faq_live
end_h2 = next(l[4:] for l in L if l.startswith('H2: Un coaching personalizzato'))

# package features, in the live order, with Base's "not included" lines (class="excluded" on the live page)
lis = [(c, txt(t)) for c, t in re.findall(r'<li[^>]*class="([^"]*(?:in|ex)cluded[^"]*)"[^>]*>(.*?)</li>', SRC, re.S)]
starts = [i for i, (c, t) in enumerate(lis) if t.startswith('Piano di allenamento giornaliero')]
assert len(starts) == 3, starts
groups = [lis[a:b] for a, b in zip(starts, starts[1:] + [len(lis)])]
FEAT = dict(zip(('base', 'avanzato', 'premium'), groups))
pay = {lab.strip(): u for u, lab in re.findall(r'<option value="(https://[^"\s]+)\s*"[^>]*>\s*([^<]+?)\s*<', SRC)}
PAY_B = next(u for k, u in pay.items() if k.startswith('Base')); PAY_A = next(u for k, u in pay.items() if k.startswith('Avanzato'))

FOR = {'base': 'Per chi sa seguire l’allenamento in autonomia, senza il contatto diretto con un coach.',
       'avanzato': 'Matteo come tuo coach: feedback settimanale, una chiamata al mese, analisi approfondita dei dati e Vekta incluso.',
       'premium': 'Il coaching più vicino: contatto, feedback e analisi ogni giorno, e una chiamata ogni settimana.'}
def card(key, h2, term, price, per, sub, buttons, badge='', cls=''):
    inc = [t for c, t in FEAT[key] if 'excluded' not in c]; no = [t for c, t in FEAT[key] if 'excluded' in c]
    items = ''.join(f'<li{" class=\"more\"" if i >= 12 else ""}>{E(x)}</li>' for i, x in enumerate(inc))
    if no:
        items += '<li class="more no-lab">Incluso in Avanzato e Premium</li>' + ''.join(f'<li class="more no">{E(x)}<span class="vh"> (non incluso nel Base)</span></li>' for x in no)
    first = re.search(r'<a [^>]*>.*?</a>', buttons).group(0).replace(' pay"', ' pay pay2"')
    return f'''<article class="pkg {cls}" id="pkg-{key}">
        {badge}
        <div class="pkg-term">{term}</div>
        <h2>{h2}</h2>
        <p class="pkg-for">{FOR[key]}</p>
        <div class="pkg-price"><b>{price}</b><span>{per}</span></div>
        <p class="pkg-sub">{sub}</p>
        <div class="pkg-buy">{buttons}<a class="pkg-call" href="{P.CAL}" {EXT}>Non sei sicuro? Prenota una consulenza gratuita →</a></div>
        <div class="pkg-lab">Cosa include</div>
        <ul class="ticks">{items}</ul>
        <button type="button" class="pkg-all" aria-expanded="false"><span>Vedi tutte le caratteristiche</span><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 8l5 5 5-5"/></svg></button>
        <div class="pkg-buy2">{first}</div>
      </article>'''
cards = ''.join([
    card('base', 'Base', '12 Settimane', '€19', '/sett', 'Addebitato con un pagamento unico di €228 per le 12 settimane.', P.btn('Acquista Base 12 Settimane · €228', PAY_B)),
    card('avanzato', 'Avanzato', 'Abbonamento di 6 mesi', '€149', '/mese', '', P.btn('Abbonati ad Avanzato · €149/mese', PAY_A),
         '<span class="pkg-badge">Mensile (Il Nostro Più Popolare)</span>', 'hot'),
    card('premium', 'Premium', 'Abbonamento di 3 mesi (€10 di sconto per 6 mesi)', '€249', '/mese', '',
         '<a class="btn btn-go pay" href="#contact" data-waitlist="Premium">Iscriviti alla lista d’attesa</a>'
         '<span class="pay-note">Premium 3 mesi €249/mese · 6 mesi €239/mese</span>', '', 'sold'),
])

# real testimonials, translated from English, real names (REVIEWS in coaching_common)
REV_IT = [(0, 'Non solo mi ha fatto innamorare del ciclismo, ma ha creduto in me anche quando io non ci credevo. Oggi sono campionessa europea Gran Fondo e gravel 19-34 e medaglia d’argento ai Mondiali Gran Fondo, avendo iniziato a pedalare solo lo scorso febbraio.'),
          (1, 'Con la sua competenza, il suo supporto e un approccio personalizzato, ho raggiunto il mio obiettivo di qualificarmi per i Campionati del Mondo UCI Gran Fondo.'),
          (5, 'Ogni settimana avevo un piano davvero su misura e, di conseguenza, mi sono presentato alla Mallorca 312 nella forma migliore di sempre.'),
          (7, 'Matteo Cigala è stato un coach incredibile: mi ha aiutato a organizzare l’allenamento intorno alla famiglia e al lavoro. Grazie a lui non solo ho raggiunto i miei obiettivi, ma ho anche registrato i miei record di potenza di sempre.'),
          (8, 'Non ho tempo da dedicare a ore di chilometri inutili, e Matteo ha ottimizzato alla perfezione il mio allenamento sul tempo che ho a disposizione.'),
          (6, 'Matteo ha portato la mia FTP da 220 W a 260 W in meno di 4 mesi e il mio sprint da circa 600 W a 920 W.')]
def rv_it(i, q):
    t, _, n, w, ph = REVIEWS[i]
    return (f'<figure class="rv"><div class="rv-stars" role="img" aria-label="5 stelle">★★★★★</div><blockquote>“{E(q)}”</blockquote>'
            f'<figcaption class="rv-txt"><div><b>Atleta seguito da Matteo</b><span>Recensione tradotta dall’inglese</span></div></figcaption></figure>')   # Matteo 15 Nov: no English names on the Italian page
strip = ('<div class="rv-wrap"><div class="rv-row" id="rv-row" tabindex="0" aria-label="Recensioni degli atleti">' + ''.join(rv_it(i, q) for i, q in REV_IT) + '</div>'
         '<div class="rv-nav"><button type="button" class="rv-btn" data-d="-1" aria-label="Recensioni precedenti">←</button><button type="button" class="rv-btn" data-d="1" aria-label="Recensioni successive">→</button></div></div>')
# the live page's review photos (live alt text kept): a photo row
LIVE_PICS = [(u, a) for u, q, a in re.findall(r"""<img (https://coaching\.cigalacycling\.com/wp-content/uploads/[^ ]+) alt=(['"])(.*?)\2>""", '\n'.join(block("H2: LEGGI LE NOSTRE RECENSIONI")))]
def up(u): return img(u.split('/uploads/')[1].rsplit('.', 1)[0].split('/', 2)[-1], 'italia-' + re.sub(r'[^a-z0-9]+', '-', u.rsplit('/', 1)[1].rsplit('.', 1)[0].lower())[:40])
pics = ''.join(f'<div class="photo it-pic"><img src="{up(u)}" alt="{E(a)}" loading="lazy"></div>' for u, a in LIVE_PICS)
assert len(LIVE_PICS) == 5, LIVE_PICS

# Matteo 15 Nov: the events as cards (name, place, discipline), more exciting than a list; live wording kept
TYPES = {'Strada': '#34c46a', 'Gravel': '#f0bf00', 'MTB': '#ff3d33', 'Ultra': '#a78bfa', 'Tutte le discipline': '#5f86c9'}
EV_T = {'Strade Bianche': 'Strada', 'Hero': 'MTB', 'Nove Colli': 'Strada', 'Maratona': 'Strada', 'Stelvio': 'Strada', 'Paganella': 'MTB',
        'Hills of Gravel': 'Gravel', 'Colnago': 'Strada', 'Mondiali': 'Tutte le discipline', 'Calendario FCI': 'Tutte le discipline'}
EV_IC = {'Strada': '<path d="M3 20 9 6l4 8 3-5 5 11z"/>', 'Gravel': '<circle cx="6" cy="17" r="2"/><circle cx="13" cy="15" r="1.5"/><circle cx="18" cy="18" r="2.5"/><path d="M2 21h20"/>',
         'Ultra': '<path d="M3 17c3-6 6 2 9-4s6-2 9-6"/><circle cx="3" cy="17" r="1.5"/><circle cx="21" cy="7" r="1.5"/>',
         'MTB': '<path d="m3 20 6-9 3 4 3-6 6 11z"/><path d="M14 6l1-3 2 1"/>', 'Tutte le discipline': '<circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/>'}
EV_MORE = ['**Campionato Italiano Gravel** (FCI)', '**Campionati Italiani Granfondo e Marathon** (FCI)', '**Serenissima Gravel** (Veneto) — UCI Gravel World Series',
           '**Nova Eroica** (Buonconvento, Siena)', '**L’Eroica** (Gaiole in Chianti)', '**Granfondo Il Lombardia** (Como)',
           '**Granfondo Tre Valli Varesine** (Varese)', '**Sportful Dolomiti Race** (Feltre)', '**Granfondo Campagnolo Roma** (Roma)',
           '**Tuscany Trail** (Toscana) — bikepacking, circa 500 km', '**Italy Divide** (da Pompei al Lago di Garda) — ultra gravel e bikepacking',
           '**Veneto Gravel** (Bassano del Grappa)', '**Dolomiti Superbike** (Villabassa, Alta Pusteria)', '**Capoliveri Legend Cup** (Isola d’Elba)', '**La Fausto Coppi** (Cuneo)', '**Granfondo Felice Gimondi** (Bergamo)']
EV_T.update({'Superbike': 'MTB', 'Capoliveri': 'MTB', 'Tuscany Trail': 'Ultra', 'Italy Divide': 'Ultra', 'Veneto Gravel': 'Gravel', 'Fausto Coppi': 'Strada', 'Gimondi': 'Strada', 'Gravel': 'Gravel', 'Eroica': 'Gravel', 'Granfondo e Marathon': 'Tutte le discipline', 'Lombardia': 'Strada', 'Tre Valli': 'Strada', 'Sportful': 'Strada', 'Campagnolo': 'Strada'})
WON = ('Strade Bianche', 'Campionato Italiano Gravel', 'Il Lombardia', 'Tre Valli Varesine', 'Mondiali, Europei')   # Mondiali/Europei: European Champion Gran Fondo 2022   # About page: Matteo's own wins
def ev_card(x):
    t = next((v for k, v in EV_T.items() if k in x), 'Strada'); c = TYPES[t]
    m = re.match(r'\*\*(.+?)\*\*\s*(.*)', x.replace('**\n\n**', '').strip())
    name, rest = (m.group(1).strip(), m.group(2).strip()) if m else (x.replace('**', '').strip(), '')
    pl = re.match(r'\(([^)]+)\)\s*(.*)', name + ' ' + rest) if False else None
    nm = re.match(r'(.+?)\s*\(([^)]+)\)$', name)
    if nm: name, rest = nm.group(1), f'({nm.group(2)}) {rest}'.strip()
    rest = rest.strip()
    won = '<span class="it-ev-won">★ Vinta da Matteo</span>' if any(w in name for w in WON) else ''
    return (f'<li data-t="{t}" style="--tc:{c}"><span class="it-ev-ic"><svg viewBox="0 0 24 24" aria-hidden="true">{EV_IC[t]}</svg></span><span class="it-ev-tag">{t}</span>'
            f'<b>{E(name)}</b>{won}{f"<span class=it-ev-pl>{E(rest.strip("() ").replace(") —", " —"))}</span>" if rest else ""}</li>')
# Matteo 15 Nov: the sample calendar in Italian too (same days and numbers as on the English pages)
CAL_IT = [('>Nutrition<', '>Nutrizione<'),
          ('Daily macronutrient intake: 300 g carbohydrates · 160 g protein · 75 g fat', 'Apporto giornaliero di macronutrienti: 300 g carboidrati · 160 g proteine · 75 g grassi'),
          ('Daily macronutrient intake: 560 g carbohydrates = 2,240 kcal (62.2%)', 'Apporto giornaliero di macronutrienti: 560 g carboidrati = 2.240 kcal (62,2%)'),
          ('4×6 min torque efforts alternating + bursts', '4×6 min di forza resistente alternati a scatti'),
          ('LDT + 3×10′ at SS, high cadence', 'LDT + 3×10′ in sweet spot, cadenza alta'),
          ('LDT 4h aim at 2000 m elevation', 'LDT 4h con obiettivo 2000 m di dislivello')]
def cal_it():
    h = P.NUT.cal_days(('21', '24', '26'))
    for a, b in CAL_IT:
        assert a in h, a
        h = h.replace(a, b)
    return h
# Matteo 15 Nov: a map of Italy in our style next to the regions (the list stays, for Google). Outline: Natural Earth
# 50m (public domain) via world-atlas; coaching/italy-map.json is made by a small script (outline + the listed cities).
import json as _json
def italy_map():
    m = _json.load(open(ROOT + 'coaching/italy-map.json'))
    vb = f"{m['minx'] - 10} {m['miny'] - 10} {m['w'] - m['minx'] + 20} {m['h'] - m['miny'] + 20}"
    dots = ''.join(f'<g class="it-city" style="--i:{i}"><circle cx="{x}" cy="{y}" r="9" class="it-halo"/><circle cx="{x}" cy="{y}" r="4"/><title>{E(n)}</title></g>' for i, (n, (x, y)) in enumerate(m['pts'].items()))
    labels = ''.join(f'<text x="{m["pts"][n][0] + dx}" y="{m["pts"][n][1] + dy}" class="it-lab" text-anchor="{a}">{n}</text>' for n, dx, dy, a in
                     [('Milano', 0, 24, 'middle'), ('Venezia', 12, 16, 'start'), ('Torino', -12, 5, 'end'), ('Bolzano', 12, -4, 'start'), ('Firenze', 12, -2, 'start'), ('Siena', -12, 10, 'end'),
                      ('Roma', 12, 5, 'start'), ('Napoli', 12, 5, 'start'), ('Bari', 12, -2, 'start'), ('Cagliari', 0, 22, 'middle'), ('Palermo', 0, -12, 'middle'), ('Catania', 12, 5, 'start')])
    return (f'<svg class="it-map" viewBox="{vb}" role="img" aria-labelledby="it-map-t"><title id="it-map-t">Mappa dell’Italia con le città dove seguiamo ciclisti</title>'
            f'<defs><linearGradient id="it-g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#009a44" stop-opacity=".35"/><stop offset="1" stop-color="#009a44" stop-opacity=".08"/></linearGradient>'
            f'<filter id="it-glow" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="6"/></filter></defs>'
            f'<path d="{m["d"]}" fill="#009a44" opacity=".35" filter="url(#it-glow)"/><path d="{m["d"]}" class="it-land" fill="url(#it-g)"/>'
            f'{dots}{labels}</svg>')
WHY_IC = ['<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>', '<path d="M13 2 3 14h9l-1 8 10-12h-9z"/>', '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
          '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>', '<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/>',
          '<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/>', '<path d="M12 2.7s6 6.6 6 11.3a6 6 0 0 1-12 0c0-4.7 6-11.3 6-11.3z"/>',
          '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10z"/><path d="M2 21c0-3 1.9-5.4 5.2-6.1C9.6 14.4 12 13 13 12"/>',
          '<path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 8.5 8.5 0 0 1-3.8-.9L3 21l1.9-5.7A8.5 8.5 0 1 1 21 11.5z"/>']
FACTS = [('clock', 'Comunicazione in italiano', 'Parli direttamente con Matteo, nella tua lingua, per chiamate, feedback e domande.'),
         ('currency', 'Prezzi in euro', 'Paghi in euro: nessun costo di cambio.'),
         ('route', 'Costruito sulle tue strade', 'Dolomiti, Appennini, gravel o pianura: il piano segue il tuo territorio e il tuo calendario gare.')]
facts = ''.join(f'<div class="note"><svg viewBox="0 0 24 24" aria-hidden="true">{CN.IC[i]}</svg><p><b>{E(t)}</b><br>{E(d)}</p></div>' for i, t, d in FACTS)
STEPS = [('Iscriviti o parlane prima', 'Scegli il pacchetto e iscriviti subito, oppure prenota prima una consulenza gratuita con Matteo.'),
         ('Test e zone', 'Ogni pacchetto parte con i test (CP, FTP, FTHR o INSCYD) per impostare le zone. Con Avanzato e Premium Matteo analizza anche a fondo i tuoi dati degli ultimi 6–12 mesi.'),
         ('Il tuo piano', 'Le sessioni arrivano su Vekta o TrainingPeaks e si sincronizzano con Garmin, Wahoo, Hammerhead o Zwift.'),
         ('Feedback', 'Con Avanzato e Premium Matteo rivede le tue sessioni (ogni settimana o ogni giorno) e adatta il piano a lavoro, famiglia e meteo.'),
         ('Nutrizione, se vuoi', 'Aggiungi il coaching nutrizionale 1-to-1 con la nostra nutrizionista sportiva Marine Lenehan (WorldTour Pro): macro giornalieri, carboidrati per ora e note nello stesso calendario.')]
how = ''.join(f'<li class="cn-day"><div class="cn-num"><span><small>STEP</small>{i + 1}</span></div><div class="panel cn-box"><h3 class="h-sm">{E(t)}</h3><p>{E(d)}</p></div></li>' for i, (t, d) in enumerate(STEPS))
NUT_Q = ('Posso lavorare 1-to-1 con una nutrizionista?', ['Sì. Puoi aggiungere il coaching nutrizionale con la nostra nutrizionista sportiva, Marine Lenehan: WorldTour Pro con LIDL-TREK, 2 volte campionessa nazionale irlandese e campionessa del mondo amatori gravel 2024. Scrive i tuoi macro giornalieri, i carboidrati per ora e le note nutrizionali nello stesso calendario del tuo allenamento, rivede il tuo diario alimentare e pianifica l’alimentazione in gara e il gut training. Il prezzo dipende da ciò che ti serve ed è concordato con Marine.'])
faq = faq_live + [NUT_Q]
faq_html = ''.join(f'<details{" open" if i == 0 else ""}><summary><h3>{E(q)}</h3></summary>' + ''.join(f'<p>{E(p)}</p>' for p in ps) + '</details>' for i, (q, ps) in enumerate(faq))
nums_html = ''.join(f'<div class="stat"><h3 class="n" data-count="{E(n)}">{E(n)}</h3><h4 class="l">{E(l)}</h4></div>' for n, l in nums)
chips = lambda xs, cls: f'<ul class="{cls}">' + ''.join(f'<li>{md(x)}</li>' for x in xs) + '</ul>'
hsrc = img('IMG_3999AWDWWWU', 'italia-hero-team')

MAIN = f'''<div class="hero hero-sm">
  <img src="{hsrc}" alt="{E(live_alt('IMG_3999AWDWWWU'))}" style="object-position: 50% 45%">
  <div class="in">
    <div class="eyebrow eb-pill"><span class="dot"></span>Allenatore di ciclismo online</div>
    <h1>PREPARATORE DI CICLISMO ITALIA</h1>
    <p class="lede">Preparati con il preparatore di ciclismo <a href="{C}/about/" {EXT}>Matteo Cigala</a> — ovunque tu sia in Italia.</p>
    <div class="ctas"><a class="btn btn-go" href="{P.CAL}" {EXT}>Prenota una consulenza gratuita</a><a class="btn btn-ghost" href="#packages">Vedi i pacchetti ↓</a></div>
  </div>
</div>

<section class="it-intro-sec">
  <div class="in it-intro">
    <div class="it-me"><img src="{conv('coaching/brand/matteo-cigala-author-signature.webp', 'italia-matteo-firma')}" alt="Matteo Cigala, preparatore di ciclismo, con la maglia bianca Cigala Cycling e la sua firma" loading="lazy" width="720" height="943"></div>
    <div class="gn-txt">
      <div class="eyebrow">Il tuo coach</div>
      <ul class="it-nums">{''.join(f'<li><b>{a}</b><span>{b}</span></li>' for a, b in (('28+', 'anni nel ciclismo'), ('10+', 'anni da preparatore'), ('200+', 'vittorie')))}</ul>
      <p>{E(intro[1])}</p>
      {''.join(f'<p>{E(x)}</p>' for x in intro[2:])}
    </div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Perché sceglierci</div><h2>{E("Perche' atleti in Italia scelgono Matteo Cigala")}</h2><div class="bar"></div></div></div>
    <ul class="it-why">{''.join(f'<li><svg viewBox="0 0 24 24" aria-hidden="true">{WHY_IC[i % len(WHY_IC)]}</svg><span>{md(x)}</span></li>' for i, x in enumerate(why))}</ul>
  </div>
</section>

<section id="packages">
  <div class="in">
    <div class="head"><div><div class="eyebrow">Scegli il tuo pacchetto</div><h2>PACCHETTI DI PREPARAZIONE</h2><div class="bar"></div></div></div>
    <div class="pkgs">{cards}</div>
    <p class="terms"><b>Iscrivendoti a uno dei nostri pacchetti, accetti i nostri Termini e Condizioni. Consulta i Termini e Condizioni <a href="{C}/terms-conditions/" {EXT}>QUI</a></b></p>
    <div class="vk-logos cn-tp">
      <a class="vk-lock" href="https://joinvekta.com/partnerships" {EXT} aria-label="{E(live_alt('SDFASDFASDF'))}"><img src="{LOGO}" alt="" loading="lazy" width="64" height="64"><svg class="vk-x" viewBox="0 0 20 20" aria-hidden="true"><path d="M4 4l12 12M16 4L4 16"/></svg><img src="{P.VKLOGO}" alt="{E(live_alt('SDFASDFASDF'))}" loading="lazy" width="531" height="139"></a>
      <span><img src="{P.TPLOGO}" alt="{E(live_alt('PfNJBaCPkS_eSn5J'))}" loading="lazy"></span>
    </div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Come si inizia</div><h3 class="h-sec">COME FUNZIONA</h3><div class="bar"></div></div></div>
    <div class="cn-howgrid">
      <ol class="cn-days">{how}</ol>
      <figure class="nu-cal pk-cal cn-cal">
        <div class="cal-scroll" tabindex="0" aria-label="Giorni di esempio dal calendario di un atleta, con la nutrizione"><div class="cal-row">{cal_it()}</div></div>
        <figcaption>Giorni di esempio dal calendario di un atleta: le tue sessioni e, con il coaching nutrizionale, le note di Marine e i carboidrati per ora. <a href="{C}/nutrition/#upgrade" {EXT}>Scopri il coaching nutrizionale →</a></figcaption>
      </figure>
    </div>
  </div>
</section>

<section>
  <div class="in">
    <div class="it-motto"><p class="it-motto-t">ALLENATI CON METODO, VAI PIÙ FORTE</p><h2 class="it-motto-h">{E("E' il nostro motto")}</h2></div>
    <div class="head"><div><div class="eyebrow">Cosa dicono i nostri atleti</div><h2>LEGGI LE NOSTRE RECENSIONI</h2><div class="bar"></div></div>
      <div class="rv-links"><a class="arrow-link" href="{GOOGLE_REVIEWS}" {EXT}><span class="gstar" aria-hidden="true">★</span> Le nostre recensioni su Google →</a></div></div>
    <p class="cn-lede">Scopri cosa dicono i ciclisti di Cigala Cycling: recensioni reali di atleti seguiti da Matteo.</p>
    {strip}
    <div class="it-pics">{pics}</div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Stampa e partners</div><h2>PRESENTE SU</h2><div class="bar"></div></div></div>
    {seen_logos()}
  </div>
</section>

<section class="it-ev">
  <div class="in">
    <div class="it-ev-top">
      <div class="it-ev-pic"><img src="{img('imgi_25_F42ZwHhq', 'italia-strade-bianche-estate')}" alt="Matteo Cigala vince la Medio Fondo Strade Bianche in Piazza del Campo, Siena, a braccia alzate" loading="lazy"><span>Matteo vince la Medio Fondo Strade Bianche, Siena</span></div>
      <div class="gn-txt">
        <div class="eyebrow">Il tuo obiettivo</div>
        <h2>Gli Eventi per Cui Prepariamo i Nostri Atleti</h2><div class="bar"></div>
        <p>{E(ev_p[0])}</p>
        <div class="it-ev-types" role="group" aria-label="Filtra per disciplina"><button type="button" class="on" data-f="" style="--tc:#d0d6e0">Tutti</button>{''.join(f'<button type="button" data-f="{t}" style="--tc:{c}">{t}</button>' for t, c in TYPES.items())}</div>
      </div>
    </div>
    <ul class="it-ev-grid">{''.join(ev_card(x) for x in ev_li + EV_MORE)}</ul>
    {''.join(f'<p class="it-ev-note">{E(x)}</p>' for x in ev_p[1:])}
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Risultati</div><h2>2026 IN NUMERI</h2><div class="bar"></div></div></div>
    <div class="stats nums">{nums_html}</div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head">
      <div><div class="eyebrow">Risultati reali</div><h2>LEGGI I NOSTRI CASI STUDIO</h2><div class="bar"></div></div>
      <div class="rv-links"><a class="btn btn-go" href="{C}/case-studies/" {EXT}>Leggi i nostri casi studio</a></div>
    </div>
    {case_cards(C + '/case-studies/', 'it')}
  </div>
</section>

<section>
  <div class="in split">
    <div class="gn-txt">
      <div class="eyebrow">Dove alleniamo</div>
      <h2>Seguiamo ciclisti in tutta Italia</h2><div class="bar"></div>
      <p>{E(rg_p[0])}</p>
      {chips(rg_li, 'cn-regions')}
    </div>
    <div class="it-map-wrap">{italy_map()}</div>
  </div>
  <div class="in it-devs">
    <div class="eyebrow">Compatibile con i tuoi dispositivi e app</div>
    <div class="logos apps cn-apps">{P.devices}</div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Buono a sapersi</div><h2>DOMANDE FREQUENTI</h2><div class="bar"></div></div></div>
    <div class="faq">{faq_html}</div>
  </div>
</section>

<section>
  <div class="in">
    <div class="band band-cta">
      <img src="{img('unnamed-8-1.jpg', 'matteo-worlds-silver')}" alt="{E(live_alt('unnamed-8-1.jpg'))}" loading="lazy" width="1280" height="1600">
      <div class="tx">
        <div class="eyebrow">Inizia a collaborare con Matteo</div>
        <h2>{E(end_h2)}</h2>
        <div class="bar"></div>
        <div class="ctas"><a class="btn btn-go" href="{P.CAL}" {EXT}>Prenota una consulenza gratuita</a><a class="btn btn-ghost" href="#packages">Vedi i pacchetti</a></div>
      </div>
    </div>
  </div>
</section>

<section id="contact" data-lang="it" data-subject="Messaggio dalla pagina Preparatore di Ciclismo Italia (Coaching website)" data-msg="Il tuo messaggio *">
  <div class="in split">
    <div class="photo rider"><img src="{img(G.CONTACT_PHOTO[0], G.CONTACT_PHOTO[1])}" alt="{E(live_alt(G.CONTACT_PHOTO[0]))}" loading="lazy" width="1440" height="1081"></div>
    <div>
      <div class="eyebrow">Contatti</div>
      <h3 class="h-sec">VUOI FARE IL SALTO DI QUALITÀ?</h3>
      <div class="bar"></div>
      <p class="lede">Hai domande sulla preparazione? Scrivici e Matteo ti risponderà, in italiano.</p>
      <form class="form panel" method="post" action="#" onsubmit="return false">
        <label>Nome<input name="form_fields[name]" type="text" placeholder="Nome *" required autocomplete="name"></label>
        <label>Email<input name="form_fields[email]" type="email" placeholder="Email *" required autocomplete="email"></label>
        <label>Telefono<input name="form_fields[phone]" type="tel" placeholder="Telefono (con prefisso) *" required autocomplete="tel"></label>
        <label>Messaggio<textarea name="form_fields[message]" placeholder="Il tuo messaggio *" rows="5" required></textarea></label>
        <button class="btn btn-go" type="submit">Invia &gt;</button>
      </form>
    </div>
  </div>
</section>'''

EV_JS = """<script>(function(){var bs=document.querySelectorAll('.it-ev-types button');bs.forEach(function(b){b.addEventListener('click',function(){
var f=b.dataset.f;bs.forEach(function(x){x.classList.toggle('on',x===b);});
document.querySelectorAll('.it-ev-grid li').forEach(function(li){li.classList.toggle('off',!!f&&li.dataset.t!==f);});});});})();</script>"""
IT_NL = """<script>(function(){function go(){var b=document.querySelector('.nl-band');if(!b)return;
var m={'.nl-eyebrow':'Newsletter','.nl-t':'Resta aggiornato','.nl-d':'Consigli di allenamento, novità, articoli e offerte su coaching, viaggi in bici e il nostro shop.','.nl-sr':'Indirizzo email'};
for(var k in m){var e=b.querySelector(k);if(e)e.textContent=m[k];}
var i=b.querySelector('input[type=email]');if(i)i.placeholder='Il tuo indirizzo email';var bt=b.querySelector('button[type=submit]');if(bt)bt.textContent='Iscriviti';
var n=b.querySelector('.nl-note');if(n)n.innerHTML='Una sola newsletter Cigala Cycling per tutti i nostri siti. Niente spam, puoi cancellarti quando vuoi. <a href="/privacy-policy/">Privacy policy</a>';
var msg=b.querySelector('.nl-msg');if(msg)new MutationObserver(function(){var t=msg.textContent,r={'Please enter a valid email address.':'Inserisci un indirizzo email valido.','Thanks, you’re subscribed! Watch your inbox for our next update.':'Grazie, sei iscritto! Controlla la tua casella per il prossimo aggiornamento.','Please try again.':'Riprova, per favore.'};
for(var k in r){if(t.indexOf(k)>-1&&t!==r[k]){msg.textContent=r[k];}}}).observe(msg,{childList:true,characterData:true,subtree:true});}
if(document.readyState!=='loading')go();else document.addEventListener('DOMContentLoaded',go);})();</script>"""
JS = REVIEWS_JS + G.NUMS_JS + IT_NL + EV_JS + """<script>(function(){document.querySelectorAll('.pkg-all').forEach(function(b){b.addEventListener('click',function(){
var o=!b.closest('.pkg').classList.contains('open');document.querySelectorAll('.pkg').forEach(function(p){p.classList.toggle('open',o);});
document.querySelectorAll('.pkg-all').forEach(function(x){x.setAttribute('aria-expanded',o);x.querySelector('span').textContent=o?'Mostra meno':'Vedi tutte le caratteristiche';});});});
document.querySelectorAll('[data-waitlist]').forEach(function(a){a.addEventListener('click',function(){var m=document.querySelector('#contact textarea');if(m&&!m.value)m.value='Vorrei entrare nella lista d\\u2019attesa del pacchetto '+a.dataset.waitlist+'.';});});})();</script>"""
ITCSS = '''<style>
.it-ev-top { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: 36px; align-items: center; margin-bottom: 26px; }
@media (max-width: 900px) { .it-ev-top { grid-template-columns: 1fr; gap: 20px; } }
.it-ev-pic { position: relative; border-radius: 16px; overflow: hidden; aspect-ratio: 4 / 3; border: 1px solid var(--border); }
.it-ev-pic img { width: 100%; height: 100%; object-fit: cover; object-position: 50% 40%; display: block; }
.it-ev-pic span { position: absolute; left: 0; right: 0; bottom: 0; padding: 30px 14px 12px; background: linear-gradient(transparent, rgba(8,9,10,.9)); font-size: 13px; color: var(--text); }
.it-ev-types { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.it-ev-types button { font-family: var(--body); background: transparent; cursor: pointer; transition: background .2s, color .2s; }
.it-ev-types button:hover, .it-ev-types button.on { background: var(--tc); color: #0f1011 !important; }
.it-ev-grid li.off { display: none; }
.it-ev-types button { padding: 5px 12px; border-radius: 999px; border: 1px solid var(--tc); color: var(--text); font-size: 12px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
.it-ev-grid { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
.it-ev-grid li { position: relative; display: grid; gap: 6px; align-content: start; padding: 18px; border: 1px solid var(--border); border-radius: 14px; background: linear-gradient(160deg, color-mix(in srgb, var(--tc) 12%, transparent), transparent 60%), var(--panel); transition: transform .25s, border-color .25s, box-shadow .25s; }
.it-ev-grid li:hover { transform: translateY(-4px); border-color: var(--tc); box-shadow: 0 16px 40px color-mix(in srgb, var(--tc) 22%, transparent); }
.it-ev-ic svg { width: 30px; height: 30px; fill: none; stroke: var(--tc); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.it-ev-tag { position: absolute; top: 16px; right: 16px; font-size: 10.5px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--tc); }
.it-ev-grid b { font: 400 20px/1.15 var(--head); text-transform: uppercase; color: var(--text); }
.it-ev-pl { font-size: 13.5px; color: var(--text-2); line-height: 1.45; }
.it-intro-sec { padding-top: 24px !important; }   /* Matteo 15 Nov: photo a little closer to the hero */
.it-intro { display: grid; grid-template-columns: minmax(0, 4fr) minmax(0, 7fr); gap: 40px; align-items: center; }
@media (max-width: 900px) { .it-intro { grid-template-columns: 1fr; } .it-me { max-width: 280px; margin: 0 auto; } }
.it-me img { width: 100%; height: auto; display: block; filter: drop-shadow(0 24px 50px rgba(0,0,0,.5)); }
.it-nums { list-style: none; margin: 10px 0 18px; padding: 0; display: flex; flex-wrap: wrap; gap: 10px 26px; }
.it-nums li { display: grid; }
.it-nums b { font: 400 clamp(34px, 4vw, 48px)/1 var(--head); color: var(--green-text); }
.it-nums span { font-size: 12px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--text-3); }
.it-lead { font-size: 18px !important; color: var(--text) !important; line-height: 1.55; }
.it-facts { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-top: 28px; }
.it-facts .note { padding: 16px 18px; border: 1px solid var(--border); border-radius: 14px; background: var(--panel-grad), var(--panel); }
@media (max-width: 800px) { .it-facts { grid-template-columns: 1fr; } }
.it-why { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
@media (max-width: 900px) { .it-why { grid-template-columns: repeat(2, minmax(0, 1fr)); } } @media (max-width: 560px) { .it-why { grid-template-columns: 1fr; } }
.it-why li { display: grid; gap: 10px; align-content: start; padding: 18px; border: 1px solid var(--border); border-radius: 14px; background: var(--panel-grad), var(--panel); font-size: 15px; line-height: 1.5; color: var(--text-2); transition: transform .25s, border-color .25s; }
.it-why li:hover { transform: translateY(-3px); border-color: var(--green); }
.it-why b { color: var(--text); }
.it-why svg { width: 40px; height: 40px; padding: 9px; border-radius: 10px; background: var(--green-wash); fill: none; stroke: var(--green-text); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.it-map-wrap { display: grid; place-items: center; }
.it-map { width: 100%; max-width: 440px; height: auto; overflow: visible; }
.it-land { stroke: #34c46a; stroke-width: 1.6; stroke-linejoin: round; }
.it-city circle { fill: #ff3d33; }
.it-city .it-halo { fill: rgba(255,61,51,.25); transform-box: fill-box; transform-origin: center; animation: it-pulse 2.4s ease-out infinite; animation-delay: calc(var(--i) * .15s); }
@keyframes it-pulse { 0% { transform: scale(.6); opacity: 1; } 100% { transform: scale(2.2); opacity: 0; } }
@media (prefers-reduced-motion: reduce) { .it-city .it-halo { animation: none; } }
.it-lab { fill: #d0d6e0; font: 600 13px var(--body); paint-order: stroke; stroke: #0f1011; stroke-width: 3px; }
.it-devs { margin-top: 36px; }
.it-ev-won { justify-self: start; padding: 3px 9px; border-radius: 999px; background: rgba(240,191,0,.14); color: #f0bf00; font-size: 11px; font-weight: 700; letter-spacing: .04em; }
.it-motto { text-align: center; margin: 0 auto 48px; padding: 34px 20px; border-radius: 18px; border: 1px solid var(--border); background: radial-gradient(600px 200px at 50% 0%, rgba(0,154,68,.22), transparent 70%), var(--panel); }
.it-motto-t { margin: 0; font: 400 clamp(30px, 5vw, 60px)/1 var(--head); color: var(--text); letter-spacing: .01em; }
.it-motto-h { margin: 12px 0 0 !important; font: 600 14px/1.3 var(--body) !important; letter-spacing: .16em !important; text-transform: uppercase; color: var(--green-text) !important; }
.it-ev-note { margin: 18px 0 0; color: var(--text-2); max-width: 80ch; }
/* Italian on this page: the shared parts (sold-out stamp, newsletter band) */
.pkg.sold::after { content: "ESAURITO" !important; }
.it-pics { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; margin-top: 18px; }
.it-pic { aspect-ratio: 1 / 1; margin: 0; }
.it-pic img { width: 100%; height: 100%; object-fit: cover; }
@media (max-width: 700px) { .it-pics { grid-template-columns: repeat(3, minmax(0, 1fr)); } .it-pics .it-pic:nth-child(n+4) { display: none; } }
</style>'''

# Matteo 15 Nov: the Italian page in the first person ("agli italiani piace la prima persona"); his name stays where it
# matters for search (H1 area, the H2 "Perche' atleti in Italia scelgono Matteo Cigala", the hero line). Quotes untouched.
FIRST = [("vittorie, Matteo offre una preparazione", "vittorie, offro una preparazione"), ("Perché sceglierci", "Perché scegliere me"),
         ("Comunicazione diretta in italiano con Matteo", "Comunicazione diretta in italiano con me"), ("Matteo come tuo coach:", "Io come tuo coach:"),
         ("consulenza gratuita con Matteo.", "consulenza gratuita con me."), ("Con Avanzato e Premium Matteo analizza anche", "Con Avanzato e Premium analizzo anche"),
         ("Con Avanzato e Premium Matteo rivede le tue sessioni (ogni settimana o ogni giorno) e adatta", "Con Avanzato e Premium rivedo le tue sessioni (ogni settimana o ogni giorno) e adatto"),
         ("con la nostra nutrizionista sportiva Marine Lenehan", "con la nutrizionista sportiva con cui lavoro, Marine Lenehan"),
         ("con la nostra nutrizionista sportiva, Marine Lenehan", "con la nutrizionista sportiva con cui lavoro, Marine Lenehan"),
         ("E&#x27; il nostro motto", "È il mio motto"), ("Cosa dicono i nostri atleti", "Cosa dicono i miei atleti"),
         ("LEGGI LE NOSTRE RECENSIONI", "LEGGI LE MIE RECENSIONI"), ("Le nostre recensioni su Google", "Le mie recensioni su Google"),
         ("recensioni reali di atleti seguiti da Matteo.", "recensioni reali degli atleti che alleno."),
         ("Gli Eventi per Cui Prepariamo i Nostri Atleti", "Gli Eventi per Cui Preparo i Miei Atleti"), ("Prepariamo atleti per granfondo", "Preparo atleti per granfondo"),
         ("Costruiamo anche il piano dei nostri atleti italiani", "Costruisco anche il piano dei miei atleti italiani"),
         ("Obbiettivi raggiunti dai nostri atleti", "Obiettivi raggiunti dai miei atleti"),
         ("LEGGI I NOSTRI CASI STUDIO", "LEGGI I MIEI CASI STUDIO"), ("Leggi i nostri casi studio", "Leggi i miei casi studio"),
         ("Dove alleniamo", "Dove alleno"), ("Seguiamo ciclisti in tutta Italia</h2>", "Seguo ciclisti in tutta Italia</h2>"),
         ("Matteo segue da remoto atleti in tutta Italia", "Seguo da remoto atleti in tutta Italia"), ("dove seguiamo ciclisti", "dove seguo ciclisti"),
         ("perché include accesso settimanale a Matteo oltre", "perché include un contatto settimanale con me oltre"), ("No. Seguiamo ciclisti", "No. Seguo ciclisti"),
         ("Inizia a collaborare con Matteo", "Inizia a collaborare con me"),
         ("Seguiamo ciclisti in tutta Italia e in tutto il mondo.", "Seguo ciclisti in tutta Italia e in tutto il mondo."),
         ("Hai domande sulla preparazione? Scrivici e Matteo ti risponderà, in italiano.", "Hai domande sulla preparazione? Scrivimi."),
         ("Iscrivendoti a uno dei nostri pacchetti", "Iscrivendoti a uno dei miei pacchetti")]
for _a, _b in FIRST:
    assert _a in MAIN, _a
    MAIN = MAIN.replace(_a, _b)

if __name__ == '__main__':
    build(NAME, PATH, MAIN, f'{PATH} rebuilt like the UK/USA/Canada pages, in Italian: package cards and buy buttons, steps, calendar, case studies, real reviews, form.',
          h1='PREPARATORE DI CICLISMO ITALIA',
          h2_changes={'drop': ['2025 IN NUMERI', 'LEGGI LE NOSTRE RECENSIONI – SCOPRI COSA DICONO I CICLISTI DI CIGALA CYCLING', "E' il nostro motto",
                               'Gli Eventi per Cui Prepariamo i Nostri Atleti', 'Seguiamo ciclisti in tutta Italia',
                               'Un coaching personalizzato in base ai tuoi obiettivi. Seguiamo ciclisti in tutta Italia e in tutto il mondo.'],
                      'add': ['2026 IN NUMERI', 'LEGGI I MIEI CASI STUDIO', 'LEGGI LE MIE RECENSIONI', 'È il mio motto', 'Gli Eventi per Cui Preparo i Miei Atleti',
                              'Seguo ciclisti in tutta Italia', 'Un coaching personalizzato in base ai tuoi obiettivi. Seguo ciclisti in tutta Italia e in tutto il mondo.']},   # Matteo 15 Nov: first person
          extra_css=G.GCSS + P.PCSS + FT_CSS + CS_CSS + P.CAL_CSS + CN.CCSS + ITCSS, extra_js=JS)
    print('faq', len(faq), '| why', len(why), '| events', len(ev_li), '| regions', len(rg_li), '| features', {k: len(v) for k, v in FEAT.items()})

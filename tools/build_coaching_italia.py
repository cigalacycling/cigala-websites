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
    <div class="eyebrow eb-pill"><span class="dot"></span>Preparazione ciclistica online</div>
    <h1>PREPARATORE DI CICLISMO ITALIA</h1>
    <p class="lede">Preparati con il preparatore di ciclismo <a href="{C}/about/" {EXT}>Matteo Cigala</a> — ovunque tu sia in Italia.</p>
    <div class="ctas"><a class="btn btn-go" href="{P.CAL}" {EXT}>Prenota una consulenza gratuita</a><a class="btn btn-ghost" href="#packages">Vedi i pacchetti ↓</a></div>
  </div>
</div>

<section>
  <div class="in split">
    <div class="gn-txt">
      <div class="eyebrow">Il tuo coach</div>
      {''.join(f'<p>{E(x)}</p>' for x in intro[1:])}
    </div>
    <div class="notes cn-facts">{facts}</div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Perché sceglierci</div><h2>{E("Perche' atleti in Italia scelgono Matteo Cigala")}</h2><div class="bar"></div></div></div>
    <div class="gn-txt cn-why"><ul class="ticks">{''.join(f'<li>{md(x)}</li>' for x in why)}</ul></div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Cosa dicono i nostri atleti</div><h2>{E("E' il nostro motto")}</h2><div class="bar"></div></div>
      <div class="rv-links"><a class="arrow-link" href="{GOOGLE_REVIEWS}" {EXT}><span class="gstar" aria-hidden="true">★</span> Le nostre recensioni su Google →</a></div></div>
    <p class="cn-lede">Recensioni reali di atleti seguiti da Matteo.</p>
    {strip}
    <div class="it-pics">{pics}</div>
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
        <div class="cal-scroll" tabindex="0" aria-label="Giorni di esempio dal calendario di un atleta, con la nutrizione"><div class="cal-row">{P.NUT.cal_days(('21', '24', '26'))}</div></div>
        <figcaption>Giorni di esempio dal calendario di un atleta: le tue sessioni e, con il coaching nutrizionale, le note di Marine e i carboidrati per ora. <a href="{C}/nutrition/#upgrade" {EXT}>Scopri il coaching nutrizionale →</a></figcaption>
      </figure>
    </div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Stampa e partner</div><h2>PRESENTE SU</h2><div class="bar"></div></div></div>
    {seen_logos()}
  </div>
</section>

<section>
  <div class="in">
    <div class="gn-txt">
      <div class="eyebrow">Il tuo obiettivo</div>
      <h2>Gli Eventi per Cui Prepariamo i Nostri Atleti</h2><div class="bar"></div>
      <p>{E(ev_p[0])}</p>
      {chips(ev_li, 'cn-chips')}
      {''.join(f'<p>{E(x)}</p>' for x in ev_p[1:])}
    </div>
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
    {case_cards(C + '/case-studies/')}
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
    <div>
      <div class="eyebrow">Compatibile con i tuoi dispositivi e app</div>
      <div class="logos apps cn-apps">{P.devices}</div>
    </div>
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

JS = REVIEWS_JS + G.NUMS_JS + """<script>(function(){document.querySelectorAll('.pkg-all').forEach(function(b){b.addEventListener('click',function(){
var o=!b.closest('.pkg').classList.contains('open');document.querySelectorAll('.pkg').forEach(function(p){p.classList.toggle('open',o);});
document.querySelectorAll('.pkg-all').forEach(function(x){x.setAttribute('aria-expanded',o);x.querySelector('span').textContent=o?'Mostra meno':'Vedi tutte le caratteristiche';});});});
document.querySelectorAll('[data-waitlist]').forEach(function(a){a.addEventListener('click',function(){var m=document.querySelector('#contact textarea');if(m&&!m.value)m.value='Vorrei entrare nella lista d\\u2019attesa del pacchetto '+a.dataset.waitlist+'.';});});})();</script>"""
ITCSS = '''<style>
.it-pics { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; margin-top: 18px; }
.it-pic { aspect-ratio: 1 / 1; margin: 0; }
.it-pic img { width: 100%; height: 100%; object-fit: cover; }
@media (max-width: 700px) { .it-pics { grid-template-columns: repeat(3, minmax(0, 1fr)); } .it-pics .it-pic:nth-child(n+4) { display: none; } }
</style>'''

if __name__ == '__main__':
    build(NAME, PATH, MAIN, f'{PATH} rebuilt like the UK/USA/Canada pages, in Italian: package cards and buy buttons, steps, calendar, case studies, real reviews, form.',
          h1='PREPARATORE DI CICLISMO ITALIA',
          h2_changes={'drop': ['2025 IN NUMERI', 'LEGGI LE NOSTRE RECENSIONI – SCOPRI COSA DICONO I CICLISTI DI CIGALA CYCLING'], 'add': ['2026 IN NUMERI', 'LEGGI I NOSTRI CASI STUDIO']},
          extra_css=G.GCSS + P.PCSS + FT_CSS + CS_CSS + P.CAL_CSS + CN.CCSS + ITCSS, extra_js=JS)
    print('faq', len(faq), '| why', len(why), '| events', len(ev_li), '| regions', len(rg_li), '| features', {k: len(v) for k, v in FEAT.items()})

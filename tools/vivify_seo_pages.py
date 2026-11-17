"""New SEO pages for vivifysports.com (16 Nov 2026), called by tools/build_vivify.py.

Matteo: "make sure her site ranks high for sports nutritionist and cycling sports nutritionist, especially in Ireland",
plus pages for her international audience. Plan and keyword map: vivify/SEO-PLAN.md.

Copy rules:
- Only facts already on vivifysports.com: credentials, titles, prices, services, partners, testimonials, Marine's own articles.
- No invented clients, results, numbers, prices or opening hours.
- DRAFT copy: Marine to read and approve before it goes on WordPress.
"""
import json


def build(b):
    e, img, head, ticks, chips, cta, ICON = b.e, b.img, b.head, b.ticks, b.chips, b.cta, b.ICON
    LIVE, DISC, OUT = b.LIVE, b.DISCOVERY, b.OUT

    def faq_block(qas, eyebrow='Questions', title='FAQ'):
        items = ''.join(f'<details class="qa panel"><summary>{e(q)}</summary><div>{a}</div></details>' for q, a in qas)
        schema = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": _strip(a)}} for q, a in qas]}
        return f'<section style="padding-top:24px"><div class="wrap" style="max-width:860px">{head(eyebrow, title, center=True)}<div style="margin-top:28px">{items}</div></div></section>', schema

    def people(names):
        return [t for t in b.T if t[2] in names]

    def quotes(names, title='What athletes say'):
        cards = ''.join(f"""<article class="tcard panel"><span class="q">{ICON['quote']}</span>
 <div class="who">{img(p, a, w=64, h=64)}<div><p class="name">{e(n)} <span class="sport">{e(s)}</span></p></div></div>
 <blockquote>{e(q)}</blockquote></article>""" for p, a, n, s, q in people(names))
        return f'<section style="padding-top:24px"><div class="wrap">{head("Client stories", title, tag=None, center=True)}<div class="tgrid" style="{'columns:1;max-width:460px;margin:32px auto 0' if len(people(names)) == 1 else 'margin-top:32px'}">{cards}</div></div></section>'

    def posts(slugs, title='Read Marine’s articles'):
        allp = {(p['url'] or '').rsplit('/', 1)[-1]: p for p in b.blog_posts()}
        cards = ''
        for s in slugs:
            p = allp.get(s)
            if not p:
                continue
            ph = img(p['img'], p['title'], w=640, h=400) if p['img'] else img(b.LOGO, b.LOGO_ALT, w=90, h=85, style='margin:auto;padding-top:40px')
            cards += f'<a class="bcard panel" href="{p["url"]}"><div class="ph">{ph}</div><div class="tx"><h3 class="h3" style="font-size:19px;margin-bottom:10px">{e(p["title"])}</h3><div class="meta"><span>{e(p["read"])}</span></div></div></a>'
        return f'<section style="padding-top:24px"><div class="wrap">{head("From the blog", title, tag=None, center=True)}<div class="bgrid" style="margin-top:28px">{cards}</div></div></section>'

    def hero(eyebrow, h1, lead, photo=None, alt='', btn=('Book your free discovery call', DISC)):
        if photo:
            return f"""<section class="hero" style="min-height:min(74vh,660px)">{img(photo, alt, lazy=False, w=1600, h=1067)}
 <div class="wrap"><span class="pill">{eyebrow}</span><h1>{h1}</h1><p class="lead">{lead}</p>
 <a class="btn btn-primary" href="{btn[1]}">{btn[0]} {ICON['arrow']}</a></div></section>"""
        return f"""<section class="page-hero"><div class="wrap"><span class="eyebrow">{eyebrow}</span><h1>{h1}</h1><span class="bar" style="margin:16px auto 18px"></span>
 <p class="lead">{lead}</p><a class="btn btn-primary" href="{btn[1]}">{btn[0]} {ICON['arrow']}</a></div></section>"""

    def creds(title='Why athletes choose Marine'):
        items = [('MSc in Sports Nutrition', 'Universidad Europea de Madrid (2025), plus a Professional Diploma in Sports Nutrition from Barça Innovation Hub (2023).'),
                 ('WorldTour professional cyclist', 'Signed with LIDL-TREK in 2025. Irish National Gravel Champion (2026) and Amateur Gravel World Champion (2024).'),
                 ('Built on your training', 'Your plan follows your training load week by week, with TrainingPeaks, Vekta and MyFitnessPal.'),
                 ('The whole athlete', 'Also a qualified massage therapist and 200-hour Yoga Alliance teacher, for recovery as well as fuel.')]
        cards = ''.join(f'<div class="pcard panel"><span style="color:var(--lime-text)">{ICON["star"]}</span><span class="h3">{e(t)}</span><p style="margin:0">{e(d)}</p></div>' for t, d in items)
        return f'<section style="padding-top:24px"><div class="wrap">{head("Marine Lenehan, MSc", title, tag=None, center=True)}<div class="g4" style="margin-top:28px">{cards}</div></div></section>'

    def plans_strip():
        rows = [('Nutritional Assessment', '50 min', '100€ / 120 US$'), ('Follow-up Consultation', '30 min', '50€ / 60 US$'),
                ('The Healthy Body Plan', '3 months', '99€ / 119 US$ a month'), ('The Happy Body Plan', '3 months', '149€ / 180 US$ a month'),
                ('The Performing Body Plan', '3 months', '199€ / 240 US$ a month (sold out for now)'), ('Race Fuelling Plan', '30 min call + PDF plan', '70€')]
        tr = ''.join(f'<tr><th scope="row">{n}</th><td>{d}</td><td>{p}</td></tr>' for n, d, p in rows)
        return f"""<div class="tbl-wrap"><table class="cmp" style="min-width:520px"><thead><tr><th scope="col">Option</th><th scope="col">Length</th><th scope="col">Price</th></tr></thead><tbody>{tr}</tbody></table></div>
 <p class="center" style="margin-top:18px"><a href="sports-nutritionist-ireland.html#plans">Compare everything each plan includes {ICON['arrow']}</a></p>"""

    def page(file, body, schema_items):
        graph = [{"@type": "WebPage", "@id": LIVE + b.NEW[file][0], "name": b.NEW[file][1], "description": b.NEW[file][2],
                  "about": {"@id": LIVE + "/#marine"}}] + schema_items + [PERSON]
        open(OUT + file, 'w').write(b.shell(file, body, {"@context": "https://schema.org", "@graph": graph}))

    PERSON = {"@type": "Person", "@id": LIVE + "/#marine", "name": "Marine Lenehan", "jobTitle": "Sports Nutritionist",
              "worksFor": {"@type": "Organization", "name": "Vivify Sports", "url": LIVE}, "url": LIVE + "/about",
              "alumniOf": "Universidad Europea de Madrid", "knowsAbout": ["Sports nutrition", "Cycling nutrition", "Endurance fuelling", "Triathlon nutrition"],
              "sameAs": [b.IG]}
    SERVICE = lambda name, typ, area: {"@type": "Service", "name": name, "serviceType": typ, "areaServed": area,
                                       "provider": {"@id": LIVE + "/#marine"}, "url": LIVE + "/sports-nutritionist-ireland"}

    # ------------------------------------------------------------ CYCLING NUTRITIONIST
    qas = [('How many carbs per hour should I eat on the bike?',
            '<p>It depends on how long and how hard you ride. For long rides and endurance events, 60–90 g of carbohydrate per hour is a common target, and some athletes reach 100–120 g/hour after training their gut to tolerate it. Marine explains the details in <a href="post-carbohydrate-fueling-endurance-sports.html">How Many Carbs Per Hour Do You Need?</a></p>'),
           ('Can you help me lose weight without losing power?',
            '<p>Yes. Marine’s approach is “fuel for performance, not restriction”: enough energy and carbohydrate to support training, adequate protein, hydration and recovery, without extreme diets. One client lost over 13 kg while getting stronger for the Traka gravel race.</p>'),
           ('Do you work with gravel and ultra-distance riders?',
            '<p>Yes. Marine is the Amateur Gravel World Champion (2024) and Irish National Gravel Champion (2026), and has coached riders for ultra-endurance gravel races.</p>'),
           ('Can you help me prepare for a Gran Fondo or sportive?',
            '<p>Yes. Marine is the European Gran Fondo Champion (2023). She builds your daily nutrition around your training and a race-day plan for your event, whether that is the Wicklow 200, L’Étape du Tour, the Marmotte or a UCI Gran Fondo World Series race.</p>'),
           ('Do you work with elite and professional riders?',
            '<p>Yes. Marine races in the WorldTour with LIDL-TREK and works with riders up to elite level: race calendars and stage races, high-carbohydrate race fuelling, safe body composition, training camps and batch-tested supplements.</p>'),
           ('Do I need to be in Ireland?',
            '<p>No. Coaching is online. Marine currently coaches athletes in the USA, Canada, Ireland and Finland, and has coached athletes in France, Italy and the Netherlands. Plans are priced in euro and US dollars.</p>')]
    faq_html, faq_schema = faq_block(qas, 'Cycling nutrition', 'Common questions')
    body = f"""
{hero('Sports Nutritionist · Ireland & Online', 'Cycling Nutritionist',
      'Nutrition coaching for cyclists of every discipline (road, gravel, track, mountain bike and cyclocross) from Marine Lenehan: MSc sports nutritionist and LIDL-TREK WorldTour professional cyclist.',
      '0e1488-26eed664485245b6b26c855875ee', 'Road cyclist riding through a forest')}
<section><div class="wrap g2" style="align-items:start">
 <div>{head('Fuel like a pro', 'A cycling nutritionist who races at the top')}
  <p>Most nutritionists learn cycling from the outside. Marine fuels her own WorldTour racing with LIDL-TREK using the same evidence-based strategies she builds for her clients. She knows what a five-hour training day, a crit or a gravel race asks of the body. She also knows what you can actually eat from a jersey pocket.</p>
  <p>Whether you are training for the Wicklow 200, your first gravel race or a season of racing, your plan follows your training load week by week. Marine works with TrainingPeaks, Vekta and MyFitnessPal, so you know what to eat on and off the bike.</p></div>
 <div class="panel" style="padding:32px"><span class="eyebrow">What we work on</span>
  {chips(['Carbs per hour on the bike', 'Gut training', 'Hydration &amp; sweat rate', 'Race-day fuelling', 'Recovery nutrition', 'Weight management', 'Avoiding the bonk', 'Supplements', 'Iron &amp; energy levels', 'Winter training fuel'])}</div>
</div></section>
<section style="padding-top:8px"><div class="wrap">
 {head('Every discipline', 'Road, gravel, track, MTB, cyclocross', tag='h2', center=True)}
 <div class="g3" style="margin-top:28px">
  <div class="pcard panel"><span class="h3">Road racing</span><p style="margin:0">Fuel for repeated hard efforts, race-day carbohydrate targets and recovery between stage or weekend races.</p></div>
  <div class="pcard panel"><span class="h3">Gravel &amp; ultra</span><p style="margin:0">Long days with little support: what to carry, how much to eat each hour and how to train your gut to take it.</p></div>
  <div class="pcard panel"><span class="h3">Track</span><p style="margin:0">Short, explosive efforts and long competition days: fuelling between rounds, fast recovery and power-to-weight.</p></div>
  <div class="pcard panel"><span class="h3">Mountain bike</span><p style="margin:0">Hard, technical efforts where it is hard to eat: what to use in the feed zone and carbs you can actually get down on the trail.</p></div>
  <div class="pcard panel"><span class="h3">Cyclocross</span><p style="margin:0">Short, all-out winter races: timing your pre-race meal, warm-up fuel and recovering between back-to-back race weekends.</p></div>
  <div class="pcard panel"><span class="h3">Sportives &amp; leisure</span><p style="margin:0">More energy on long rides, no more cramping or bonking, and healthy habits that fit around work and family.</p></div>
 </div></div></section>
<section style="padding-top:8px"><div class="wrap g2" style="align-items:start">
 <div>{head('Elite &amp; pro riders', 'Elite and professional riders')}
  <p>Marine races in the WorldTour with LIDL-TREK, so she knows the demands of elite cycling from the inside: a full race calendar, stage races, travel and the fine margins that decide results. Elite and development riders get the same evidence-based approach she uses for her own racing.</p>
  <p>Food first, always. Where supplements help, Marine recommends batch-tested products only, which matters for any rider subject to anti-doping rules.</p></div>
 <div class="g2" style="gap:14px">
  <div class="pcard panel"><span class="h3">Race calendar &amp; stage races</span><p style="margin:0">Fuelling and recovery between stages, back-to-back race days and a full season.</p></div>
  <div class="pcard panel"><span class="h3">Race-day fuelling at the top level</span><p style="margin:0">High carbohydrate intakes (90–120 g/h) with gut training, so you can absorb what the race demands.</p></div>
  <div class="pcard panel"><span class="h3">Body composition, safely</span><p style="margin:0">Power-to-weight without under-fuelling: protecting health, hormones, bones and performance.</p></div>
  <div class="pcard panel"><span class="h3">Travel, camps &amp; altitude</span><p style="margin:0">Eating well at training camps, at altitude and on the road between races.</p></div>
 </div>
</div></section>
<section class="section-tight" style="padding-top:0"><div class="wrap center"><a class="btn btn-secondary" href="womens-cycling-nutrition.html">Women's cycling nutrition {ICON['arrow']}</a></div></section>
<section style="padding-top:8px"><div class="wrap">
 {head('Gran Fondos, sportives, gravel and more', 'Fuel for your target event', center=True, lead='Whatever you are training for, your nutrition is built around the event: its distance, terrain, climbing, weather and feed stations. From the Wicklow 200 to the Marmotte, the Traka or the Cape Epic.')}
 <div class="g3" style="margin-top:28px"><div class="pcard panel"><span class="h3">Gran Fondos &amp; sportives</span><ul class="chips" style="margin-top:12px"><li>UCI Gran Fondo World Championships</li><li>Gran Fondo</li><li>Gran Fondo Strade Bianche</li><li>Gran Fondo Il Lombardia</li><li>Nove Colli</li><li>Gran Fondo Fausto Coppi</li><li>Gran Fondo Stelvio Santini</li><li>Wicklow 200</li><li>Ring of Kerry Charity Cycle</li><li>L’Étape du Tour</li><li>La Marmotte</li><li>Maratona dles Dolomites</li><li>Mallorca 312</li></ul></div><div class="pcard panel"><span class="h3">Gravel</span><ul class="chips" style="margin-top:12px"><li>UCI Gravel World Championships</li><li>The Traka</li><li>Unbound Gravel</li><li>Tuscany Trail</li><li>L’Eroica</li><li>Gravel Earth Series</li></ul></div><div class="pcard panel"><span class="h3">Mountain bike</span><ul class="chips" style="margin-top:12px"><li>XC and marathon (XCM) races</li><li>Absa Cape Epic</li><li>Enduro</li></ul></div><div class="pcard panel"><span class="h3">Cyclocross &amp; track</span><ul class="chips" style="margin-top:12px"><li>National cyclocross series</li><li>National championships</li><li>Track omnium and endurance events</li></ul></div><div class="pcard panel"><span class="h3">Multi-day &amp; ultra</span><ul class="chips" style="margin-top:12px"><li>Haute Route</li><li>Stage races</li><li>Ultra-distance and bikepacking events</li></ul></div></div>
 <p class="center" style="margin-top:22px"><a class="btn btn-primary" href="race-fuelling-plan.html">Get a fuelling plan for your event {ICON['arrow']}</a></p>
</div></section>
{creds()}
<section style="padding-top:24px"><div class="wrap">{head('Coaching options', 'Plans and prices', center=True)}<div style="margin-top:24px">{plans_strip()}</div></div></section>
{quotes(['Francesco Pippa, Italy', 'Sean Goggin, Ireland', 'Matteo Cigala,Italy', 'James Makin, Ireland', 'Iwan Harmsen, Netherlands', 'Damian Maloney, Ireland'], 'Cyclists who fuel with Marine')}
{posts(['cycling-nutrition-what-to-eat-and-drink-during-bike-rides-of-any-length', 'why-do-you-always-bonk-out-on-the-bike', 'top-5-foods-for-cyclists-why', 'effective-fuelling-techniques-for-winter-training-for-cyclists', 'all-about-carbohydrates-sugar-for-cyclists', '3-benefits-of-yoga-for-cyclists'], 'Cycling nutrition articles')}
{faq_html}
{cta('Ride stronger, fuel smarter', 'Start with a free 30-minute discovery call about your riding, your goals and your next event.', 'Book your free call', DISC)}"""
    page('cycling-nutritionist.html', body, [SERVICE('Cycling nutrition coaching', 'Sports nutrition coaching for cyclists', ['Ireland', 'Worldwide']), faq_schema])

    # ------------------------------------------------------------ RACE FUELLING PLAN
    qas = [('When should I get my fuelling plan?',
            '<p>Ideally several weeks before your event, so you can practise it in training and train your gut to tolerate the carbohydrate you will need on the day.</p>'),
           ('Is a fuelling plan included in the coaching plans?',
            '<p>A competition nutrition plan is part of The Performing Body Plan (sold out for now). You can also buy a fuelling plan on its own for a single event, for 70€.</p>'),
           ('How much does a fuelling plan cost?',
            '<p>70€. It includes a 30-minute call with Marine to understand your event, followed by your personal fuelling plan as a PDF. You choose your call time and pay online in one step.</p>'),
           ('Which events do you plan for?',
            '<p>Endurance events of any length: road races, sportives, gravel and ultra-distance rides, triathlon from sprint to Ironman, and running races.</p>')]
    faq_html, faq_schema = faq_block(qas, 'Fuelling plans', 'Common questions')
    body = f"""
{hero('Cycling · Triathlon · Running', 'Race Fuelling Plan',
      'Remember bonking out half way through your event? A precise plan for race day, based on your sport, gender, weight and metabolism.',
      'nsplsh-5aa897658f1e4fb8bd88bbd8b165', 'Ironman 70.3 Nutrition Plan: How to Fuel Your Training and Race Day', btn=('Buy your fuelling plan · 70€', b.FUELLING_PAY))}
<section><div class="wrap g2" style="align-items:start">
 <div>{head('Race day, planned', 'What your fuelling plan covers')}
  <p>Fuelling for an event can be quite a headache. Marine builds a plan around your event, your body and what your gut can handle. It tells you what to eat and drink, how much and when, from the days before the start to the finish line.</p>
  <p>It uses the same approach Marine uses for her own racing in the WorldTour, and for clients like Colum. He took 30 minutes off his Ironman 70.3 time with the right nutrition plan.</p>
  <div class="panel" style="padding:24px 26px;margin-top:22px;display:flex;flex-wrap:wrap;gap:18px;align-items:center;justify-content:space-between">
   <div><span class="h2" style="font-size:44px">70€</span><p class="muted" style="margin:4px 0 0;text-align:left">30-minute call + your fuelling plan in PDF</p><p class="muted" style="margin:2px 0 0;font-size:12.5px;text-align:left">Choose your call time and pay in one step.</p></div>
   <a class="btn btn-primary" href="{b.FUELLING_PAY}" target="_blank" rel="noopener">Buy your fuelling plan {ICON['arrow']}</a></div></div>
 <div class="panel" style="padding:32px"><span class="eyebrow">Tailored to your goals and your event</span>
  {ticks(['Nutrition for the day before and race day', 'Macros or practical recipes, whichever you prefer', 'Carbohydrate intake per hour', 'Supplements', 'Hydration strategy', 'Recovery strategy'])}</div>
</div></section>
<section style="padding-top:8px"><div class="wrap">
 {head('How it works', 'Three steps', center=True)}
 <div class="g3" style="margin-top:28px">
  <div class="pcard panel"><span class="num">1.</span><span class="h3">Buy your plan</span><p style="margin:0">Choose your 30-minute call time with Marine and pay online (70€) in one step.</p></div>
  <div class="pcard panel"><span class="num">2.</span><span class="h3">30-minute call</span><p style="margin:0">Tell Marine about your event: distance, course, expected time, weather, what you eat now and what has gone wrong before.</p></div>
  <div class="pcard panel"><span class="num">3.</span><span class="h3">Your plan in PDF</span><p style="margin:0">A clear plan for your sport, gender, weight and metabolism: grams of carbs per hour, fluids and what to carry. Practise it on long sessions before race day.</p></div>
 </div></div></section>
{quotes(['Colum Traynor, Ireland', 'Matteo Cigala,Italy', 'Francesco Pippa, Italy'], 'Fuelled for race day')}
{posts(['carbohydrate-fueling-endurance-sports', 'ironman-70-3-nutrition-plan', 'water-vs-sports-drinks-what-is-the-best-choice', 'do-lactate-gels-work', 'why-do-you-always-bonk-out-on-the-bike', 'cycling-nutrition-what-to-eat-and-drink-during-bike-rides-of-any-length'], 'Fuelling articles')}
{faq_html}
{cta('Got an event coming up?', '70€: a 30-minute call about your event, then your personal fuelling plan in PDF.', 'Buy your fuelling plan', b.FUELLING_PAY, ext=True)}"""
    page('race-fuelling-plan.html', body, [dict(SERVICE('Race fuelling plan', 'Event nutrition and fuelling plan', 'Worldwide'), offers={'@type': 'Offer', 'price': '70', 'priceCurrency': 'EUR', 'url': b.FUELLING_PAY}), faq_schema])

    # ------------------------------------------------------------ TRIATHLON
    qas = [('Can you help me plan nutrition for an Ironman 70.3?',
            '<p>Yes. Marine builds the plan around your training and your race: daily fuelling for three sports, carbohydrate per hour on the bike and run, hydration, and gut training before race day. See her <a href="' + LIVE + '/post/ironman-70-3-nutrition-plan">Ironman 70.3 nutrition plan</a> article.</p>'),
           ('Can you help me fuel for a full Ironman?',
            '<p>Yes. Long-distance triathlon is where fuelling matters most. Marine plans your carbohydrate, fluid and sodium intake for the bike and the run, trains your gut to handle it in the months before, and builds your race-week and race-morning nutrition, whether you are racing Ironman Wales, Challenge Roth or Kona.</p>'),
           ('I get stomach problems on the run. Can nutrition help?',
            '<p>Often, yes. Gut health and gut training are part of the coaching: the aim is fewer gastrointestinal problems such as cramping, nausea and bloating, and better carbohydrate absorption.</p>'),
           ('Do you coach the training too?',
            '<p>Marine coaches nutrition. She works alongside your coach and your training plan, using TrainingPeaks so your fuelling follows your training load.</p>')]
    faq_html, faq_schema = faq_block(qas, 'Triathlon nutrition', 'Common questions')
    body = f"""
{hero('Swim · Bike · Run', 'Triathlon Nutritionist',
      'Nutrition coaching for triathletes, from your first sprint to Ironman: fuel three sports, recover between sessions and arrive at race day with a plan.',
      '0e1488-9726c9f5f34c4bc0a075d5cb639e', 'Triathlete swimming in open water')}
<section><div class="wrap g2" style="align-items:start">
 <div>{head('Three sports, one plan', 'Fuel your training and your race')}
  <p>Triathlon training is long and varied, often with two sessions in a day. Fuelling it well makes the difference between adapting to training and just getting tired. Marine builds your nutrition week by week from your training load, so hard days are fuelled and recovery is supported.</p>
  <p>On race day the bike leg sets up your run. Your plan covers how much carbohydrate and fluid you take on the bike, what you carry on the run and how to train your gut to tolerate it.</p></div>
 <div class="panel" style="padding:32px"><span class="eyebrow">What we work on</span>
  {chips(['Daily fuelling for double days', 'Bike-to-run fuelling', 'Carbs per hour', 'Hydration &amp; sweat rate', 'Gut training', 'Recovery between sessions', 'Body composition', 'Supplements'])}</div>
</div></section>
<section style="padding-top:8px"><div class="wrap"><div class="cta">
 <div><span class="eyebrow">Client result</span><div class="h2">A 30 minute PB at Ironman 70.3</div><span class="bar"></span>
  <p class="lead" style="margin:0">“The nutrition advice I received for my 70.3 Ironman training &amp; race day resulted in a 30 min PB &amp; I never felt so good on the run leg.” Colum Traynor, Ireland</p></div>
 <div><a class="btn btn-primary" href="race-fuelling-plan.html">Get a race fuelling plan {ICON['arrow']}</a></div></div></div></section>
<section style="padding-top:8px"><div class="wrap">
 {head('Ironman, 70.3, Olympic and sprint', 'Fuel for your target race', center=True, lead='Your plan is built around your race: distance, course, climate and the aid stations on the bike and run. From the Dublin City Triathlon to Ironman Wales, Challenge Roth or the Ironman World Championship.')}
 <div class="g4" style="margin-top:28px"><div class="pcard panel"><span class="h3">Full distance (Ironman)</span><ul class="chips" style="margin-top:12px"><li>Ironman World Championship</li><li>Challenge Roth</li><li>Ironman Wales</li><li>Ironman Lanzarote</li><li>Ironman Frankfurt</li><li>Ironman Lake Placid</li><li>Ironman Mont-Tremblant</li></ul></div><div class="pcard panel"><span class="h3">Middle distance (70.3)</span><ul class="chips" style="margin-top:12px"><li>Ironman 70.3 World Championship</li><li>Ironman 70.3 races</li><li>Challenge middle-distance races</li></ul></div><div class="pcard panel"><span class="h3">Olympic &amp; sprint</span><ul class="chips" style="margin-top:12px"><li>Dublin City Triathlon</li><li>Hell of the West</li><li>Escape from Alcatraz Triathlon</li><li>National championships</li></ul></div><div class="pcard panel"><span class="h3">Off-road &amp; multisport</span><ul class="chips" style="margin-top:12px"><li>XTERRA</li><li>Duathlon</li><li>Aquathlon</li></ul></div></div>
 <p class="center" style="margin-top:22px"><a class="btn btn-primary" href="race-fuelling-plan.html">Get a fuelling plan for your race {ICON['arrow']}</a></p>
</div></section>
{creds('A nutritionist who competes')}
<section style="padding-top:24px"><div class="wrap">{head('Coaching options', 'Plans and prices', center=True)}<div style="margin-top:24px">{plans_strip()}</div></div></section>
{posts(['ironman-70-3-nutrition-plan', 'carbohydrate-fueling-endurance-sports', 'fatigue-endurance-athletes', 'endurance-athlete-nutrition', 'water-vs-sports-drinks-what-is-the-best-choice', 'what-should-i-be-eating-for-breakfast-as-an-athlete'], 'Triathlon nutrition articles')}
{faq_html}
{cta('Ready for your next race?', 'A free 30-minute discovery call to talk through your training, your races and your nutrition.', 'Book your free call', DISC)}"""
    page('triathlon-nutritionist.html', body, [SERVICE('Triathlon nutrition coaching', 'Sports nutrition coaching for triathletes', ['Ireland', 'Worldwide']), faq_schema])

    # ------------------------------------------------------------ ONLINE / INTERNATIONAL
    qas = [('How do online consultations work?',
            '<p>Consultations are private online video calls. Between calls, Marine follows your training on TrainingPeaks or Vekta and your food diary on MyFitnessPal, and updates your plan as your training changes.</p>'),
           ('Can I pay in US dollars?',
            '<p>Yes. Every option is priced in euro and US dollars. For example, the Nutritional Assessment is 100€ / 120 US$.</p>'),
           ('Which athletes do you work with?',
            '<p>Endurance athletes, mainly cyclists, triathletes and runners, from first events to elite level. Marine currently coaches athletes in the USA, Canada, Ireland and Finland, and has coached athletes in France, Italy and the Netherlands.</p>'),
           ('Can I try it before committing?',
            '<p>Yes. The first step is a free 30-minute discovery call.</p>')]
    faq_html, faq_schema = faq_block(qas, 'Working online', 'Common questions')
    flags = [('USA', 'Coaching now'), ('Canada', 'Coaching now'), ('Ireland', 'Coaching now'), ('Finland', 'Coaching now')]
    body = f"""
{hero('Worldwide · Online', 'Online Sports Nutritionist',
      'Personal nutrition coaching from an MSc sports nutritionist and WorldTour cyclist, wherever you live and train. Currently coaching athletes in the USA, Canada, Ireland and Finland.')}
<section><div class="wrap g2" style="align-items:start">
 <div>{head('From Wicklow to the world', 'Coaching that travels with you')}
  <p>Vivify Sports is based in Wicklow, Ireland, and works with athletes worldwide. Everything happens online: consultations by video call, your plan updated weekly from your training load, and support between calls.</p>
  <p>Marine races the WorldTour herself, so she understands travel and racing abroad, and fits your nutrition around them.</p></div>
 <div class="panel" style="padding:32px"><span class="eyebrow">How it works</span>
  {ticks(['Free 30-minute discovery call', 'Nutritional assessment by video call', 'Weekly plan from your TrainingPeaks or Vekta training load', 'Food diary review in MyFitnessPal', 'WhatsApp support on every 3-month plan', 'Prices in euro and US dollars'])}</div>
</div></section>
<section style="padding-top:8px"><div class="wrap">
 {head('Where Marine coaches', 'Athletes on both sides of the Atlantic', tag='h2', center=True, lead='Currently coaching athletes in the USA, Canada, Ireland and Finland. Past clients in France, Italy and the Netherlands.')}
 <div class="g4" style="margin-top:28px">{''.join(f'<div class="pcard panel center"><span class="h3">{c}</span><p class="muted" style="margin:0">{n}</p></div>' for c, n in flags)}</div>
</div></section>
<section style="padding-top:24px"><div class="wrap">{head('Coaching options', 'Plans in euro and US dollars', center=True)}<div style="margin-top:24px">{plans_strip()}</div></div></section>
{creds()}
{quotes(['Francesco Pippa, Italy', 'Eleonore Vaillon, France', 'Iwan Harmsen, Netherlands', 'Matteo Cigala,Italy'], 'Athletes from across Europe')}
{faq_html}
{cta('Wherever you train', 'Book a free 30-minute discovery call online.', 'Book your free call', DISC)}"""
    page('online-sports-nutritionist.html', body, [SERVICE('Online sports nutrition coaching', 'Sports nutrition coaching', 'Worldwide'), faq_schema])

    # ------------------------------------------------------------ DUBLIN & WICKLOW
    qas = [('Do you see clients in person in Dublin?',
            '<p>Nutrition consultations are online by video call, so there is no travel and you can book from anywhere in Dublin. Workshops for clubs are in person in Co. Wicklow and Co. Dublin. Sports massage on call is currently sold out.</p>'),
           ('Do you give talks to Dublin and Wicklow clubs?',
            '<p>Yes. Marine gives nutrition workshops and talks for cycling, triathlon, running, swimming and athletic clubs, gyms and team sports. See <a href="workshops.html">Workshops &amp; Talks</a>.</p>')]
    faq_html, faq_schema = faq_block(qas, 'Local', 'Common questions')
    body = f"""
{hero('Wicklow · Dublin · Ireland', 'Sports Nutritionist in Dublin &amp; Wicklow',
      'Nutrition coaching for athletes across Dublin and Wicklow from Marine Lenehan, an MSc sports nutritionist based in Wicklow Town.',
      '0e1488-70faaa082bbd4ad4b8d8f16a5bc3', 'Cyclist riding a lakeside road above a lake')}
<section><div class="wrap">
 {head('Local and online', 'Three ways to work with Marine', center=True)}
 <div class="g3" style="margin-top:28px">
  <a class="scard panel" href="sports-nutritionist-ireland.html"><div class="tx"><span class="eyebrow">Online</span><span class="h3">Nutrition coaching</span><p class="muted">Consultations by video call, with your plan updated weekly from your training.</p><span class="go">See plans {ICON['arrow']}</span></div></a>
  <a class="scard panel" href="workshops.html"><div class="tx"><span class="eyebrow">In person</span><span class="h3">Club workshops &amp; talks</span><p class="muted">For cycling, running, swimming and athletic clubs, gyms and teams.</p><span class="go">Workshops {ICON['arrow']}</span></div></a>
  <a class="scard panel" href="massage-therapy.html"><div class="tx"><span class="eyebrow">Currently sold out</span><span class="h3">Sports massage</span><p class="muted">Deep tissue, cupping and Thai massage, on call in Co. Wicklow and Co. Dublin. Sold out for now.</p><span class="go">Massage {ICON['arrow']}</span></div></a>
 </div></div></section>
<section style="padding-top:8px"><div class="wrap g2" style="align-items:start">
 <div>{head('Rooted in Irish cycling', 'Irish champion, local partner')}
  <p>Marine is the Irish National Gravel Champion (2026), Irish National Criterium Champion (2024) and has podiums at the Elite Irish Road and TT Nationals. Vivify Sports partners with the Wicklow 200 and works with riders and triathletes across Ireland.</p></div>
 <div class="panel" style="padding:32px">{ticks(['Wicklow Town service area', 'Sports massage on call: currently sold out', 'Online coaching across Ireland', 'Free 30-minute discovery call'])}</div>
</div></section>
{quotes(['Sean Goggin, Ireland', 'Colum Traynor, Ireland', 'James Makin, Ireland', 'Damian Maloney, Ireland'], 'Athletes from Ireland')}
{faq_html}
{cta('Based in Wicklow', 'Book a free 30-minute discovery call, or ask about a talk for your club.', 'Book your free call', DISC)}"""
    local = {"@type": "ProfessionalService", "name": "Vivify Sports", "url": LIVE, "email": b.EMAIL, "telephone": b.PHONE,
             "address": {"@type": "PostalAddress", "addressLocality": "Wicklow", "addressRegion": "Co. Wicklow", "addressCountry": "IE"},
             "areaServed": ["County Wicklow", "County Dublin", "Ireland"], "founder": {"@id": LIVE + "/#marine"}, "sameAs": [b.IG, b.GBP]}
    page('sports-nutritionist-dublin.html', body, [local, faq_schema])

    # ------------------------------------------------------------ WOMEN'S CYCLING NUTRITION
    qas = [('Should I change my nutrition across my menstrual cycle?',
            '<p>Some women notice changes in energy, appetite, hydration or gut comfort at different points of their cycle, and some don’t. The research is still developing, so there is no single plan that suits every woman. Marine looks at your own training, symptoms and food diary and adjusts from there.</p>'),
           ('Why do female athletes need to think about iron?',
            '<p>Endurance training and menstrual blood loss both raise iron needs, so women who ride a lot are more likely to run low. Low iron can show up as fatigue and a drop in performance. Marine covers this in <a href="' + LIVE + '/post/iron-deficiency-anemia-and-performance">Iron Deficiency, Anemia and Performance</a>. If you think your iron is low, get your levels checked by your GP.</p>'),
           ('I want to lose weight but keep my power. Is that possible?',
            '<p>Yes, with care. Eating too little for the training you do (low energy availability) can affect your hormones, bones, recovery and performance. Marine’s approach is fuel for performance, not restriction: enough energy on hard days, and sustainable habits rather than crash diets.</p>'),
           ('Do you only work with racers?',
            '<p>No. Marine works with women at every level, from leisure riders and sportive cyclists to racers, in Ireland and online worldwide.</p>')]
    faq_html, faq_schema = faq_block(qas, "Women's cycling nutrition", 'Common questions')
    body = f"""
{hero('By a female WorldTour cyclist', "Women's Cycling Nutrition",
      'Nutrition coaching for women who ride, from Marine Lenehan: MSc sports nutritionist and LIDL-TREK WorldTour professional cyclist.',
      '0e1488-70faaa082bbd4ad4b8d8f16a5bc3', 'Female cyclist riding a lakeside road above a lake')}
<section><div class="wrap g2" style="align-items:start">
 <div>{head('Made for female athletes', 'Fuel the way your body works')}
  <p>Most sports nutrition advice was built from research on men. Women who ride have their own needs: hormones that change through the month and through life, higher iron needs, and a greater risk of under-fuelling when training is high and food is tight.</p>
  <p>Marine races in the women's WorldTour with LIDL-TREK, so she knows these questions from the inside. Your plan is built around your training load, your cycle and your goals, whether that is a first sportive, a gravel race or a season of racing.</p></div>
 <div class="panel" style="padding:32px"><span class="eyebrow">What we work on</span>
  {chips(['Energy availability', 'Iron &amp; fatigue', 'Your menstrual cycle', 'Carbs per hour on the bike', 'Hydration', 'Recovery &amp; protein', 'Bone health', 'Weight without restriction', 'Gut comfort', 'Supplements'])}</div>
</div></section>
<section style="padding-top:8px"><div class="wrap">
 {head('The key areas', 'Four things female cyclists should know', center=True)}
 <div class="g4" style="margin-top:28px">
  <div class="pcard panel"><span class="num">1.</span><span class="h3">Eat enough</span><p style="margin:0">Under-fuelling for your training (low energy availability) can affect hormones, bones, mood and performance. Fuel the work first.</p></div>
  <div class="pcard panel"><span class="num">2.</span><span class="h3">Watch your iron</span><p style="margin:0">Training and menstrual losses raise iron needs. Low iron often shows up as fatigue that rest does not fix.</p></div>
  <div class="pcard panel"><span class="num">3.</span><span class="h3">Know your cycle</span><p style="margin:0">Energy, appetite and gut comfort can change through the month. Your plan follows how you feel, not a generic chart.</p></div>
  <div class="pcard panel"><span class="num">4.</span><span class="h3">Fuel on the bike</span><p style="margin:0">Carbohydrate during long rides protects your training and recovery, and that applies to women just as much as men.</p></div>
 </div></div></section>
{creds('A nutritionist who races')}
<section style="padding-top:24px"><div class="wrap">{head('Coaching options', 'Plans and prices', center=True)}<div style="margin-top:24px">{plans_strip()}</div></div></section>
{quotes(['Eleonore Vaillon, France'], 'In her words')}
{posts(['iron-deficiency-anemia-and-performance', 'fatigue-endurance-athletes', 'why-am-i-so-tired-after-exercise-understanding-post-exercise-fatigue-in-endurance-athletes', 'carbohydrate-fueling-endurance-sports', 'daily-fat-intake-guide', 'weight-loss-metabolism-guide'], 'Articles for female athletes')}
{faq_html}
{cta('Ride strong, fuel well', 'Start with a free 30-minute discovery call with Marine about your riding and your goals.', 'Book your free call', DISC)}"""
    page('womens-cycling-nutrition.html', body, [SERVICE("Women's cycling nutrition coaching", 'Sports nutrition coaching for female cyclists', ['Ireland', 'Worldwide']), faq_schema])

    # ------------------------------------------------------------ FAQ
    qas = [('What does a sports nutritionist do?',
            '<p>A sports nutritionist helps you eat for your training and your goals: enough energy and carbohydrate for the work you do, protein for recovery, hydration, and fuelling during sessions and races. Marine also looks at vitamins, minerals and supplements, gut health and your relationship with food.</p>'),
           ('Who is Marine Lenehan?',
            '<p>Marine is the founder of Vivify Sports. She holds an MSc in Sports Nutrition from Universidad Europea de Madrid and has raced as a WorldTour professional with LIDL-TREK since 2025. Read more <a href="about.html">about Marine</a>.</p>'),
           ('Do I need to live in Ireland?',
            '<p>No. Coaching is online and Marine works with athletes worldwide. Prices are shown in euro and US dollars. See <a href="online-sports-nutritionist.html">online coaching</a>.</p>'),
           ('Which plan should I choose?',
            '<p>Start with the Nutritional Assessment for a one-off review and report. For ongoing support, The Healthy Body Plan builds habits with a weekly macro plan, The Happy Body Plan adds a weekly meal plan and more calls, and The Performing Body Plan (sold out for now) adds unlimited calls, daily WhatsApp support and sport-specific work such as a competition plan and sweat rate test. <a href="sports-nutritionist-ireland.html#plans">Compare the plans</a>.</p>'),
           ('How much do the plans cost?',
            '<p>The Nutritional Assessment is 100€ (120 US$) and a Follow-up Consultation is 50€ (60 US$). The 3-month plans are 99€, 149€ or 199€ a month (119, 180 or 240 US$).</p>'),
           ('Is the discovery call free?', '<p>Yes. It is a free 30-minute call to talk about your goals and see whether coaching is right for you. <a href="free-sports-nutrition-consultation.html">Book it here</a>.</p>'),
           ('How many carbs per hour should I eat during endurance exercise?',
            '<p>For long endurance sessions and events, 60–90 g per hour is a common target, and trained athletes can reach 100–120 g/hour after gut training. Read <a href="post-carbohydrate-fueling-endurance-sports.html">the full article</a>.</p>'),
           ('Do you work with clubs and teams?', '<p>Yes. Marine gives workshops and talks for clubs, gyms and teams. See <a href="workshops.html">Workshops &amp; Talks</a>.</p>'),
           ('Can you help with weight loss?',
            '<p>Yes, without crash diets. Clients have lost weight while gaining energy and power. The focus is on sustainable habits and fuelling your training properly.</p>')]
    faq_html, faq_schema = faq_block(qas, 'Vivify Sports', 'Your questions')
    body = f"""
{hero('Questions &amp; answers', 'Sports Nutrition FAQ', 'Everything you need to know before working with Vivify Sports. Can’t find your answer? Get in touch.', btn=('Contact Marine', 'contact.html'))}
{faq_html.replace('style="padding-top:24px"', 'style="padding-top:0"', 1)}
{cta('Still have a question?', 'Book a free 30-minute call and ask Marine directly.', 'Book your free call', DISC)}"""
    page('faq.html', body, [faq_schema])

    # ------------------------------------------------------------ TESTIMONIALS
    body = f"""
{hero('What athletes say', 'Client Reviews', 'Cyclists and triathletes on working with Marine. She coaches athletes in the USA, Canada, Ireland and Finland.', btn=('Book your free discovery call', DISC))}
{b.google_reviews()}
{b.testimonials(h2_names=False)}
<section class="section-tight"><div class="wrap center"><p class="lead">Worked with Marine? <a href="{b.GBP}" target="_blank" rel="noopener">Leave a review on Google</a>. It helps other athletes find Vivify Sports.</p></div></section>
{cta('Your turn', 'Start with a free 30-minute discovery call.', 'Book your free call', DISC)}"""
    page('testimonials.html', body, [])


def _strip(h):
    import re, html
    return html.unescape(re.sub(r'<[^>]+>', '', h)).strip()

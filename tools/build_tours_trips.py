"""Tours trip pages (15, /trips/<slug>/) in the trip design (trip/pub/index.html, Dolomites).

Source of the words = each trip page's ORIGINAL Elementor data (stg-tours/backup/page-<id>.json), read in
order and sorted into the design's sections. Headings keep their live level (H2 stays H2, H3 stays H3) and
wording; body text, links and prices are copied as they are. Repeated link-only headings ("BOOK NOW") become
buttons; the "20+ / 500+ / 5★ / 10" stats become numbers (not headings).
Booking: the live WeTravel links, opened in a new tab as live.

Usage: python3 -I tools/build_tours_trips.py [slug ...]   (no slug = all 15)
Writes tourspages/page-trip-<slug>.html and stg-tours/out/list-trip-<slug>.json; push with
python3 -I tools/push_tours_list.py trip-<slug>.
"""
import os, re, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_tours_pages import fix_text, items, text_of, clean, img_tag, reviews_block, PARTNERS_H2, PAGE_CSS, L, EXT, E, YT_JS, exit_pop
from tours_img import media, webp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
IDS = json.load(open(ROOT + 'stg-tours/trip-ids.json'))
TRIPS = {t['slug']: t for t in json.load(open(ROOT + 'tours/trips-2027.json'))['trips']}
M = json.load(open(ROOT + 'stg-tours/media-webp.json'))
TYPE = {'road': 'Road', 'gf': 'Gran Fondo', 'gravel': 'Gravel'}
import importlib.util as _iu
_sp = _iu.spec_from_file_location('trm', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tours_route_maps.py')); _trm = _iu.module_from_spec(_sp); _sp.loader.exec_module(_trm)
ROUTE_NOTES = {k: v.get('note', '') for k, v in _trm.ROUTES.items()}
_SPJ = json.load(open(ROOT + 'tours/spots.json'))
SPOTS = {k: v for k, v in _SPJ.items() if not k.startswith('_')}
GUIDE_NICK = {'Giampietro': 'JP'}   # first name -> nickname (About page: Giampietro 'JP')
# guides from the About page team (photo, role; no bio there): added to a tour, or replacing a guide (Matteo 16 Nov)
TEAM = {'JP': ('Guide', 2658, 'Giampietro, JP to everyone, is retired and lives for cycling. Every week he guides mountain bike tours in his home region of Franciacorta, riding among its vineyards and wineries.'),
        'Marco': ('Support & Mechanic', 2651, 'Marco is a semi-pro rider from Lake Garda. On tour he looks after the group from the van and keeps every bike running smoothly, from the first ride to the last.'),
        'Antonio': ('Guide', 4665, 'Antonio was a professional cyclist for many years. Now he enjoys the other side of the sport: guiding our riders and sharing the roads and climbs he knows so well.'),
        'Bone': ('Support & Mechanic', 10683, 'Alessio, known as Bone, is a former pro and a stage winner at the Baby Giro. Today he is a full-time bike mechanic who loves joining our tours.'),   # bios from Matteo 16 Nov   # Bone: Alessio, photo from Matteo 16 Nov
        'Amedeo': ('Tour Guide Leader', 2214, 'A former pro cyclist, Amedeo has been a cycling tour guide and massage therapist for a decade, with almost 1,000 days on tours: one of the most experienced guides you will find.'),
        'Piero': ('Guide & Gravel Expert', 3455, 'Piero is a passionate cyclist and architect, whose eye for detail carries into his riding. He started out in downhill mountain biking before finding his true love: gravel.')}   # bios as on the live tour pages
GUIDES_SET = {'lake-garda-and-stelvio': ['Piero', 'Amedeo', 'JP'], 'lake-garda-gravel': ['Piero', 'Amedeo', 'JP']}   # the whole guide line-up for a tour (Matteo 16 Nov)
GALLERY_PHOTOS = {'lake-garda-and-stelvio': [2211, 2212, 2209, 434, 780, 650, 898, 2235, 2233]}   # Garda & Stelvio: the live gallery photos are 450-800px wide (soft); sharper Garda photos (Matteo 16 Nov)
GUIDES_ADD = {'maratona-dles-dolomites': ['JP', 'Bone'], 'dolomites': ['Bone'], 'italian-alps': ['Antonio'], 'alpine-gravel-escape': ['Antonio'], 'italys-coast-to-coast': ['Antonio', 'Marco']}   # Coast to Coast: Marco = the younger support & mechanic, not Marco "DS" (Matteo 16 Nov)
OP_LOGO = {'maratona-dles-dolomites': 'logo-mdd'}
# who may book through us (Matteo 16 Nov: our target markets as listed for Cigala on the official Maratona tour-operator page)
OP_NOTE = {'maratona-dles-dolomites': 'As an Official Tour Operator, we offer this tour to riders resident in our official target markets: '
           '<strong>Ireland, the United Kingdom, Northern Europe, North America and Australia</strong>. '
           'Not sure if your country is on the list? <a href="/contact/">Get in touch</a>: we can always ask the organisers and let you know.'}   # the Maratona logo beside "Official tour operator" (Matteo 16 Nov)
GUIDES_DROP = {'italys-coast-to-coast': {'AMEDEO'}, 'maratona-dles-dolomites': {'AMEDEO'}}   # Matteo 16 Nov
GUIDES_SWAP = {'dolomites': {'AMEDEO': 'Antonio'}, 'french-alps': {'AMEDEO': 'Bone'}, 'wonderful-slovenia': {'AMEDEO': 'Bone'}, 'lake-como-gran-fondo-il-lombardia': {'MARINE': 'JP'}}   # French Alps and Slovenia: Alessio 'Bone' in Amedeo's place (Matteo 16 Nov)
HOTEL_PIC_ORDER = {'dolomites': [1, 0]}   # live has the Andreas and Rezia photos the wrong way round (Matteo 16 Nov)
FACT_PHOTO = {'lake-garda-and-stelvio': 4856, 'wonderful-slovenia': 6280}   # the photo in Trip at a glance (Matteo 16 Nov: Garda's was soft, Slovenia's was a map)
EXTRA_PHOTO = {'italian-alps': 6102, 'alpine-gravel-escape': 6143,   # Alpine Gravel: two riders on the Stelvio road, not the hairpins already on the poster (Matteo 16 Nov)
                 # gravel photo on the road tour, Stelvio photo on the gravel tour
               'lake-garda-and-stelvio': {'GRAVEL': 7766, 'STELVIO': 2225}, 'lake-garda-gravel': 434}   # by a word of the section title when a page has several   # a photo beside "Fancy a few days on the gravel?" (Matteo 16 Nov)
# Maratona: two hotels in one text block live -> a card each, with their own photos and stars (Matteo 16 Nov)
LEVEL_FROM_DATA = {'italys-coast-to-coast'}   # Matteo 16 Nov: Coast to Coast is open to beginners too (tours/trips-2027.json)
FAQ_EDIT = {
 'italys-coast-to-coast': [(r'fitness level', None, '<p>This trip suits Beginner, Intermediate and Expert riders. The route features rolling terrain with a few climbs each day, generally 3 to 6 km long at 5 to 8%, and the support van is always there if you want a break.</p>')],
 'alpine-gravel-escape': [(r'gravel tour running at the same time', 'I see you have a road tour running at the same time, can I join one or two road rides?',
     '<p>Yes. Our <a href="https://tours.cigalacycling.com/trips/italian-alps/">Italian Alps</a> road tour runs at the same time, and both groups share the same accommodation and evening restaurants. You can swap in a road day or two: just let us know when booking and we will rent a road bike for you for the day.</p>')],
}
TRAIN = '<p>Some dedicated preparation makes a real difference. If you would like a structured plan built around this trip, visit our COACH page and Matteo can help you put together a plan based on your current level and the time you have before you travel.</p>'.replace('COACH', '<a href="https://coaching.cigalacycling.com/">cycling coaching</a>')
PACK = '<p>Beyond your usual riding kit, bring extra layers and a rain jacket: WHY Our full <a href="https://tours.cigalacycling.com/guides/what-to-pack-cycling-holiday/">guide to packing for a European cycling holiday</a> covers everything else you will need for the week.</p>'
EXTRA_FAQ = {   # Matteo 16 Nov: these tours had no FAQ live; answers only use facts already on each page
 'dolomites': [
   ('Do I need to bring my own bike, or can I rent one?', "<p>You're welcome to bring your own bike, or rent one for the week. After booking, you will receive a form to fill out via email: let us know there, and if you want to rent, add your measurements so we can prepare the right bike for you.</p>"),
   ('What fitness level do I need for this trip?', '<p>This trip suits Intermediate and Expert riders. Every day takes on famous Dolomites passes, with around 8,200 m of climbing over five days of riding, so a good level of fitness is needed to enjoy it.</p>'),
   ('What kind of support is included on this trip?', '<p>A support vehicle follows the group every day with snacks and water on route, and our ex-pro guides ride with you and share their tips.</p>'),
   ('Where do we stay?', '<p>Two nights in Canazei at Hotel Andreas (4-star) and three nights in La Villa, Alta Badia, at Hotel Rezia (3-star superior), both with breakfast included.</p>'),
   ('Is there a single room supplement?', '<p>Yes, single rooms are available at €60 per night, with limited availability.</p>'),
   ('Should I specifically train for a trip like this?', TRAIN),
   ('What should I pack for this trip?', PACK.replace('WHY', 'the mountain passes are much cooler than the valleys, even in July.'))],
 'tuscany-epic-gravel': [
   ('Do I need to bring my own bike, or can I rent one?', "<p>You're welcome to bring your own bike, or rent one for the week. After booking, you will receive a form to fill out via email: let us know there, and if you want to rent, add your measurements so we can prepare the right bike for you.</p>"),
   ('What fitness level do I need for this trip?', '<p>This trip is for Expert riders. You will ride about 450 km over five days, around 80% of it on gravel, so you need good endurance and confident bike handling on loose surfaces.</p>'),
   ('Is there an option for an e-gravel bike?', '<p>Yes, gravel e-bikes are available to rent. Let us know when you book.</p>'),
   ('What kind of support is included on this trip?', '<p>Every day comes with the full pro experience: a van with feed zones, snacks and water on route, plus guided routes by our ex-pro guides.</p>'),
   ('Is there a single room supplement?', '<p>Yes, single rooms are available at €60 per night, with limited availability.</p>'),
   ('Should I specifically train for a trip like this?', TRAIN),
   ('What should I pack for this trip?', PACK.replace('WHY', 'early June in Tuscany is usually warm, but a shower is always possible.'))],
 'cyprus-crossing-gravel': [
   ('Do I need to bring my own bike, or can I rent one?', "<p>You're welcome to bring your own bike, or rent one for the week. After booking, you will receive a form to fill out via email: let us know there, and if you want to rent, add your measurements so we can prepare the right bike for you.</p>"),
   ('What fitness level do I need for this trip?', '<p>This trip is for Expert riders: about 420 km and 8,800 m of climbing over six days on a mix of gravel and quiet mountain roads, from the coast up to Mount Olympus and back down to the sea.</p>'),
   ('What kind of support is included on this trip?', '<p>A full back-up car follows the group every day with snacks and water on route, and our guides ride with you.</p>'),
   ('Is my kit washed during the trip?', '<p>Yes, laundry of your cycling kit is included.</p>'),
   ('Is there a single room supplement?', '<p>Yes, a single room supplement is available at €50 per night.</p>'),
   ('Should I specifically train for a trip like this?', TRAIN),
   ('What should I pack for this trip?', PACK.replace('WHY', 'April is mild by the sea, but the mountains around Mount Olympus are much cooler.'))],
}
ev_km = lambda o: ' / '.join(str(n) for n in sorted(int(re.search(r'(\d+)', b).group(1)) for a, b in o)) + ' km'   # every course length, shortest first: 87 / 137 km (Matteo 16 Nov)
EVENT_DAY = {   # itinerary day -> (title, official courses); 2026 editions, checked 16 Nov (Matteo: list the options, "from" the shortest)
 'chianti-gran-fondo-strade-bianche': {5: ('GRAN FONDO STRADE BIANCHE', [('Gran Fondo', '137 km'), ('Medio Fondo', '87 km')])},
 'discover-the-algarve-granfondo': {4: ('GRAN FONDO ALGARVE', [('Granfondo', '130 km'), ('Mediofondo', '90 km')])},
 'maratona-dles-dolomites': {5: ('MARATONA DLES DOLOMITES', [('Maratona', '138 km, 4,230 m'), ('Medio', '106 km, 3,130 m'), ('Sellaronda', '55 km, 1,780 m')])},
 'lake-como-gran-fondo-il-lombardia': {5: ('GRANFONDO IL LOMBARDIA', [('Gran Fondo', '110 km, start and finish in Bergamo')])},
 'tour-of-flanders-experience': {3: ('WE RIDE FLANDERS SPORTIVE', [('Short', '79 km'), ('Medium', '133 km'), ('Long', '163 km'), ('Full Ronde', '247 km from Antwerp')])},
}
HOTEL_TEXT = {'Hotel Soleil': '<p>Located in the heart of La Villa, at the foot of the famous Gran Risa, Soleil Alpine Lifestyle Hotel blends contemporary Alpine design with the character of South Tyrol. Modern rooms, excellent dining, an indoor pool, sauna and steam bath, and dedicated cycling services make it an ideal base for the Sellaronda and the Maratona climbs.</p>'}   # shorter, in line with Rezia (Matteo 16 Nov)
HOTELS = {'maratona-dles-dolomites': [('Hotel Rezia', 3, True, 8626, [8627, 8629, 8631]), ('Hotel Soleil', 4, False, 8709, [8707, 8708])]}
DYN = set(IDS)   # the dynamic trip page on every tour (Matteo 16 Nov, after the Algarve pilot): count-up numbers, animated map badge, route drawn day by day, days sliding in
HOTEL_PIC_ORDER_IDS = {'discover-the-algarve-granfondo': [2572, 2563, 2565, 2564, 2566, 2561, 2567, 2562, 2573]}   # Vilar do Golf: the resort and pool first, not the gym
TRIP_VIDEO = {'cyprus-crossing-gravel': ('jrRjn70pquM', 3353)}   # YouTube id, cover photo (our own: no YouTube request until the visitor taps play) - Matteo 16 Nov
HERO_TALL = {'tuscany-epic-gravel'}   # about 2 cm taller (Matteo 16 Nov)
HERO_PHOTO = {'discover-the-algarve-granfondo': 710, 'dolomites': 3719,   # Dolomites: wide drone photo of the towers and the pass road, not a Maratona photo (Matteo 16 Nov)
              'italian-alps': 2225, 'french-alps': 719, 'alpine-gravel-escape': 6100,
              'italys-coast-to-coast': 4465, 'lake-como-gran-fondo-il-lombardia': 4482}   # Lake Como: a rider descending above the lake (Matteo 16 Nov)   # sharp 2560px originals (Matteo 16 Nov: the old ones looked soft)   # Dolomites / Italian Alps: photos with riders (Matteo 16 Nov)   # media id: rider in Cigala kit above an Algarve beach
HERO_DPOS = {'tuscany-epic-gravel': 'center 54%', 'tour-of-flanders-experience': '50% 65%', 'french-alps': 'center 70%', 'alpine-gravel-escape': 'center 84%', 'dolomites': 'center 45%', 'lake-como-gran-fondo-il-lombardia': 'center 55%', 'italian-alps': 'center 60%'}   # focus point on laptops (Matteo 16 Nov: Flanders showed the arch, not the riders)
HOTEL_FALLBACK = {'tour-of-flanders-experience': ('h3', 'Hotel T ****')}   # 4 stars (Matteo 16 Nov)   # live has no hotel heading: the main card (stars: add '****' once Matteo confirms)
HERO_MPOS = {'tour-of-flanders-experience': '50% 70%', 'french-alps': '45% 70%', 'alpine-gravel-escape': '30% 62%', 'dolomites': '45% 60%', 'italian-alps': '30% 60%', 'discover-the-algarve-granfondo': '80% 45%', 'chianti-gran-fondo-strade-bianche': '52% 30%'}   # focus point of the hero photo on phones
AVAIL = {'low': ('Last few spots', ''), 'mid': ('Filling up fast', ' amber'), 'high': ('Spots available', ' green')}   # wording + dot colour, same on every tour (Matteo 16 Nov)
MON = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

_sv = lambda d: f'<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{d}</svg>'
ICON = {   # line icons for the glance strip and Trip at a glance (Matteo 16 Nov)
    'route': _sv('<circle cx="5" cy="18" r="2.2"/><circle cx="19" cy="6" r="2.2"/><path d="M7 18h8.5a3.5 3.5 0 0 0 0-7h-7a3.5 3.5 0 0 1 0-7H17"/>'),
    'climb': _sv('<path d="M2 20l6.5-10 4 6 3-4.5L22 20z"/><path d="M15.5 11.5l1.8-2.7"/>'),
    'moon': _sv('<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>'),
    'cal': _sv('<rect x="3.5" y="5" width="17" height="15" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/>'),
    'level': _sv('<path d="M5 19v-4M12 19v-8M19 19V5"/>'),
    'pin': _sv('<path d="M12 21s-6.5-6.2-6.5-11a6.5 6.5 0 0 1 13 0c0 4.8-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.4"/>'),
    'group': _sv('<circle cx="9" cy="8.5" r="3"/><path d="M3.5 19a5.5 5.5 0 0 1 11 0"/><circle cx="17" cy="9.5" r="2.4"/><path d="M15.5 14.2A4.6 4.6 0 0 1 21 18.5"/>'),
    'flag': _sv('<path d="M5 21V4"/><path d="M5 4h11l-2 4 2 4H5"/>'),
    'plane': _sv('<path d="M10.5 13.5L3 11l1.5-1.5 8 .5 4-4.5a2 2 0 0 1 3 3l-4.5 4 .5 8L14 22l-2.5-7.5L8 18v2.5L6.5 22l-1-3.5L2 17.5 3.5 16H6z"/>'),
    'dot': _sv('<circle cx="12" cy="12" r="3"/>'),
}

def trim_tag(src, alt):   # the rental bike, cropped to the bike (Matteo 16 Nov: it sat small in a lot of white)
    im = webp(src, 1000, alt, trim=True)
    return f'<img src="{im["url"]}" alt="{E(im["alt"])}" loading="lazy">'

STD_GUIDE = {
 'MATTEO': ('Founder & Tours Director', 'Since founding Cigala Cycling in 2015, Matteo has led over 100 tours. A former pro and current amateur racer, Matteo is the 2022 European Champion Gran Fondo.'),
 'AMEDEO': ('Tour Guide Leader', 'A former pro cyclist, Amedeo has been a cycling tour guide and massage therapist for a decade, with almost 1,000 days on tours: one of the most experienced guides you will find.'),
 'PIERO': ('Guide & Gravel Expert', 'Piero is a passionate cyclist and architect, whose eye for detail carries into his riding. He started out in downhill mountain biking before finding his true love: gravel.')}   # the live texts most tours use
SHOWN = {'JP': 'GIAMPIETRO "JP"', 'Bone': 'ALESSIO "BONE"'}   # name and nickname, as on About (Matteo 16 Nov)
def team_card(name):
    role, photo, bio = TEAM[name]
    return (f'<article class="panel guide"><div class="ph">{img_tag(photo, 600, alt=f"{name}, {role.lower()} at Cigala Cycling Tours")}</div>'
            f'<div class="tx"><h3>{E(SHOWN.get(name, name.upper()))}</h3><div class="role">{E(role)}</div>{f"<p>{E(bio)}</p>" if bio else ""}</div></article>')

DYN_JS = """<script>(function(){var rm=matchMedia('(prefers-reduced-motion: reduce)').matches,io='IntersectionObserver' in window&&!rm;
if(io)document.documentElement.classList.add('dyn-ok');
function when(el,cb,th){if(!io){cb(el);return;}var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){o.unobserve(e.target);cb(e.target);}});},{threshold:th||.25});o.observe(el);}
document.querySelectorAll('.cl .dyn-in').forEach(function(el){when(el,function(x){x.classList.add('go');},el.classList.contains('day')?.15:.3);});
document.querySelectorAll('.cl .dyn-count .n').forEach(function(el){var t=el.lastChild;if(!t||t.nodeType!==3)return;var m=t.textContent.match(/^([\\d,]+)(.*)$/);if(!m)return;
var to=+m[1].replace(/,/g,''),suf=m[2];if(!io)return;var fmt=function(v){return v.toLocaleString('en-US')+suf;};el.style.minWidth=el.offsetWidth+'px';t.textContent=fmt(0);
when(el,function(){var t0=performance.now();(function f(n){var k=Math.min(1,(n-t0)/1400);t.textContent=fmt(Math.round(to*(1-Math.pow(1-k,3))));if(k<1)requestAnimationFrame(f);})(t0);},.5);});})();</script>"""

def raw(pid): return json.loads(json.load(open(ROOT + f'stg-tours/backup/page-{pid}.json'))['meta']['_elementor_data'] or '[]')

def faqs(data):
    """Nested accordion -> [(question, answer html)] (titles in settings, answers in the child containers)."""
    out = []
    def walk(xs):
        for e in xs:
            if e.get('widgetType') == 'nested-accordion':
                titles = [i.get('item_title', '') for i in e['settings'].get('items', [])]
                for t, child in zip(titles, e.get('elements', [])):
                    ans = ''.join(clean(v) for k, v, s in items([child]) if k == 'text')
                    out.append((t.strip(), ans))
            walk(e.get('elements', []))
    walk(data)
    return out

def classify(k, t):
    u = t.upper().replace('’', "'").strip()
    if re.match(r'^BO+K NOW', u): return 'book'
    if k == 'h3' and u.startswith('BUILD YOUR TOUR WITH US'): return 'custom-sub'
    rules = [("WHAT'S NOT INCLUDED", 'notinc'), ("WHAT'S INCLUDED", 'inc'), ('AIRPORT TRANSFER', 'transfers'), ('AT GLANCE', 'glance'),
             ('DAY TO DAY', 'd2d'), ('GALLERY', 'gallery'), ('ACCOMODATION', 'hotels'), ('ACCOMMODATION', 'hotels'), ('WHERE YOU WILL STAY', 'hotels'),
             ('BIKE RENTAL', 'bike'), ('READ OUR TESTIMONIALS', 'reviews'), ('CUSTOMISE YOUR TOUR', 'custom'), ('YOUR TOUR GUIDES', 'guides'),
             ('FREQUENTLY ASKED', 'faq'), ('PLAN YOUR TRIP', 'related'), ('OFFICIAL TOUR OPERATOR', 'operator'), ('FANCY A FEW DAYS', 'extra'), ('OPTIONAL DAY-TRIP', 'extra')]
    for w, kind in rules:
        if w in u: return kind
    if re.match(r'^ROUTE( MAP)?$', u): return 'route'
    if re.match(r'^[\d,.]+\s*[+★]?$', u): return 'stat'
    return None

def lines(h):
    """A text block -> list items: <li>s if it is a list, else its lines (paragraphs / <br>)."""
    lis = re.findall(r'<li[^>]*>(.*?)</li>', h, re.S)
    if lis: return [x.strip() for x in lis if text_of(x)]
    parts = re.split(r'<br\s*/?>|</p>\s*<p[^>]*>|\n', re.sub(r'^<p[^>]*>|</p>$', '', h.strip()))
    return [p.strip() for p in parts if text_of(p)]

def km_m(title):
    """'SELLA RONDA WITH A TWIST 80km | 2400mt' -> ('SELLA RONDA WITH A TWIST', '80 km', '2,400 m')"""
    m = re.search(r'\s*(\d[\d.,]*)\s*km\s*[|/]?\s*(\d[\d.,]*)?\s*(mt|m)?\b.*$', title, re.I)
    if not m: return title.strip(), None, None
    fmt = lambda n: f'{int(n.replace(",", "").replace(".", "")):,} m' if n else None
    return title[:m.start()].strip(), f'{m.group(1)} km', fmt(m.group(2))

def nice(t):   # headings typed in capitals live: the design shows them in capitals with CSS, words unchanged
    return t


POSTS = {p['id']: p for p in json.load(open(ROOT + 'stg-tours/backup/posts.json'))}
def related_html(sec, h1):
    """'Plan Your Trip' + 'Cycling Guides & Tips' (both H2 live) + intro + three chosen guides (live loop grid by post id)."""
    ids = next((s.get('post_query_posts_ids') for k, v, s in sec['items'] if k == 'loop-grid'), []) or []
    h2b = next((v for k, v, s in sec['items'] if k == 'h2'), '')
    lede = ''.join(f'<p>{text_of(v)}</p>' for k, v, s in sec['items'] if k == 'text')
    cards = []
    for i in ids:
        p = POSTS.get(int(i))
        if not p: continue
        t = html.unescape(p['title']['raw']); u = p['link'].replace('https://staging.tours.cigalacycling.com', L)
        ex = html.unescape(re.sub(r'<[^>]+>', '', p['excerpt']['raw'] or '')).strip()
        ph = f'<a class="ph" href="{u}">{img_tag(p["featured_media"], 900, alt=t)}</a>' if p.get('featured_media') else ''
        cards.append(f'<article class="tcard dtour">{ph}<div class="tx"><div class="by">By Tours Director Matteo Cigala</div><h3>{E(t)}</h3>'
                     f'<div class="desc"><p>{E(ex)}</p></div><div class="bottom"><div class="ctas one"><a class="btn btn-go" href="{u}">Read the guide →</a></div></div></div></article>')
    if not cards: return ''
    return (f'<section id="guides-tips"><div class="in"><div class="head"><div><h2 class="eyebrow ey2">{E(text_of(sec["h"]))}</h2>'
            f'<h2>{E(text_of(h2b))}</h2><div class="bar"></div><div class="lede">{lede}</div></div></div><div class="tgrid">{"".join(cards)}</div></div></section>')

def trip(slug):
    pid = IDS[slug]; tr = TRIPS[slug]; data = raw(pid)
    it = [x for x in items(data) if x[0] not in ('open', 'close', 'divider', 'spacer')]
    h1i = next(i for i, x in enumerate(it) if x[0] == 'h1'); h1 = it[h1i][1]
    secs, cur = [], {'kind': 'top', 'h': None, 'tag': None, 'items': []}
    for k, v, s in it[h1i + 1:]:
        if k == 'text' and cur['kind'] in ('inc', 'notinc', 'transfers', 'entry') and len(text_of(v)) < 40:   # short text lines used as box titles live
            tt = text_of(v).strip().rstrip(':').upper()
            if tt in ('AIRPORT TRANSFERS', 'AIRPORT TRANSFER'): secs.append(cur); cur = {'kind': 'transfers', 'h': text_of(v), 'tag': 'p', 'items': []}; continue
            if tt.startswith('GRAN FONDO ENTRY PRICE'): secs.append(cur); cur = {'kind': 'entry', 'h': text_of(v), 'tag': 'p', 'items': []}; continue
        if k == 'h4' and classify(k, text_of(v)) in ('inc', 'notinc', 'transfers'):   # some pages have "What's not included" as an H4
            secs.append(cur); cur = {'kind': classify(k, text_of(v)), 'h': v, 'tag': 'h4', 'items': []}; continue
        if k in ('h2', 'h3', 'h5'):
            t = text_of(v); kind = classify(k, t)
            if kind == 'book':
                cur['items'].append(('book', s.get('link', {}).get('url', ''), s)); continue
            if kind == 'custom-sub' or (kind is None and cur['kind'] in ('hotels', 'guides', 'final', 'custom') and k == 'h3') or (kind is None and cur['kind'] == 'related' and not any(x[0] == 'h2' for x in cur['items'])):
                cur['items'].append((k, v, s)); continue
            if kind is None and cur['kind'] == 'top' and k == 'h2':
                kind = 'intro'
            elif kind is None and k == 'h2' and re.sub(r'\W', '', t.upper()).startswith(re.sub(r'\W', '', text_of(h1).upper())[:6]) and secs and secs[-1]['kind'] != 'top':
                kind = 'final'
            elif kind is None and k == 'h3' and cur['kind'] in ('glance', 'route', 'd2d', 'day', 'gallery', 'inc', 'notinc', 'transfers'):
                kind = 'day'
            elif kind is None and k == 'h2' and cur['kind'] == 'hotels':
                cur['items'].append((k, v, s)); continue
            elif kind is None and k in ('h2', 'h3') and cur['kind'] == 'final':
                cur['items'].append((k, v, s)); continue
            elif kind is None:
                kind = 'other'
            moved = []   # live puts a section's photo just before its heading: it belongs to the new section
            while cur['items'] and cur['items'][-1][0] == 'img' and cur['kind'] != 'top': moved.insert(0, cur['items'].pop())
            secs.append(cur); cur = {'kind': kind, 'h': v, 'tag': k, 'items': moved}
            continue
        cur['items'].append((k, v, s))
    secs.append(cur)
    S = lambda kind: [x for x in secs if x['kind'] == kind]
    one = lambda kind: (S(kind) or [None])[0]

    # ---------- top: dates, price, deposit, companion, book link, hero photo ----------
    top = secs[0]
    texts = [v for k, v, s in top['items'] if k == 'text']
    price_h = next((v for k, v, s in top['items'] if k in ('h4', 'h3', 'h5', 'h6') and '€' in text_of(v)), '')
    price_t = text_of(price_h).replace('​', '')
    early = re.search(r'(Early bird.*)$', price_t, re.I)
    price_main = price_t[:early.start()].strip() if early else price_t
    if early and not price_main and '€' in price_t:   # 'Early bird prices until 30/05 €1299 | £1149 | $1499*' (Lake Como): the note first, then the price
        i_ = price_t.index('€'); price_main = price_t[i_:].strip()
        early = re.match(r'(.*)', price_t[:i_].strip())
    prices = [p.strip() for p in price_main.split('|')]
    book_urls = [v for k, v, s in it if k == 'book' and v] + [x[1] for x in [(k, v) for k, v, s in it] if False]
    book = next((s.get('link', {}).get('url') for k, v, s in it if k in ('h2', 'h3', 'h5') and classify(k, text_of(v)) == 'book' and s.get('link', {}).get('url')), None)
    book = book or next((v[1] for k, v, s in it if k == 'btn' and 'wetravel' in (v[1] or '')), '')
    assert 'wetravel' in book, (slug, book)
    small = [text_of(t) for t in texts[1:]]
    deposit = next((x for x in small if x.lower().startswith('deposit')), '')
    companion = next((x for x in small if 'companion' in x.lower()), '')
    stay = next((x for x in small if 'shorter or longer' in x.lower()), '')
    other_small = [x for x in small if x not in (deposit, companion, stay)]
    dates_live = text_of(texts[0]) if texts else ''
    hero_src = next((v for k, v, s in top['items'] if k == 'img'), None) or json.load(open(ROOT + f'stg-tours/backup/page-{pid}.json')).get('featured_media')
    # ---------- glance ----------
    g = one('glance'); glance = []; g_trans = []
    KEYS = r'(START\s*&(?:amp;)?\s*FINISH(?: LOCATION)?|START(?: LOCATION)?|FINISH(?: LOCATION)?|DAYS RIDING|RIDING DAYS|TOTAL DISTANCE|TOTAL ELEVATION|TOTAL CLIMBING|DISTANCE|ELEVATION|CLIMBING|GROUP SIZE|LEVEL|LONGEST DAY|DIFFICULTY)'
    if g:
        in_trans = False
        for k, v, s in g['items']:
            if k == 'text':
                for ln in lines(v):
                    t = text_of(ln).strip()
                    if not t: continue
                    if re.match(r'(?i)^airport transfers?:?$', t): in_trans = True; continue
                    if in_trans:   # "Inbound 28/07 12:00 pm noon from Geneva Airport (GVA)"
                        m = re.match(r'(?i)^(inbound|outbound|arrival|departure)\s*:?\s*(.*)$', t)
                        g_trans.append((m.group(1).capitalize(), m.group(2)) if m else ('', t)); continue
                    m = re.match(r'(?i)^' + KEYS + r'\s*:*\s*(.+)$', t)
                    if m: glance.append((m.group(1).capitalize(), E(m.group(2).strip().lstrip(':：-– ').strip())))
                    else: glance.append(('', ln))
    glance = [(a, E(tr['level'].replace(', ', ', ')) if a.upper() == 'LEVEL' and slug in LEVEL_FROM_DATA else b) for a, b in glance]   # level changed by Matteo
    gl = {a.upper(): b for a, b in glance}
    get = lambda *keys: next((text_of(gl[k]) for k in gl for w in keys if w in k), '')
    # ---------- hero ----------
    hero_alt = f'{text_of(h1).title()} bike tour - Cigala Cycling Tours'
    tags = [TYPE[tr['type']], tr['country'], tr['level'].replace(', ', ' · ')]
    # Matteo 16 Nov: the country as a round flag, the level with the same 3-bar meter as the tour cards
    fl = M.get('flag-' + {'Italy': 'it', 'France': 'fr', 'Portugal': 'pt', 'Slovenia': 'si', 'Cyprus': 'cy', 'Belgium': 'be'}.get(tr['country'], ''))
    lb = {'beginner': 1, 'intermediate': 2, 'expert': 3}.get(tr['level'].split(',')[0].strip().lower(), 2)
    lmeter = '<span class="lm" aria-hidden="true">' + ''.join('<i class=on></i>' if i < lb else '<i></i>' for i in range(3)) + '</span>'
    tags_html = (f'<span class="tag{" dot" if tr["type"] != "gravel" else " gdot"}">{E(tags[0])}</span>'
                 + f'<span class="tag">{E(tags[1])}</span>'   # the country by name (Matteo 16 Nov: the flags stay on the cards only)
                 + f'<span class="tag tlvl">{lmeter}{E(tags[2])}</span>')
    pr = prices[0] if prices else ''
    pr_rest = ' · '.join(prices[1:])
    li = ''.join(f'<li><span>{E(a)}</span><span>{E(b)}</span></li>' for a, b in [x for x in [
        ('Deposit', re.sub(r'(?i)^deposit\s*', '', deposit)) if deposit else None,
        ('Non-cycling companion', re.sub(r'(?i).*companion\s*(for)?\s*', '', companion)) if companion else None,
        ('Group size', re.split(r'\s*\(', get('GROUP'))[0]) if get('GROUP') else None] if x])   # short form here; the full text is in the Route facts
    TC = f'{L}/terms-conditions/#rider-eligibility'   # the Expert tours rules in the terms (Matteo 16 Nov)
    extra_small = ''.join(f'<p class="note">{E(x)}</p>'.replace('Expert', f'<a href="{TC}">Expert</a>') if re.match(r'(?i)^level\b', x) else f'<p class="note">{E(x)}</p>' for x in other_small)
    stay_html = (f'<p class="note">{E(stay)}</p>'.replace('contact us', f'<a href="{L}/contact/">contact us</a>')) if stay else ''
    sp = SPOTS.get(slug, _SPJ.get('_default'))
    av_txt, av_cls = AVAIL.get(sp, AVAIL['high'])
    live_ = ' live' if sp in ('low', 'mid') else ''   # only red and amber pulse: urgency stands out (Matteo 16 Nov)
    spots_html = f'<div class="spots av-{sp}"><span class="dot{live_}{av_cls}" aria-hidden="true"></span>{E(av_txt)}</div>'
    card = M.get('trip-' + slug)   # the trip's photo (tour cards); the live top image is a designed poster, shown next to the intro
    hero_img = (f'<img src="{card["url"]}" alt="{E(card["alt"])}">' if card else img_tag(hero_src, 2000, alt=hero_alt, lazy=False))
    if slug in HERO_PHOTO:   # a hero photo of its own (Matteo 16 Nov: the Algarve card photo was also used further down)
        hero_img = img_tag(HERO_PHOTO[slug], 2000, alt=hero_alt, lazy=False)
    hero_img = hero_img.replace('<img ', f'<img style="--mpos:{HERO_MPOS.get(slug, "50% 30%")};--dpos:{HERO_DPOS.get(slug, "center 40%")}" ', 1)   # phones: where the rider is in the photo
    import datetime as _dt
    _nn = (_dt.date.fromisoformat(tr['end']) - _dt.date.fromisoformat(tr['start'])).days   # days and nights from the 2027 dates (Matteo 16 Nov: not said anywhere at the top)
    dn_html = (f'<div class="dn"><span>{ICON["cal"]}{_nn + 1} days</span><span>{ICON["moon"]}{_nn} nights</span>'
               f'<span>{ICON["route"]}{E(tr["distance"])}</span><span>{ICON["climb"]}{E(tr["climbing"])}</span></div>')   # + distance and climbing (Matteo 16 Nov)
    hero = f'''<div class="hero thero{" tall" if slug in HERO_TALL else ""}">
  {hero_img}
  <div class="in">
    <div>
      <div class="crumbs"><a href="{L}/" {EXT}>Home</a> / <a href="{L}/trips/" {EXT}>Bike tours</a> / {E(tr['name'])}</div>
      <div class="tags">{tags_html}</div>
      <h1>{E(h1)}</h1>
      <div class="dates">{E(dates_live)}</div>
      {dn_html}
      {'<a class="btn btn-ghost hvid" href="#video"><span class="pl" aria-hidden="true"></span>Watch the video</a>' if slug in TRIP_VIDEO else ''}
    </div>
    <aside class="book bk2" aria-label="Price and booking">
      <div class="bk-top">
        <span class="lab">Price per person</span>
        <div class="price">{E(pr)}<small>{E(pr_rest)}</small></div>
        {f'<span class="early">{E(early.group(1).strip())}</span>' if early else ''}
        {spots_html}
      </div>
      <ul>{li}</ul>
      <div class="bk-cta"><a class="btn btn-go btn-lg" href="{E(book)}" target="_blank" rel="noopener">Book now →</a></div>
      {f'<div class="bk-notes">{stay_html}{extra_small}</div>' if stay_html or extra_small else ''}
    </aside>
  </div>
</div>'''
    # ---------- glance strip ----------
    dist, climb, days_riding = get('DISTANCE'), get('CLIMBING', 'ELEVATION'), get('DAYS RIDING', 'RIDING DAYS')
    from datetime import date as _d
    nights = (_d.fromisoformat(tr['end']) - _d.fromisoformat(tr['start'])).days
    lvl = tr['level']; bars = {'beginner': 1, 'intermediate': 2, 'expert': 3}.get(lvl.split(',')[0].strip().lower(), 2)
    meter = '<span class="lm" aria-hidden="true">' + ''.join('<i class=on></i>' if i < bars else '<i></i>' for i in range(3)) + '</span>'
    short = lambda x: re.split(r'\s*(?:\(|approx|apprx|depending)', x, flags=re.I)[0].strip() or x   # the strip shows the number; the full line is in Trip at a glance
    cells = [('route', short(dist or tr['distance']), 'Total distance'), ('climb', short(climb or tr['climbing']).lstrip('+').replace(' mt', ' m'), 'Total climbing'),
             ('cal', short(days_riding) if days_riding else f'{nights + 1} days', 'Days riding' if days_riding else f'{nights} nights'),
             ('level', lvl.replace(', ', ' · '), 'Level')]   # 4 cells: one full row, a closed box (Matteo 16 Nov)
    strip = ''.join(f'<div><span class="gi" aria-hidden="true">{ICON[ic]}</span><div><div class="n{" sm" if len(n) > 12 else ""}">{meter if ic == "level" else ""}{E(n)}</div><div class="l">{E(l)}</div></div></div>' for ic, n, l in cells if n)
    glance_html = f'<div class="in" style="padding-top:28px"><div class="panel glance g4{" dyn-count" if slug in DYN else ""}" aria-label="Trip at a glance">{strip}</div></div>'
    # ---------- sections ----------
    def H(sec, eyebrow, fallback=None, tag=None):
        t = re.sub(r'<[^>]+>', '', sec['h']).replace('​', '').strip() if sec and sec['h'] else fallback
        tg = (sec['tag'] if sec and sec['tag'] in ('h2', 'h3') else None) or tag or 'h2'
        return f'<div class="head"><div><div class="eyebrow">{eyebrow}</div><{tg} class="sh">{E(t)}</{tg}><div class="bar"></div></div></div>'
    out = [hero, glance_html]
    nav = []
    intro = one('intro')
    if intro:
        paras = ''.join(clean(v) for k, v, s in intro['items'] if k == 'text')
        pst = M.get('poster-' + slug)   # the poster with our map badge (tools/tours_posters.py)
        pb = M.get('posterbase-' + slug) if slug in DYN else None
        if pb and os.path.exists(ROOT + f'tourspages/maps/badge-{slug}.svg'):   # the map draws itself on the poster's tile
            bsvg = open(ROOT + f'tourspages/maps/badge-{slug}.svg').read()
            cls = iter(['bf', 'br', 'bh', 'bo'] if bsvg.count('<path') == 4 else ['bf', 'br', 'bo'])
            bsvg = re.sub(r'<path ', lambda m_: f'<path class="{next(cls)}" pathLength="1" ', bsvg)
            pst = dict(pb, alt=pst['alt'] if pst else pb['alt'])
            cimg = f'<div class="cardimg pdyn dyn-in"><img src="{pst["url"]}" alt="{E(pst["alt"])}" loading="lazy"><div class="pbadge" aria-hidden="true">{bsvg}</div></div>'
        else: cimg = (f'<div class="cardimg"><img src="{pst["url"]}" alt="{E(pst["alt"])}" loading="lazy"></div>' if pst else
                f'<div class="cardimg">{img_tag(hero_src, 1200, alt=hero_alt)}</div>') if hero_src and card else ''
        out.append(f'<section id="overview"><div class="in split"><div>{H(intro, "The trip")}<div class="prose">{paras}</div></div>{cimg}</div></section>')
        nav.append(('overview', 'Overview'))
    if slug in TRIP_VIDEO:   # the trip on film, right after the intro (Matteo 16 Nov); YouTube loads only when the visitor taps play (YT_JS, youtube-nocookie)
        vid, cover = TRIP_VIDEO[slug]
        out.append(f'<section id="video" style="padding-top:28px"><div class="in"><div class="head"><div><div class="eyebrow">Watch the trip</div>'
                   f'<p class="band-title">{E(re.sub(r"\s*\|\s*Gravel$", "", tr["name"]))} on film</p><div class="bar"></div></div></div>'
                   f'<div class="panel vcard tvid"><button type="button" class="yt" data-id="{vid}" aria-label="Play the {E(re.sub(r"\s*\|\s*Gravel$", "", tr["name"]))} video">'
                   f'{img_tag(cover, 1600, alt=f"{tr["name"]} gravel cycling tour video - Cigala Cycling Tours")}<span class="play" aria-hidden="true"></span></button></div></div></section>')
        nav.append(('video', 'Video'))
    op = one('operator')
    if op:
        logo = next((v for k, v, s in op['items'] if k == 'img'), None)
        if logo: logo_html = img_tag(logo, 400, cls="oplogo")
        elif slug in OP_LOGO: lg = M[OP_LOGO[slug]]; logo_html = f'<img class="oplogo" src="{lg["url"]}" alt="{E(lg["alt"])}" loading="lazy">'
        else: logo_html = ''
        note = f'<p class="opnote">{OP_NOTE[slug]}</p>' if slug in OP_NOTE else ''
        out.append(f'<section style="padding-top:28px"><div class="in"><div class="panel opbox"><div class="optext">{H(op, "Official partner")}{note}</div>{logo_html}</div></div></section>')
    route = one('route')
    # our own route map (tools/tours_route_maps.py, Cigala style) for every trip; the live map image only as a fallback
    mp = ROOT + f'tourspages/maps/day-{slug}.svg'   # day-by-day routes on real roads (tools/tours_day_routes.py, Matteo 16 Nov)
    if not os.path.exists(mp): mp = ROOT + f'tourspages/maps/{slug}.svg'
    svg = open(mp).read().replace('aria-label="Route map"', f'aria-label="{E(text_of(h1).title())} bike tour route map by Cigala Cycling Tours"') if os.path.exists(mp) else ''
    if svg and slug in DYN:   # the route draws itself, one day after the other
        svg = svg.replace('<svg class="rmap dmap"', '<svg class="rmap dmap anim dyn-in"', 1)
        svg = re.sub(r'<path id="dr(\d+)"', r'<path id="dr\1" pathLength="1"', svg)
        _n = iter(range(99)); svg = re.sub(r'<g class="(dr|db)" data-d="(\d+)"', lambda m_: f'<g class="{m_.group(1)}" data-d="{m_.group(2)}" style="--i:{m_.group(2)}"', svg)
    rimg = None
    if route and not svg:
        rimg = next((v for k, v, s in route['items'] if k == 'img'), None)
        for k, v, s in route['items']:
            if rimg is None and k == 'e-image':
                try: rimg = s['image']['value']['src']['value']['id']['value']
                except (KeyError, TypeError): pass
    def ficon(a):
        u = a.upper()
        for w, ic in (('START', 'pin'), ('FINISH', 'pin'), ('DAYS', 'cal'), ('DISTANCE', 'route'), ('ELEVATION', 'climb'), ('CLIMB', 'climb'),
                      ('GROUP', 'group'), ('LEVEL', 'level'), ('DIFFICULTY', 'level'), ('LONGEST', 'flag')):
            if w in u: return ICON[ic]
        return ICON['dot']
    facts = ''.join(f'<div><span class="fi" aria-hidden="true">{ficon(a)}</span><dt>{E(a)}</dt><dd>{b}</dd></div>' for a, b in glance if a)
    if g_trans and not one('inc'):   # shown as the transfer band under What's included instead
        facts += '<div class="ftrans"><span class="fi" aria-hidden="true">' + ICON['plane'] + '</span><dt>Airport transfers</dt><dd>' + ''.join(
            f'<span class="tl"><b>{E(a)}</b> {E(b)}</span>' if a else f'<span class="tl">{E(b)}</span>' for a, b in g_trans) + '</dd></div>'
    g_tag = (g['tag'] if g else 'h3')
    g_title = re.sub(r'<[^>]+>', '', g['h']).strip() if g else ''
    gp = [x['id'] for gs in S('gallery') for k, v, s_ in gs['items'] if k == 'gallery' for x in s_.get('gallery', [])] + [v for gs in S('gallery') for k, v, s_ in gs['items'] if k == 'img']
    gp = GALLERY_PHOTOS.get(slug) or list(dict.fromkeys(gp))
    if slug in FACT_PHOTO: gp = [FACT_PHOTO[slug]]
    fph = (f'<figure class="fphoto">{img_tag(gp[9] if len(gp) > 9 else gp[5] if 5 < len(gp) < 9 else gp[-1], 900, alt=f"Riders on the {text_of(h1).title()} bike tour - Cigala Cycling Tours")}</figure>' if gp else '')   # fills the box beside a long map (Matteo 16 Nov)
    dl = f'<dl class="panel facts"><{g_tag} class="facts-h">{E(g_title)}</{g_tag}>{facts}{fph}</dl>' if facts else ''
    note = ROUTE_NOTES.get(slug, '')
    map_html = svg or (img_tag(rimg, 1400, alt=f"{text_of(h1).title()} bike tour map by Cigala Cycling Tours") if rimg else '')
    dmeta = json.load(open(ROOT + 'tours/routes/days-meta.json')).get(slug) if 'day-' in mp else None
    if dmeta and svg:   # the day list under the map: colour, day, title and distance from the itinerary; hover or tap highlights the day
        dl_ = []
        for n, d in enumerate(S('day'), 1):
            if str(n) not in dmeta: continue
            t, km, up = km_m(text_of(d['h']))
            if n in EVENT_DAY.get(slug, {}): t, opts_ = EVENT_DAY[slug][n]; km = ev_km(opts_)
            kmv = km or re.search(r'(\d+)\s*km', text_of(''.join(v for k, v, s_ in d['items'] if k == 'text'))) and f"{re.search(r'(\d+)\s*km', text_of(''.join(v for k, v, s_ in d['items'] if k == 'text'))).group(1)} km"
            dl_.append(f'<li><button type="button" data-d="{n}"><span class="sw" style="background:{dmeta[str(n)]["color"]}">{n}</span>'
                       f'<span class="dt">{E(t)}</span>{f"<span class=dk>{E(kmv)}</span>" if kmv else ""}</button></li>')
        map_html += f'<ol class="dleg" aria-label="Days on the map">{"".join(dl_)}</ol>'
    if map_html or dl:
        head = H(route, 'Where you ride') if route else '<div class="head"><div><div class="eyebrow">Where you ride</div><p class="band-title">Route</p><div class="bar"></div></div></div>'
        out.append(f'<section id="route"><div class="in">{head}<div class="route"><div class="map">{map_html}'
                   f'{f"<p class=mapnote>{E(note)}</p>" if note else ""}</div>{dl}</div></div></section>')
        nav.append(('route', 'Route'))
    days = S('day')
    if days:
        d2d = one('d2d')
        gpx = ''.join(f'<p class="gpx">{text_of(v)}</p>' for k, v, s in (d2d['items'] if d2d else []) if k == 'text')
        lis = []
        for n, d in enumerate(days, 1):
            t, km, up = km_m(text_of(d['h']))
            evo = ''
            if n in EVENT_DAY.get(slug, {}):   # an event day: the official courses, "from" the shortest (Matteo 16 Nov)
                t, opts_ = EVENT_DAY[slug][n]; up = None
                km = ev_km(opts_)
                evo = f'<div class="evopts"><span>{"Choose your course:" if len(opts_) > 1 else "The course:"}</span> ' + ''.join(f'<span class="evo"><b>{E(a)}</b> {E(b)}</span>' for a, b in sorted(opts_, key=lambda o: int(re.search(r'(\d+)', o[1]).group(1)))) + '</div>'
            chips = (f'<span class="chip km">{km}</span>' if km else '') + (f'<span class="chip up">{up}</span>' if up else '')
            body = ''.join(clean(v) for k, v, s in d['items'] if k in ('text',)) + ''.join(f'<p>{clean(v)}</p>' for k, v, s in d['items'] if k in ('h4', 'h5', 'h6'))
            tg = d['tag'] if d['tag'] in ('h2', 'h3') else 'h3'
            lis.append(f'<li class="day"><div class="num"><span><small>DAY</small>{n}</span></div><div class="panel box"><{tg}>{E(t)}</{tg}>'
                       f'{f"<div class=meta>{chips}</div>" if chips else ""}{evo}<div class="prose">{body}</div></div></li>')
        head = H(d2d, 'Itinerary') if d2d else '<div class="head"><div><div class="eyebrow">Itinerary</div><p class="band-title">Day by day</p><div class="bar"></div></div></div>'
        if slug in DYN: lis = [x.replace('<li class="day">', '<li class="day dyn-in">', 1) for x in lis]
        out.append(f'<section id="itinerary"><div class="in">{head}{gpx}<ol class="days">{"".join(lis)}</ol></div></section>')
        nav.append(('itinerary', 'Day by day'))
    for ex in S('extra') + S('other'):
        body = ''.join(clean(v) for k, v, s in ex['items'] if k == 'text') + ''.join(f'<p>{clean(v)}</p>' for k, v, s in ex['items'] if k in ('h4', 'h5', 'h6'))
        btns = ''.join(f'<a class="btn btn-go" href="{E(u)}">{E(t.capitalize())} →</a>' for k, (t, u), s in [(k, v, s) for k, v, s in ex['items'] if k == 'btn'] if u)
        xp = EXTRA_PHOTO.get(slug)
        if isinstance(xp, dict): xp = next((v for w, v in xp.items() if w in text_of(ex['h']).upper()), None)
        imgs = [v for k, v, s in ex['items'] if k == 'img'] or ([xp] if xp and ex['kind'] == 'extra' else [])
        vid = next((re.search(r'(?:v=|youtu\.be/)([\w-]{11})', s.get('youtube_url', '')) for k, v, s in ex['items'] if k == 'video'), None)
        media_html = (f'<div class="vcard panel" style="margin-top:16px"><button type="button" class="yt" data-id="{vid.group(1)}" aria-label="Play the video">'
                      f'<img src="https://i.ytimg.com/vi/{vid.group(1)}/hqdefault.jpg" alt="{E(text_of(ex["h"]))} video" loading="lazy"><span class="play" aria-hidden="true"></span></button></div>') if vid else ''
        if len(imgs) == 1 and not vid:   # one photo (the Maratona jersey): photo on one side, text on the other (Matteo 16 Nov: too much black)
            ph_ = img_tag(imgs[0], 1200, alt=f"{text_of(h1).title()} - Cigala Cycling Tours")   # the jersey: original photo on its own grey (Matteo 16 Nov)
            out.append(f'<section><div class="in"><div class="panel xbox xsplit{" xcover" if xp else ""}"><div class="xph">{ph_}</div>'
                       f'<div class="xtx">{H(ex, "Make it yours" if ex["kind"] == "extra" else "Good to know")}<div class="prose">{body}</div>{f"<div class=ctas>{btns}</div>" if btns else ""}</div></div></div></section>')
            continue
        if imgs: media_html += '<div class="gal3" style="margin-top:16px">' + ''.join(img_tag(x, 1200, alt=f'{text_of(h1).title()} - Cigala Cycling Tours') for x in imgs[:3]) + '</div>'
        out.append(f'<section><div class="in"><div class="panel xbox">{H(ex, "Make it yours" if ex["kind"] == "extra" else "Good to know")}'
                   f'<div class="prose">{body}</div>{f"<div class=ctas>{btns}</div>" if btns else ""}{media_html}</div></div></section>')
    inc, notinc, trans = one('inc'), one('notinc'), one('transfers')
    if inc:
        inc_li = ''.join(f'<li><span>{x}</span></li>' for k, v, s in inc['items'] if k == 'text' for x in lines(clean(v)))
        # Matteo 16 Nov: no stack of boxes on the right. Included | Not included side by side, then the airport transfers
        # and the Gran Fondo entry prices as full-width bands underneath.
        no_html = ''
        if notinc:
            no_li = ''.join(f'<li><span>{x}</span></li>' for k, v, s in notinc['items'] if k == 'text' for x in lines(clean(v)))
            no_html = f'<div class="panel no"><{notinc["tag"]} class="inh">{E(text_of(notinc["h"]))}</{notinc["tag"]}><ul>{no_li}</ul></div>'
        bands = ''
        if trans or g_trans:
            rows, notes_ = [], []
            pend, gr = '', []   # transfers listed in Trip at a glance (French Alps, Flanders, Slovenia...): label, date, then details lines
            for a_, b_ in ([] if trans else g_trans):
                if a_ and not b_: pend = a_; continue
                m = re.match(r"^\s*(\d{1,2}/\d{1,2}(?:/\d{2,4})?)\s*(.*)$", b_)
                if m: gr.append([m.group(1), a_ or pend, [m.group(2)] if m.group(2) else []]); pend = ''
                elif gr: gr[-1][2].append(b_.strip())
                else: notes_.append(E(b_))
            for d_, lab_, parts in gr:
                main_ = re.sub(r'(?i)\bnoon\s+', '', parts[0]) if parts else ''
                main_ = re.sub(r'^(\d{1,2}:\d{2}\s*(?:am|pm)?\s*)from\b', r'\1From', main_)
                rows.append([d_, main_ + (f' ({", ".join(parts[1:])})' if len(parts) > 1 else '')])   # no Inbound/Outbound label (Matteo 16 Nov)
            for k, v, s in (trans['items'] if trans else []):
                if k != 'text': continue
                for x in lines(clean(v)):
                    t = text_of(x).strip()
                    m = re.match(r"^\s*(\d{1,2}/\d{1,2}(?:/\d{2,4})?)\s*(.*)$", t)
                    if m: rows.append([m.group(1), m.group(2)])
                    elif rows and not rows[-1][1]: rows[-1][1] = t   # the date on its own line, the details on the next
                    elif rows and re.match(r'^[-–\s]*\d{1,2}:\d{2}', t): rows[-1][1] += ' - ' + t.strip('- –')   # a pick-up time on its own line belongs to the transfer above
                    elif re.match(r'(?i)^(inbound|outbound)$', t): continue   # labels on their own line: not shown (Matteo 16 Nov)
                    else: notes_.append(x)
            lv_ = [n for n in notes_ if re.search(r'(?i)leaves at\s*\d', text_of(n))]
            if lv_ and len(lv_) == len(rows):   # 'Airport transfer leaves at 11:00 am' notes (Lake Como): the times belong to the transfers, in order
                for r_, n_ in zip(rows, lv_):
                    mm = re.search(r'(?i)leaves at\s*(\d{1,2}:\d{2}\s*(?:am|pm)?)(.*)$', text_of(n_))
                    r_[1] += ' - ' + mm.group(1) + (' ' + mm.group(2).strip() if mm.group(2).strip() else '')
                notes_ = [n for n in notes_ if n not in lv_]
            def tparts(t):   # '... Airport - 13:00 pm - 19:30 pm' -> text and the pick-up times (Matteo 16 Nov: show them)
                tm = [f'{int(h):02d}:{mi}' for h, mi in re.findall(r'(\d{1,2}):(\d{2})\s*(?:am|pm)?', t, re.I)]
                txt = re.sub(r'\s*-?\s*\d{1,2}:\d{2}\s*(?:am|pm)?', '', t, flags=re.I).strip(' -–')
                txt = re.sub(r'\s+at(?=\s*(?:\(|$))', '', txt).strip(' -–')   # 'Airport at 10:30am' -> 'Airport' (the time is a chip)
                txt = re.sub(r'(?i)^at\s*(?=from\b)', '', txt).strip()   # '22/04/27 at 21:30 from Paphos' -> 'From Paphos' (Cyprus)
                txt = txt[:1].upper() + txt[1:]
                return txt, tm
            cards = ''
            for d, t in rows:
                txt, tm = tparts(t)
                chips_ = ''.join(f'<span class="tt">{x}</span>' for x in tm)
                cards += (f'<div class="tcard2"><span class="ic" aria-hidden="true">{ICON["plane"]}</span><div><b>{E(d)}</b><span>{E(txt)}</span>'
                          + (f'<span class="tts">{"Pick-up times" if len(tm) > 1 else "Pick-up"}: {chips_}</span>' if tm else '') + '</div></div>')
            tt_ = trans["tag"] if trans else 'p'
            bands += (f'<div class="panel tband"><{tt_} class="inh">{E(text_of(trans["h"]).rstrip(":")) if trans else "Airport transfers"}</{tt_}><div class="trow">{cards}</div>'
                      + ''.join(f'<p class="tnote">{x}</p>' for x in notes_) + '</div>')
        ent = one('entry')
        if ent:   # Gran Fondo entry prices (Strade Bianche): the grid prices as tiles, then the notes
            ls_ = [x for k, v, s in ent['items'] if k == 'text' for x in lines(clean(re.sub(r'(€)(?=Grid)', r'\1<br>', v)))]
            grid_ = [re.match(r'^\s*(Grid \d+)\s*\(([^)]*)\)\s*:?\s*(.*)$', text_of(x)) for x in ls_]
            tiles = ''.join(f'<div class="ptile"><span>{E(m.group(1))}</span><b>{E(m.group(3))}</b><small>Places {E(m.group(2))}</small></div>' for m in grid_ if m)
            nts = ''.join(f'<p class="tnote">{x}</p>' for x, m in zip(ls_, grid_) if not m)
            bands += f'<div class="panel tband"><p class="inh">{E(text_of(ent["h"]).rstrip("*"))}</p><div class="prow">{tiles}</div>{nts}</div>'
        out.append(f'<section id="included"><div class="in">{H(inc, "The details")}<div class="inc2"><div class="panel yes"><p class="inh">Included in the price</p><ul>{inc_li}</ul></div>{no_html}</div>'
                   f'{bands}</div></section>')
        nav.append(('included', "What's included"))
    for gsec in S('gallery'):
        pics = GALLERY_PHOTOS.get(slug) or ([x['id'] for k, v, s in gsec['items'] if k == 'gallery' for x in s.get('gallery', [])] + [v for k, v, s in gsec['items'] if k == 'img'])
        seen = []; [seen.append(p) for p in pics if p not in seen]
        if not seen: continue
        n_ = 9 if len(seen) >= 9 else 5 if len(seen) >= 5 else len(seen)   # big photo + 4 or 8: the grid has no empty cells (Matteo 16 Nov)
        figs = ''.join(f'<figure{" class=g-big" if n == 0 and n_ >= 5 else ""}>{img_tag(p, 1400 if n == 0 else 900, alt=f"{text_of(h1).title()} bike tour - Cigala Cycling Tours")}</figure>' for n, p in enumerate(seen[:n_]))
        out.append(f'<section id="gallery"><div class="in">{H(gsec, "Real riders, real roads")}<div class="gallery g{n_}">{figs}</div></div></section>')
    hs = one('hotels')
    if hs:
        names = [(k, v) for k, v, s in hs['items'] if k == 'h3']
        notes = ''.join(f'<h2 class="hnote">{E(text_of(v))}</h2>' for k, v, s in hs['items'] if k == 'h2')
        mt = re.match(r'^\s*(ACCOM+ODATION|WHERE YOU WILL STAY)\s+(\S.*)$', text_of(hs['h']), re.I)
        if mt:   # one live heading holds both: split it into the section title and the hotel name
            names.insert(0, (hs['tag'] if hs['tag'] in ('h2', 'h3') else 'h3', mt.group(2)))
            hs = dict(hs, h=mt.group(1))
        txt = ''.join(clean(v) for k, v, s in hs['items'] if k == 'text')
        pics = [x['id'] for k, v, s in hs['items'] if k == 'gallery' for x in s.get('gallery', [])] + [v for k, v, s in hs['items'] if k == 'img']
        if not names and slug in HOTEL_FALLBACK: names = [HOTEL_FALLBACK[slug]]
        if slug in HOTEL_PIC_ORDER:
            o_ = HOTEL_PIC_ORDER[slug]; pics = [pics[i] for i in o_] + pics[len(o_):]
        if slug in HOTEL_PIC_ORDER_IDS: pics = HOTEL_PIC_ORDER_IDS[slug]
        hotels_ = []
        for n, (tg, v) in enumerate(names):
            t = text_of(v); stars = len(re.findall(r'\*', t)); sup = bool(re.search(r'\*\s*S\b', t))
            nm = re.sub(r'[*]+\s*S?\s*$', '', t).strip()
            if nm: hotels_.append((n, tg, nm, stars, sup))
        def hcard(n, tg, nm, stars, sup, body='', cls=''):
            ph = f'<div class="ph">{img_tag(pics[n], 1200, alt=f"{nm.title()} - {text_of(h1).title()} bike tour")}</div>' if n < len(pics) else ''
            st = (f'<div class="stars" aria-label="{stars} stars{" superior" if sup else ""}">{"★" * stars}{"<span class=sup>S</span>" if sup else ""}</div>') if stars else ''
            return f'<article class="panel hotel{cls}">{ph}<div class="tx"><div class="eyebrow">Your hotel</div>{st}<{tg}>{E(nm)}</{tg}>{body}</div></article>'
        if slug in HOTELS:   # one card per hotel, each with its own text, stars and photos
            paras = re.split(r'(?=<p><strong>)', txt)
            def htext(name):
                if name in HOTEL_TEXT: return HOTEL_TEXT[name]
                seg = next((x for x in paras if name.lower() in x.lower()[:120]), '')
                seg = re.sub(r'<strong>.*?</strong>(\s*<br\s*/?>)?', '', seg, count=1, flags=re.S)
                return seg
            cards_html = '<div class="hotels hcards">'
            for nm, st_n, sup, main, extra_ in HOTELS[slug]:
                body = htext(nm)   # the hotel's own paragraphs (Soleil has two)
                stars_ = f'<div class="stars" aria-label="{st_n} stars{" superior" if sup else ""}">{"★" * st_n}{"<span class=sup>S</span>" if sup else ""}</div>'
                thumbs = ''.join(img_tag(x, 600, alt=f'{nm} - {text_of(h1).title()} bike tour') for x in extra_)
                cards_html += (f'<article class="panel hotel hx"><div class="ph">{img_tag(main, 1200, alt=f"{nm} - {text_of(h1).title()} bike tour")}</div>'
                               f'<div class="tx"><div class="eyebrow">Your hotel</div>{stars_}<h3>{E(nm)}</h3><div class="prose">{body}</div>'
                               f'<div class="hthumbs n{len(extra_)}">{thumbs}</div></div></article>')
            cards_html += '</div>'
            intro_html, pics = '', []
            hotels_ = HOTELS[slug]
        elif len(hotels_) == 1:   # one hotel: photo and text side by side in one card (Matteo 16 Nov: no big empty black area)
            cards_html = hcard(*hotels_[0], body=f'<div class="prose">{txt}</div>{notes}', cls=' hotel1')
            intro_html = ''
        else:
            cards_html = '<div class="hotels">' + ''.join(hcard(*h, cls=' wide' if len(hotels_) % 2 and i == len(hotels_) - 1 else '') for i, h in enumerate(hotels_)) + '</div>'
            intro_html = f'<div class="prose dprose">{txt}</div>{notes}'
        rest = pics[len(hotels_):]
        k = 8 if len(rest) >= 8 else 4 if len(rest) >= 4 else 3 if len(rest) == 3 else 0   # full rows only
        strip_html = (f'<div class="strip s{4 if k != 3 else 3}">' + ''.join(img_tag(p, 600, alt=f'{text_of(h1).title()} hotel - Cigala Cycling Tours') for p in rest[:k]) + '</div>') if k else ''
        out.append(f'<section id="hotels"><div class="in">{H(hs, "Where you stay")}{intro_html}{cards_html}{strip_html}</div></section>')
        nav.append(('hotels', 'Hotels'))
    bk = one('bike')
    if bk:
        bimg = next((v for k, v, s in bk['items'] if k == 'img'), None)
        dl, lede = [], []
        for k, v, s in bk['items']:
            if k != 'text': continue
            for ln in lines(clean(v)):
                tl_ = html.unescape(text_of(ln)).replace('\u200b', '').strip()
                tl_ = re.sub(r'^(?:START\s*&\s*)?F+RAMESET\s*:?\s*', 'FRAMESET: ', tl_)   # live 'START & FFRAMESET 3T...' (Cyprus, Tuscany Epic): the frameset line
                m = re.match(r'^([A-Z][A-Z &/-]{2,30})\s*:\s*(\S.*)$', tl_) or re.match(r'^([A-Z][A-Z]{2,20})\s+(\S.*)$', tl_)   # the label runs to the colon
                if m and m.group(1).strip().isupper():   # 'START & FRAMESET: Guerciotti...' (Coast to Coast) -> Frameset (Matteo 16 Nov)
                    lab_ = 'Frameset' if 'FRAMESET' in m.group(1) else m.group(1).strip().capitalize()
                    dl.append((lab_, E(m.group(2).strip().lstrip(':').strip())))
                else: lede.append(ln)
        dlh = ''.join(f'<dt>{E(a)}</dt><dd>{b}</dd>' for a, b in dl)
        out.append(f'<section id="bike-rental"><div class="in"><div class="panel bike">'
                   f'{f"<div class=ph>{trim_tag(bimg, alt=f'Rental bike for the {text_of(h1).title()} tour')}</div>" if bimg else ""}'
                   f'<div class="tx">{H(bk, "Travel light")}<div class="lede">{"".join(f"<p>{x}</p>" for x in lede)}</div><dl>{dlh}</dl></div></div></div></section>')
        nav.append(('bike-rental', 'Bike rental'))
    gd = one('guides')
    if gd:
        lede = ''; ppl = []; started = False
        for k, v, s in gd['items']:
            if k == 'img': ppl.append({'img': v, 'texts': []}); started = True
            elif k == 'h3' and ppl: ppl[-1]['name'] = (k, v)
            elif k == 'h3': ppl.append({'img': None, 'texts': [], 'name': (k, v)})
            elif k == 'text' and ppl: ppl[-1]['texts'].append(v)
            elif k == 'text': lede += clean(v)
        cards = []
        for p in ppl:
            if 'name' not in p: continue
            nm = text_of(p['name'][1]); role = text_of(p['texts'][0]) if p['texts'] else ''
            sw = GUIDES_SWAP.get(slug, {}).get(nm.split()[0].upper()) if nm else None
            if sw:   # another guide on this tour: their card from the team (no bio)
                cards.append(team_card(sw)); continue
            if 'CIGALA' not in nm.upper():   # Matteo 16 Nov: guides by first name (or nickname), for their privacy; Matteo Cigala in full
                first = nm.split()[0]; nm = GUIDE_NICK.get(first.title(), first)
            bio = ''.join(clean(x) for x in p['texts'][1:])
            if nm.split()[0].upper() in STD_GUIDE:   # one standard card per person on every tour (Matteo 16 Nov: same height, no contradictions)
                role, bio = STD_GUIDE[nm.split()[0].upper()]; bio = f'<p>{E(bio)}</p>'
            ph = f'<div class="ph">{img_tag(p["img"], 600, alt=f"{nm.title()}, {role} at Cigala Cycling Tours")}</div>' if p['img'] else ''
            cards.append(f'<article class="panel guide">{ph}<div class="tx"><h3>{E(nm)}</h3><div class="role">{E(role)}</div>{bio}</div></article>')
        cards += [team_card(n) for n in GUIDES_ADD.get(slug, [])]
        if slug in GUIDES_SET: cards = [team_card(n) for n in GUIDES_SET[slug]]
        drop = {'MARINE'} | GUIDES_DROP.get(slug, set())   # Marine runs operations and bookings: on no tour (Matteo 16 Nov)
        cards = [c for c in cards if not any(f'<h3>{n}</h3>' in c for n in drop)]
        if any('class="role"' in c and not re.search(r'</div>\s*<p>|</div>(?:<p|<div class="prose")', c.split('class="role"')[1]) for c in cards): print('  !! guide without a bio on', slug)
        stats = []
        for st_ in S('stat'):
            lab = next((text_of(v) for k, v, s in st_['items'] if k == 'text'), '')
            num = {'500+': '700+', '10': '11'}.get(text_of(st_['h']).strip(), text_of(st_['h']).strip())   # same numbers as the homepage (Matteo 15 Nov)
            num_h = E(num).replace('★', '<i>★</i>')   # the star in gold, as on the homepage
            stats.append(f'<div class="stat"><div class="n">{num_h}</div><div class="l">{E(lab)}</div></div>')
        st_html = f'<div class="cc tstats"><div class="stats">{"".join(stats)}</div></div>' if stats else ''   # the homepage stats (Matteo 16 Nov)
        out.append(f'<section id="guides"><div class="in">{H(gd, "Who rides with you")}<div class="lede gl">{lede}</div>'
                   f'<div class="guides{" g3" if len(cards) == 3 else ""}">{"".join(cards)}</div>{st_html}</div></section>')
        nav.append(('guides', 'Guides'))
    fq = one('faq')
    qa = faqs(data)
    qa = [(q, a.replace('/terms-conditions/"', '/terms-conditions/#rider-eligibility"')) for q, a in qa]   # 'Expert' links straight to the rule
    for rx, q2, a2 in FAQ_EDIT.get(slug, []):   # per-tour corrections (Matteo 16 Nov: every FAQ must match its tour)
        qa = [((q2 or q), (a2 or a)) if re.search(rx, q) else (q, a) for q, a in qa]
    qa = [(q, re.sub(r'(?i)cooler than down at lake level', 'cooler than down in the valley', a) if slug in ('alpine-gravel-escape', 'italian-alps') else a) for q, a in qa]
    if slug in EXTRA_FAQ and not qa:
        qa = EXTRA_FAQ[slug]; fq = {'h': 'Frequently Asked Questions', 'tag': 'h2', 'items': []}
    if fq and qa:
        fh = ''.join(f'<details class="panel faq"><summary><h3>{E(q)}</h3></summary><div class="a">{a}</div></details>' for q, a in qa)
        out.append(f'<section id="faq"><div class="in">{H(fq, "Good to know")}<div class="faqs">{fh}</div></div></section>')
    rel = one('related')
    if rel: out.append(related_html(rel, h1))
    rv = one('reviews')
    if rv: out.append(reviews_block(text_of(rv['h'])))
    cu = one('custom')
    if cu:
        sub = next((v for k, v, s in cu['items'] if k == 'h3'), '')
        b = next((v for k, v, s in cu['items'] if k == 'btn'), ('More information', L + '/trips/private-trips/'))
        bg = next((v for k, v, s in cu['items'] if k == 'bg'), None) or 4440
        out.append(f'<section><div class="in"><div class="band">{img_tag(bg, 1600, alt="Riders on a Cigala Cycling custom tour")}<div class="tx">'
                   f'<div class="eyebrow">Custom tours</div><h2>{E(text_of(cu["h"]))}</h2><div class="bar"></div>'
                   f'{f"<h3 class=lede>{E(text_of(sub))}</h3>" if sub else ""}<div class="ctas"><a class="btn btn-go" href="{E(b[1])}">{E(b[0].capitalize())} →</a></div></div></div></div></section>')
    fin = one('final')
    fin_dates = next((text_of(v) for k, v, s in (fin['items'] if fin else []) if k in ('h3', 'h2', 'text')), dates_live)
    ftag = fin['tag'] if fin else None
    ftitle = f'<{ftag} class="fin-h">{E(text_of(fin["h"]))}</{ftag}>' if fin else f'<p class="band-title">{E(text_of(h1))}</p>'
    dtag = next((k for k, v, s in (fin['items'] if fin else []) if k in ('h3', 'h2')), None)
    fdates = f'<{dtag} class="fin-d">{E(fin_dates)}</{dtag}>' if dtag else f'<div class="fin-d">{E(fin_dates)}</div>'
    fspots = f'<div class="spots fspots av-{sp}"><span class="dot{live_}{av_cls}" aria-hidden="true"></span>{E(av_txt)}</div>'   # the same availability line under the dates (Matteo 16 Nov)
    out.append(f'<section><div class="in"><div class="panel final"><div class="eyebrow">Ready to ride?</div>{ftitle}{fdates}{fspots}'
               f'<div class="ctas"><a class="btn btn-go" href="{E(book)}" target="_blank" rel="noopener">Book now →</a>'
               f'<a class="btn btn-ghost" href="{L}/contact/">Ask a question</a></div></div></div></section>')
    tabs = ''.join(f'<a href="#{a}">{E(b)}</a>' for a, b in nav)
    out.insert(1, f'<nav class="tabs" aria-label="On this page"><div class="in">{tabs}<a class="btn btn-go tbook" href="{E(book)}" target="_blank" rel="noopener">Book now</a></div></nav>')
    out.append("""<script>(function(){var m=document.querySelector('.cl .dmap'),l=document.querySelector('.cl .dleg');if(!m||!l)return;var cur=null;
function set(d){cur=d;m.classList.toggle('hl',!!d);m.querySelectorAll('.dr,.db').forEach(function(g){g.classList.toggle('on',g.dataset.d===d);});
l.querySelectorAll('button').forEach(function(b){b.classList.toggle('on',b.dataset.d===d);b.setAttribute('aria-pressed',b.dataset.d===d);});}
l.querySelectorAll('button').forEach(function(b){b.addEventListener('mouseenter',function(){set(b.dataset.d);});b.addEventListener('focus',function(){set(b.dataset.d);});
b.addEventListener('click',function(){set(cur===b.dataset.d?null:b.dataset.d);});});l.addEventListener('mouseleave',function(){set(null);});})();</script>""")   # day highlight on the route map
    if slug in DYN: out.append(DYN_JS)
    out.append(exit_pop(f'Any questions about {re.sub(r"\s*\|\s*Gravel$", "", tr["name"])}?', 'Dates, fitness, bikes, rooms or the route: ask Matteo and the team, we are happy to help before you book.', ('Send us a message', f'{L}/contact/')))   # exit pop-up (Matteo 16 Nov)
    # one Book now on screen at a time (Matteo 16 Nov): the bar's button shows once the price box has scrolled away
    out.append("""<script>(function(){var b=document.querySelector('.cl .thero .book'),t=document.querySelector('.cl .tabs');if(!b||!t||!('IntersectionObserver' in window))return;t.classList.add('nobook');
new IntersectionObserver(function(es){t.classList.toggle('nobook',es[0].isIntersecting);}).observe(b);})();</script>""")
    out.append("""<script>(function(){var f=document.querySelector('.cl .facts .fphoto');if(!f)return;   /* the photo only when it has room (Matteo 16 Nov) */
function c(){f.hidden=false;f.style.display='';if(window.innerWidth>900&&f.getBoundingClientRect().height<260)f.style.display='none';}
addEventListener('load',c);addEventListener('resize',c);c();})();</script>""")
    # laptops: the section menu stays under the header for the whole page (sticky alone let go at the end of its block); phones: not sticky (Matteo 16 Nov)
    out.append("""<script>(function(){var t=document.querySelector('.cl .tabs');if(!t)return;var ph=document.createElement('div');t.parentNode.insertBefore(ph,t);
function f(){var pin=window.innerWidth>900&&ph.getBoundingClientRect().top<=79;if(pin!==t.classList.contains('pinned')){t.classList.toggle('pinned',pin);ph.style.height=pin?t.offsetHeight+'px':'';}}
addEventListener('scroll',f,{passive:true});addEventListener('resize',f);f();})();</script>""")
    # structured data (SEO, Matteo: only improve): TouristTrip with the route places and the euro price, linked to the site's Organization
    num = re.sub(r'[^\d.]', '', pr.replace(',', ''))
    places = [n for n, la, lo, k, ps in _trm.ROUTES.get(slug, {}).get('pts', [])]
    intro_txt = text_of(''.join(clean(v) for k, v, s in (intro['items'] if intro else []) if k == 'text'))[:300]
    ld = {"@context": "https://schema.org", "@type": "TouristTrip", "name": tr['name'], "url": f"{L}/trips/{slug}/",
          "description": intro_txt or f"Guided {TYPE[tr['type']].lower()} cycling tour in {tr['country']} with Cigala Cycling Tours.",
          "touristType": "Cyclists", "provider": {"@id": f"{L}/#organization"}}
    if card: ld["image"] = card['url']
    if places: ld["itinerary"] = {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i, "item": {"@type": "Place", "name": n}} for i, n in enumerate(places, 1)]}
    if num: ld["offers"] = {"@type": "Offer", "price": num, "priceCurrency": "EUR", "url": book, "availability": "https://schema.org/InStock"}
    out.append('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('</', '<\\/') + '</script>')
    out.append(YT_JS if 'class="yt"' in ''.join(out) else '')
    out.append("""<script>(function(){var l=document.querySelectorAll('.cl .stats .stat .n');if(!('IntersectionObserver' in window)||matchMedia('(prefers-reduced-motion: reduce)').matches)return;
l.forEach(function(el){if(el.children.length)return;var m=el.textContent.match(/^([\\d,]+)(\\D*)$/);if(!m)return;var to=+m[1].replace(/,/g,''),suf=m[2],fmt=function(v){return v.toLocaleString('en-US')+suf;};el.style.minWidth=el.offsetWidth+'px';el.textContent=fmt(0);
new IntersectionObserver(function(es,ob){if(!es[0].isIntersecting)return;ob.disconnect();var t0=performance.now();(function f(t){var k=Math.min(1,(t-t0)/1500);el.textContent=fmt(Math.round(to*(1-Math.pow(1-k,3))));if(k<1)requestAnimationFrame(f);})(t0);},{threshold:.5}).observe(el);});})();</script>""")
    main = '\n'.join(x for x in out if x)
    main = main.replace('href="https://staging.tours.cigalacycling.com', 'href="' + L)   # links only; images stay on staging
    return {'id': pid, 'slug': 'trip-' + slug, 'main': main, 'css': PAGE_CSS + TRIP_CSS, 'crumb': tr['name']}

TRIP_CSS = '''
html .cl .thero .in { display: grid; grid-template-columns: minmax(0, 1fr) 360px; gap: 32px; align-items: end; }
@media (max-width: 900px) { html .cl .thero .in { grid-template-columns: minmax(0, 1fr); } }
html .cl .tag.gdot::before { content: ""; display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--gravel); margin-right: 7px; vertical-align: 1px; }
html .cl .book .price small { display: block; margin-top: 8px; }
html .cl .book .spots { display: flex; align-items: center; gap: 2px; margin: 12px 0 4px; font-size: 13.5px; font-weight: 700; color: #fff; }
html .cl .book p.note a { color: var(--green-text); text-decoration: underline; text-underline-offset: 3px; }
html .cl .route .map { background: none !important; border: 0 !important; padding: 0 !important; aspect-ratio: auto !important; }
html .cl .dtour .desc { display: -webkit-box; -webkit-line-clamp: 5; -webkit-box-orient: vertical; overflow: hidden; }
html .cl .route .map svg { display: block; width: 100%; height: auto; border-radius: 12px; border: 1px solid var(--border); }
html .cl .route .map .mapnote { margin: 10px 0 0; font-size: 13px; color: var(--text-3); }
html .cl .route .map img { object-fit: contain !important; height: auto !important; aspect-ratio: auto !important; }
html .cl #overview .cardimg img { aspect-ratio: auto !important; height: auto !important; object-fit: contain !important; }
html .cl #overview .cardimg { aspect-ratio: auto !important; height: auto; align-self: start; }   /* the box takes the poster's own shape: no empty band under square posters */
html .cl .hnote { font-family: var(--body); font-size: 15px; font-weight: 600; letter-spacing: .02em; text-transform: none; color: var(--green-text); margin: 4px 0 16px; }
html .cl .thero .book { min-width: 0; grid-template-columns: minmax(0, 1fr); }
html .cl .thero .book > * { max-width: 100%; }
html .cl .thero .book ul { min-width: 0; width: 100%; }
html .cl .thero .book li { display: grid !important; grid-template-columns: auto minmax(0, 1fr); gap: 14px; white-space: normal; min-width: 0; }
html .cl .thero .book li span { white-space: normal !important; min-width: 0; }
html .cl .thero .book li span:last-child { text-align: right; overflow-wrap: anywhere; }
html .cl .thero .book p.note { display: block; margin: 8px 0 0; }
html .cl .sh { }
html .cl h3.sh { font-size: clamp(30px, 4.4vw, 48px); }
html .cl .facts .facts-h { grid-column: 1 / -1; font-size: 13px; font-family: var(--body); font-weight: 600; letter-spacing: .1em; color: var(--text-3); margin: 0 0 6px; }
html .cl .days { list-style: none; margin: 0; padding: 0; }
html .cl .day .prose p { margin: 0 0 10px; }
html .cl .xbox, html .cl .opbox { padding: clamp(20px, 3vw, 32px); }
html .cl .opbox { display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-wrap: wrap; }
html .cl .opbox .head { margin: 0; }
html .cl .opbox .optext { flex: 1 1 320px; min-width: 0; }
html .cl .opbox .opnote { margin: 14px 0 0; max-width: 62ch; font-size: 15px; line-height: 1.55; }
html .cl .opbox .opnote a { color: var(--green-text, #2bd47a); text-decoration: underline; text-underline-offset: 3px; font-weight: 600; }
html .cl .opbox .oplogo { width: 120px; height: auto; background: #fff; border-radius: 10px; padding: 10px; }
html .cl .hotel h3, html .cl .hotel h2 { font-size: 22px; }
html .cl .stars .sup { font-size: 11px; letter-spacing: 0; vertical-align: 2px; margin-left: 4px; }
html .cl .guide .tx p { margin: 8px 0 0; font-size: 14px; color: var(--text-2); }
html .cl .gl p { margin: 0 0 16px; }
html .cl .final { text-align: center; padding: clamp(28px, 5vw, 56px) 20px; }
html .cl .final .fin-h { font-size: clamp(34px, 5vw, 60px); }
html .cl .final .fin-d { font-family: var(--body); font-size: 16px; font-weight: 600; letter-spacing: .06em; color: var(--text-2); margin: 10px 0 20px; text-transform: uppercase; }
html .cl .final .ctas { justify-content: center; }
html .cl h2.ey2 { font-family: var(--body); font-size: 12px; line-height: 1.4; font-weight: 600; letter-spacing: .14em; color: #ff3d33; margin: 0 0 10px; }
html .cl .dtour .by { font-size: 11px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: #ff3d33; }
html .cl .dtour h3 { font-size: 22px; line-height: 1.14; }
/* ---- Matteo 16 Nov: second review ---- */
html .cl .thero .dates { color: var(--green-text, #2bd47a); }
html .cl .thero .book.bk2 { padding: 0; gap: 0; background: rgba(12,14,16,.95); border: 1px solid rgba(255,255,255,.16); border-radius: 16px; overflow: hidden; box-shadow: 0 24px 60px rgba(0,0,0,.5); }
html .cl .bk2 .bk-top { padding: 22px 24px 18px; display: grid; gap: 10px; justify-items: start; }
html .cl .bk2 .bk-top .price { margin: 0; }
html .cl .bk2 ul { padding: 0 24px; gap: 0; border-top: 1px solid var(--border-strong); }
html .cl .bk2 ul:empty { display: none; }
html .cl .thero .bk2 ul li { border-top: 0; border-bottom: 1px solid var(--border); padding: 12px 0; }
html .cl .thero .bk2 ul li:last-child { border-bottom: 0; }
html .cl .bk2 .bk-cta { padding: 18px 24px 22px; border-top: 1px solid var(--border-strong); }
html .cl .bk2 .bk-cta .btn { width: 100%; justify-content: center; }
html .cl .bk2 .bk-notes { padding: 14px 24px 18px; border-top: 1px solid var(--border); background: rgba(255,255,255,.025); }
html .cl .thero .bk2 .bk-notes p.note:first-child { margin-top: 0; }
html .cl .glance.g4 > div { display: flex; gap: 14px; align-items: center; }
html .cl .glance .gi { flex: none; width: 42px; height: 42px; border-radius: 50%; display: grid; place-items: center; color: var(--green-text, #2bd47a); background: rgba(0,154,68,.12); border: 1px solid rgba(43,212,122,.28); }
html .cl .glance .n.sm { font-size: 15px; }
html .cl .glance.g4 > div > div { min-width: 0; }
html .cl .glance.g4 .n { white-space: normal; overflow-wrap: break-word; }
@media (max-width: 600px) { html .cl .glance.g4 > div { flex-direction: column; align-items: flex-start; gap: 10px; padding: 16px; } html .cl .glance .gi { width: 34px; height: 34px; } html .cl .glance .gi svg { width: 17px; height: 17px; } html .cl .glance.g4 .n:not(.sm) { font-size: 26px; } }
html .cl .lm { display: inline-flex; align-items: flex-end; gap: 2px; margin-right: 8px; vertical-align: 0; }
html .cl .lm i { display: block; width: 3px; border-radius: 1px; background: rgba(255,255,255,.22); }
html .cl .lm i:nth-child(1) { height: 5px; } html .cl .lm i:nth-child(2) { height: 8px; } html .cl .lm i:nth-child(3) { height: 11px; }
html .cl .lm i.on { background: var(--green-text, #2bd47a); }
html .cl .facts .facts-h { font-family: var(--head); font-weight: 400; font-size: 28px; line-height: 1.05; letter-spacing: .01em; color: var(--green-text, #2bd47a); margin: 0 0 10px; }
html .cl .facts div { grid-template-columns: 32px 128px minmax(0, 1fr); align-items: center; gap: 12px; }   /* icon centred on its title (Matteo 16 Nov) */
html .cl .facts div.ftrans { align-items: start; }
@media (min-width: 901px) { html .cl dl.facts { display: flex !important; flex-direction: column; } html .cl .facts .fphoto { flex: 1 1 0; min-height: 0; margin: 18px 0 0; border-radius: 12px; overflow: hidden; } html .cl .facts .fphoto img { width: 100%; height: 100%; object-fit: cover; display: block; } }
@media (max-width: 900px) { html .cl .facts .fphoto { display: none; } }
html .cl .evopts { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: 10px 0 4px; }
html .cl .evopts > span:first-child { font-size: 13px; color: var(--text-3); margin-right: 2px; }
html .cl .evopts .evo { display: inline-flex; gap: 6px; align-items: baseline; padding: 5px 12px; border-radius: 999px; border: 1px solid rgba(43,212,122,.35); background: rgba(0,154,68,.10); font-size: 14px; }
html .cl .evopts .evo b { color: var(--green-text, #2bd47a); font-weight: 600; }
html .cl .facts .fi { width: 30px; height: 30px; border-radius: 50%; display: grid; place-items: center; color: var(--green-text, #2bd47a); background: rgba(0,154,68,.12); }
html .cl .facts .fi svg { width: 16px; height: 16px; }
html .cl .facts dt, html .cl .facts dd { padding-top: 0; }
html .cl .facts div.ftrans dt { padding-top: 7px; } html .cl .facts div.ftrans dd { padding-top: 5px; }
html .cl .facts .tl { display: block; margin-bottom: 4px; font-weight: 500; }
html .cl .facts .tl b { color: var(--green-text, #2bd47a); font-weight: 600; }
@media (max-width: 600px) { html .cl .facts div, html .cl .facts div.ftrans { grid-template-columns: 32px minmax(0, 1fr); align-items: center; row-gap: 4px; }
  html .cl .facts dt, html .cl .facts div.ftrans dt { padding-top: 0; } html .cl .facts dd, html .cl .facts div.ftrans dd { grid-column: 2; padding-top: 0; } }   /* phones: icon beside the title, the value under the title */
html .cl #itinerary .gpx { margin: 8px 0 30px; }
html .cl .gallery.g5, html .cl .gallery.g9 { grid-template-columns: repeat(4, minmax(0, 1fr)); grid-auto-flow: dense; }
html .cl .gallery .g-big { grid-column: span 2; grid-row: span 2; }
html .cl .gallery.g1 { grid-template-columns: minmax(0, 1fr); } html .cl .gallery.g2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
html .cl .gallery.g3 { grid-template-columns: repeat(3, minmax(0, 1fr)); } html .cl .gallery.g4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
@media (max-width: 700px) { html .cl .gallery.g5, html .cl .gallery.g9, html .cl .gallery.g4 { grid-template-columns: repeat(2, minmax(0, 1fr)); } html .cl .gallery.g3 { grid-template-columns: repeat(3, minmax(0, 1fr)); grid-auto-rows: 120px; } }
html .cl .hotel1, html .cl .hotels .hotel.wide { display: grid; grid-template-columns: minmax(0, 6fr) minmax(0, 5fr); overflow: hidden; }
html .cl .hotels .hotel.wide { grid-column: 1 / -1; }
html .cl .hotel1 .ph, html .cl .hotel.wide .ph { aspect-ratio: auto !important; height: 100%; min-height: 360px; }
html .cl .hotel1 .ph img, html .cl .hotel.wide .ph img { height: 100% !important; aspect-ratio: auto !important; }
html .cl .hotel1 .tx { padding: clamp(22px, 3vw, 36px); align-content: center; gap: 10px; }
html .cl .hotel .eyebrow { margin: 0; }
html .cl .hotel1 .prose p { font-size: 15px; line-height: 1.6; color: var(--text-2); margin: 6px 0 0; }
html .cl .hotel1 .hnote { margin: 12px 0 0; }
@media (max-width: 900px) { html .cl .hotel1, html .cl .hotels .hotel.wide { grid-template-columns: minmax(0, 1fr); } html .cl .hotel1 .ph, html .cl .hotel.wide .ph { min-height: 0; aspect-ratio: 16 / 10 !important; } }
html .cl .strip.s4 { grid-template-columns: repeat(4, minmax(0, 1fr)); margin-top: 14px; }
html .cl .strip.s3 { grid-template-columns: repeat(3, minmax(0, 1fr)); margin-top: 14px; }
@media (max-width: 640px) { html .cl .strip.s4 { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
html .cl .dprose + .hotels { margin-top: 18px; }
html .cl .guides.g3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
html .cl .guides.g3 .guide { grid-template-columns: minmax(0, 1fr); }
html .cl .guides.g3 .guide .ph img { aspect-ratio: 4 / 3; min-height: 0; height: auto; }
@media (max-width: 900px) { html .cl .guides.g3 { grid-template-columns: minmax(0, 1fr); } html .cl .guides.g3 .guide { grid-template-columns: 140px minmax(0, 1fr); } html .cl .guides.g3 .guide .ph img { aspect-ratio: auto; height: 100%; } }
html .cl .cc.tstats { margin-top: 32px; }
html .cl .tabs .tbook { transition: opacity .25s, visibility .25s; }
html .cl .tabs.pinned { position: fixed !important; left: 0; right: 0; top: calc(env(safe-area-inset-top, 0px) + 79px); }
@media (max-width: 900px) { html .cl .tabs { position: relative !important; top: auto !important; } }
html .cl .tabs.nobook .tbook { opacity: 0; visibility: hidden; }
html .cl .final .fspots { justify-content: center; margin: -6px 0 20px; }
html .cl .day .evopts { margin: 0 0 12px; font-size: 14px; color: var(--text-2); line-height: 1.4; }
html .cl .day .evopts > span:first-child { color: var(--text-3); font-size: 12px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; margin-right: 4px; }
html .cl .day .evopts b { color: var(--green-text, #2bd47a); font-weight: 700; }
html .cl .day .num { position: relative; z-index: 1; }   /* the timeline line runs behind the day circle, not into it (Matteo 16 Nov) */
/* ---- dynamic trip page (pilot: Algarve), only when JS runs and motion is welcome ---- */
html .cl .cardimg.pdyn { position: relative; overflow: hidden; }
html .cl .pdyn .pbadge { position: absolute; left: 65.5%; width: 30.9%; top: 0; margin-top: 3.6%; aspect-ratio: 309 / 320; display: grid; place-items: center; pointer-events: none; }
html .cl .pdyn .pbadge svg { width: 86%; height: auto; overflow: visible; }
html.dyn-ok .cl .pdyn .bo { stroke-dasharray: 1; stroke-dashoffset: 1; }
html.dyn-ok .cl .pdyn .bf, html.dyn-ok .cl .pdyn .br, html.dyn-ok .cl .pdyn .bh { opacity: 0; }
html.dyn-ok .cl .pdyn.go .bo { transition: stroke-dashoffset 1.8s ease; stroke-dashoffset: 0; }
html.dyn-ok .cl .pdyn.go .bf, html.dyn-ok .cl .pdyn.go .br { transition: opacity .8s ease 1.2s; opacity: 1; }
html.dyn-ok .cl .pdyn.go .bh { transition: opacity .6s ease 1.8s; opacity: .85; animation: bh-glow 2.6s ease-in-out 2.6s infinite; }
@keyframes bh-glow { 0%, 100% { fill-opacity: .85; } 50% { fill-opacity: .45; } }
html.dyn-ok .cl .dmap.anim .dr use { stroke-dasharray: 1; stroke-dashoffset: 1; }
html.dyn-ok .cl .dmap.anim .db { opacity: 0; transform-box: fill-box; transform-origin: center; transform: scale(.4); }
html.dyn-ok .cl .dmap.anim.go .dr use { transition: stroke-dashoffset 1.4s ease-in-out; transition-delay: calc((var(--i) - 1) * .55s); stroke-dashoffset: 0; }
html.dyn-ok .cl .dmap.anim.go .db { transition: opacity .35s ease, transform .35s ease; transition-delay: calc((var(--i) - 1) * .55s + 1.1s); opacity: 1; transform: none; }
html.dyn-ok .cl .days .day.dyn-in { opacity: 0; transform: translateY(18px); }
html.dyn-ok .cl .days .day.dyn-in::before { transform: scaleY(0); transform-origin: top; }
html.dyn-ok .cl .days .day.dyn-in.go { opacity: 1; transform: none; transition: opacity .6s ease, transform .6s ease; }
html.dyn-ok .cl .days .day.dyn-in.go::before { transform: scaleY(1); transition: transform .9s ease .3s; }
@media (prefers-reduced-motion: reduce) { html .cl .pdyn .bh { animation: none; } }
html .cl #guides .gl { margin: 4px 0 26px; }   /* more room between the intro line and the guide cards (Matteo 16 Nov) */
html .cl #guides .guide .tx { padding: 22px 22px 24px; }
html .cl #guides .guide .role { margin: 8px 0 12px; }
html .cl #guides .guide .tx { align-self: start; align-content: start; }   /* cards without a bio: name and role at the top, like the others */
html .cl .bk2 .bk-top { gap: 8px; }
html .cl .bk2 .bk-top .price { margin-bottom: 4px; }
html .cl .bk2 .bk-top .price small { padding-left: 0; margin-left: 0; }
html .cl .thero .bk2 .early, html .cl .thero .bk2 .spots { display: inline-flex; align-items: center; gap: 8px; margin: 0; padding: 5px 10px; border-radius: 6px; font-size: 12.5px; font-weight: 600; line-height: 1.3; color: var(--text); border: 1px solid; }   /* early bird and availability: the same pill, the same left edge (Matteo 16 Nov) */
html .cl .thero .bk2 .early { background: rgba(225,6,0,.12); border-color: rgba(225,6,0,.45); }
html .cl .thero .bk2 .early::before { margin: 0; }
html .cl .bk2 .spots .dot { margin-right: 0; }
html .cl .bk2 .spots.av-low { background: rgba(225,6,0,.12); border-color: rgba(225,6,0,.45); }
html .cl .bk2 .spots.av-mid { background: rgba(240,191,0,.1); border-color: rgba(240,191,0,.45); }
html .cl .bk2 .spots.av-high { background: rgba(0,154,68,.12); border-color: rgba(43,212,122,.4); }
html .cl #included .yes .inh { color: var(--green-text, #2bd47a); }   /* Included in green, Not included stays white (Matteo 16 Nov) */
html .cl .thero ~ section { padding-top: 48px; }   /* a little less space between sections on the trip pages (Matteo 16 Nov) */
html .cl .thero ~ section#route, html .cl .thero ~ section#itinerary { padding-top: 40px; }
html .cl .xsplit { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 6fr); gap: 0; padding: 0; overflow: hidden; align-items: stretch; }
html .cl .xsplit .xph { background: #d5dcdc; display: grid; place-items: center; padding: 18px; }   /* the jersey photo's own grey all round (Matteo 16 Nov) */
html .cl .faq .a a { color: var(--green-text, #2bd47a); font-weight: 700; text-decoration: underline; text-underline-offset: 3px; }   /* links in answers (cycling coaching) in green */
html .cl .xsplit .xph img { width: 100%; height: auto; max-height: 420px; object-fit: contain; }
html .cl .xsplit .xtx { padding: clamp(22px, 3vw, 36px); align-self: center; }
html .cl .xsplit.xcover .xph { padding: 0; background: none; } html .cl .xsplit.xcover .xph img { height: 100%; max-height: none; min-height: 300px; object-fit: cover; }   /* a photo fills its half; the grey ground is for product shots (the jersey) */
html .cl .xbox .prose a { color: var(--green-text, #2bd47a); font-weight: 700; text-decoration: underline; text-underline-offset: 3px; }
@media (max-width: 800px) { html .cl .xsplit { grid-template-columns: minmax(0, 1fr); } }
html .cl .bike .ph { padding: 12px 18px; }
html .cl .bike .ph img { width: 100%; max-height: 380px; height: auto; object-fit: contain; }
html .cl .tcard2 .tts { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-top: 8px; font-size: 12px; color: var(--text-3); }
html .cl .tcard2 .tt { display: inline-block; font-family: var(--head); font-size: 16px; letter-spacing: .03em; color: #fff; background: rgba(0,154,68,.18); border: 1px solid rgba(43,212,122,.35); border-radius: 6px; padding: 2px 8px; }
html .cl .hotels.hcards { align-items: start; }   /* each hotel card as tall as its own text */
html .cl .hcards .hx { display: flex; flex-direction: column; }
html .cl .hcards .hx .tx { gap: 8px; }
html .cl .hcards .hx .prose p { font-size: 14.5px; line-height: 1.6; color: var(--text-2); margin: 4px 0 0; }
html .cl .hthumbs { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin-top: 12px; }
html .cl .hthumbs.n2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
html .cl .hthumbs img { width: 100%; aspect-ratio: 4 / 3; object-fit: cover; border-radius: 8px; border: 1px solid var(--border); }
html .cl .tvid { max-width: none; width: 100%; }   /* the video uses the full content width, like the other sections (Matteo 16 Nov) */
html .cl .tvid .play { width: 84px; height: 84px; margin: -42px 0 0 -42px; }
html .cl .tvid .play::after { left: 34px; top: 26px; border-width: 16px 0 16px 25px; }
html .cl .hvid { margin-top: 18px; display: inline-flex; align-items: center; gap: 10px; }
html .cl .hvid .pl { width: 22px; height: 22px; border-radius: 50%; background: #009a44; position: relative; flex: none; }
html .cl .hvid .pl::after { content: ""; position: absolute; left: 8px; top: 6px; border-style: solid; border-width: 5px 0 5px 8px; border-color: transparent transparent transparent #fff; }
@media (min-width: 901px) { html .cl .hero.thero > img { object-position: var(--dpos, center 40%); } }
@media (min-width: 901px) { html .cl .hero.thero.tall .in { padding-top: 172px !important; } }
@media (max-width: 900px) { html .cl .hero.thero.tall > img { height: 516px; } html .cl .hero.thero.tall::after { height: 518px; } html .cl .hero.thero.tall .in { padding-top: 376px !important; } }
/* phones: the hero photo as a clear band at the top, the title and the price box under it (Matteo 16 Nov: the rider and the jersey logo were hidden) */
@media (max-width: 900px) {
  html .cl .hero.thero > img { inset: 0 0 auto 0; height: 440px; object-position: var(--mpos, 50% 30%); }
  html .cl .hero.thero::after { inset: 0 0 auto 0; height: 442px; background: linear-gradient(180deg, rgba(8,9,10,.45) 0%, rgba(8,9,10,.05) 22%, rgba(8,9,10,.1) 55%, rgba(8,9,10,1) 100%); }
  html .cl .hero.thero .in { padding-top: 300px !important; }
  html .cl .hero.thero .crumbs { position: absolute; top: 94px; left: 16px; max-width: calc(100% - 32px); width: fit-content; box-sizing: border-box; background: rgba(8,9,10,.62); backdrop-filter: blur(6px); border-radius: 999px; padding: 5px 12px; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }   /* readable over the photo */
}
html .cl .thero .tag.tflag { padding: 3px; background: rgba(8,9,10,.6); }
html .cl .thero .tag.tflag img { display: block; width: 22px; height: 22px; border-radius: 50%; object-fit: cover; box-shadow: 0 0 0 1px rgba(255,255,255,.35); }
html .cl .thero .tag.tlvl .lm { margin-right: 7px; }
html .cl .dleg { list-style: none; margin: 12px 0 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 6px; }
html .cl .dleg button { width: 100%; display: flex; align-items: center; gap: 10px; text-align: left; background: rgba(255,255,255,.03); border: 1px solid var(--border); border-radius: 10px; padding: 8px 12px; color: var(--text-2); font: 600 13px/1.3 var(--body); cursor: pointer; transition: border-color .2s, background .2s; }
html .cl .dleg button:hover, html .cl .dleg button.on { border-color: rgba(255,255,255,.3); background: rgba(255,255,255,.06); color: #fff; }
html .cl .dleg .sw { flex: none; width: 24px; height: 24px; border-radius: 50%; display: grid; place-items: center; color: #0a0c0e; font: 800 12px/1 var(--body); }
html .cl .dleg .dt { flex: 1; min-width: 0; white-space: normal; overflow-wrap: break-word; text-transform: uppercase; font-size: 11.5px; letter-spacing: .05em; }
html .cl .dleg button { white-space: normal; height: 100%; }   /* every box fills its row: no gap under a short one (Matteo 16 Nov) */
html .cl .dleg li { display: flex; }
html .cl .dleg .dk { flex: none; color: var(--text-3); font-weight: 600; font-size: 12px; }
html .cl .dmap .dr, html .cl .dmap .db { transition: opacity .2s; }
html .cl .dmap.hl .dr:not(.on), html .cl .dmap.hl .db:not(.on) { opacity: .12; }
html .cl .dmap.hl .dr.on .ln { stroke-width: 4.5; }
html .cl .inc2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; align-items: start; }
html .cl .inc2 .panel, html .cl .tband { padding: 24px 26px; }
html .cl #included .inh { font-family: var(--head); font-weight: 400; font-size: 22px; line-height: 1.1; text-transform: uppercase; letter-spacing: .01em; color: var(--text); margin: 0 0 16px; }
html .cl #included ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
html .cl #included li { display: grid; grid-template-columns: 22px minmax(0, 1fr); gap: 10px; font-size: 14.5px; }
html .cl #included .yes li::before, html .cl #included .no li::before { content: ""; width: 20px; height: 20px; border-radius: 50%; margin-top: 2px; }
html .cl #included .yes li::before { background: rgba(0,154,68,.18) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'%3E%3Cpath d='M5.5 10.5l3 3 6-7' fill='none' stroke='%232bd47a' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center / 20px no-repeat; }
html .cl #included .no li::before { background: rgba(255,255,255,.04) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'%3E%3Cpath d='M7 7l6 6M13 7l-6 6' fill='none' stroke='%238a8f98' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E") center / 20px no-repeat; }
html .cl .tband { margin-top: 16px; }
html .cl .trow { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; }
html .cl .tcard2 { display: flex; gap: 12px; align-items: flex-start; background: rgba(255,255,255,.03); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; }
html .cl .tcard2 .ic { flex: none; width: 34px; height: 34px; border-radius: 50%; display: grid; place-items: center; color: var(--green-text, #2bd47a); background: rgba(0,154,68,.12); }
html .cl .tcard2 .ic svg { width: 17px; height: 17px; }
html .cl .tcard2 b { display: block; font-family: var(--head); font-weight: 400; font-size: 19px; color: var(--green-text, #2bd47a); letter-spacing: .02em; }
html .cl .tcard2 span { font-size: 14px; color: var(--text-2); line-height: 1.45; }
html .cl .tnote { margin: 12px 0 0; font-size: 13.5px; color: var(--text-3); }
html .cl .prow { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
html .cl .ptile { background: rgba(255,255,255,.03); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; display: grid; gap: 2px; }
html .cl .ptile span { font-size: 11.5px; font-weight: 600; letter-spacing: .09em; text-transform: uppercase; color: var(--text-3); }
html .cl .ptile b { font-family: var(--head); font-weight: 400; font-size: 28px; color: #fff; }
html .cl .ptile small { font-size: 12.5px; color: var(--text-3); }
html .cl .ptile { transition: border-color .25s, background .25s, transform .25s; }
html .cl .ptile b { transition: color .25s; }
html .cl .prow .ptile:hover { transform: translateY(-2px); }   /* the grids in medal colours on hover (Matteo 16 Nov) */
html .cl .prow .ptile:nth-child(1):hover { border-color: #d4af37; background: rgba(212,175,55,.12); } html .cl .prow .ptile:nth-child(1):hover b, html .cl .prow .ptile:nth-child(1):hover span { color: #e6c55a; }
html .cl .prow .ptile:nth-child(2):hover { border-color: #c4cad0; background: rgba(196,202,208,.12); } html .cl .prow .ptile:nth-child(2):hover b, html .cl .prow .ptile:nth-child(2):hover span { color: #dfe4e8; }
html .cl .prow .ptile:nth-child(3):hover { border-color: #cd7f32; background: rgba(205,127,50,.13); } html .cl .prow .ptile:nth-child(3):hover b, html .cl .prow .ptile:nth-child(3):hover span { color: #e0965a; }
html .cl .prow .ptile:nth-child(4):hover { border-color: #2bd47a; background: rgba(0,154,68,.13); } html .cl .prow .ptile:nth-child(4):hover b, html .cl .prow .ptile:nth-child(4):hover span { color: #2bd47a; }
html .cl .thero .dn { display: flex; flex-wrap: wrap; gap: 8px 18px; margin-top: 10px; font-size: 15px; font-weight: 600; color: var(--text, #f7f8f8); letter-spacing: .02em; }
html .cl .thero .dn span { display: inline-flex; align-items: center; gap: 7px; }
@media (max-width: 600px) { html .cl .thero .dn { display: grid; grid-template-columns: auto auto; justify-content: start; column-gap: 26px; } }   /* phones: two neat rows */
html .cl .thero .dn svg { width: 17px; height: 17px; color: var(--green-text, #2bd47a); }
@media (max-width: 800px) { html .cl .inc2 { grid-template-columns: minmax(0, 1fr); } }
html .cl .inc .sidet { font-family: var(--head); font-weight: 400; font-size: 20px; line-height: 1.1; text-transform: uppercase; letter-spacing: .01em; color: var(--text); margin: 0 0 14px; }
html .cl .inc .entryp li::before { width: 7px; height: 7px; margin: 8px 0 0 7px; background: var(--green-text, #2bd47a); }   /* prices, not included items: a plain dot */
html .cl .band h3.lede { font-family: var(--body); font-weight: 400; text-transform: none; letter-spacing: 0; font-size: 17px; line-height: 1.5; color: var(--text-2); }
'''

# the shared status dot (shared/dot/dot.css), scoped to the spots line (the trip tags also use a .dot class)
TRIP_CSS += re.sub(r'(?m)^\.dot', 'html .cl .spots .dot', re.sub(r'/\*.*?\*/', '', open(ROOT + 'shared/dot/dot.css').read(), flags=re.S)).replace('{ .dot.live', '{ html .cl .spots .dot.live')

if __name__ == '__main__':
    prev_shell = open(ROOT + 'tourspages/trips.html').read()
    for slug in sys.argv[1:] or IDS:
        d = trip(slug)
        d['main'] = fix_text(d['main'])
        a, b = prev_shell.index('<div class="cl cl-page">'), prev_shell.index('<div class="cc"><footer>')
        prev = prev_shell[:a] + '<div class="cl cl-page">\n' + d['main'] + '\n</div>\n' + prev_shell[b:]
        prev = prev.replace('</style>', '</style>\n<style>\n' + d['css'] + '\n</style>', 1)
        open(ROOT + f'tourspages/page-trip-{slug}.html', 'w').write(prev)
        json.dump(d, open(ROOT + f'stg-tours/out/list-trip-{slug}.json', 'w'), ensure_ascii=False)
        m = d['main']
        print(slug, len(m), 'chars | h1', m.count('<h1'), '| h2', m.count('<h2'), '| h3', m.count('<h3'), '| days', m.count('class="day"'), '| img', m.count('<img'))

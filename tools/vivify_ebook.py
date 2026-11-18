"""Build Marine's e-book "Breakfasts to Ignite Your Potential" in the Vivify website style.

  python3 tools/vivify_ebook.py        -> vivify/ebook/ebook.html and vivify/ebook/Breakfasts-to-Ignite-Your-Potential.pdf

- Text and macros come from Marine's PDF (vivify/ebook/source-text.txt -> recipes.json), unchanged.
- Photos: Marine's own photos (vivify/ebook/img/*.jpg) are kept; recipes that had a placeholder use
  CC0 / public-domain photos (img/new-*.jpg, sources in photo-credits.json).
- Savoury toasts moved to the savoury chapter; feta oats removed; chia tips = lactose-free swap (Marine's review).
- Quinoa bowl moved into chapter 3 "Porridge & warm grains" with the oat and rice porridges.
- One recipe per page, so there are no half-empty pages.
"""
import os, json, html, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
E = ROOT + 'vivify/ebook/'
R = json.load(open(E + 'recipes.json'))
e = html.escape

# --- Marine's edits (review of the first draft)
R = [r for r in R if r['title'] != 'Savoury Spinach & Feta Oats']          # recipe removed
LACTOSE = 'VIVIFY TIP For a lactose-free version, replace the Greek yogurt with coconut yogurt.'
for r in R:
    if r['cat'] == 'CHIA SEED PUDDINGS':
        r['notes'] = [LACTOSE] + [x for x in r['notes'] if not x.startswith('VIVIFY TIP')]
    r['notes'] = [x for x in r['notes'] if 'thick yogurt' not in x]          # no "use a thick yogurt" advice
    r['ing'] = [x.replace('thick Greek', 'Greek') for x in r['ing']]
    r['notes'] = [x.replace('thick Greek', 'Greek') for x in r['notes']]

PHOTO = {
 'Raspberry Chia Seed Pudding': 'raspberry-chia', 'Mango Chia Seed Pudding': 'mango-chia', 'Banana & Cinnamon Chia Pudding': 'banana-chia',
 'Almond & Banana Overnight Oats': 'almond-banana-oats', 'Strawberry & Cream Overnight Oats': 'strawberry-oats',
 'Tiramisu Overnight Oats': 'tiramisu-oats', 'Chocolate, Peanut Butter & Banana Oats': 'choc-pb-oats',
 'Apple Pie Overnight Oats': 'new-apple-pie-overnight-oats',
 'Creamy Greek Yogurt Porridge': 'greek-yogurt-porridge', 'Berry & Nut Porridge': 'berry-nut-porridge',
 'Baked Banana Porridge': 'baked-banana-porridge', 'Creamy Cinnamon Rice Porridge': 'new-rice-porridge', 'Warm Quinoa & Berry Bowl': 'new-quinoa-berry-bowl',
 'Crunchy Homemade Granola': 'granola', 'Berries, Granola & Honey Bowl': 'berries-granola-bowl', 'Tropical Yogurt Bowl': 'tropical-bowl',
 'Classic Fluffy American Pancakes': 'classic-pancakes', 'Oat Pancakes': 'oat-pancakes',
 'Cottage Cheese & Banana Pancakes': 'cottage-banana-pancakes', 'Fluffy Buttermilk Blueberry Pancakes': 'blueberry-pancakes',
 'Fluffy Greek Yogurt Pancakes': 'new-greek-yogurt-pancakes', 'French Toast with Greek Yogurt & Berries': 'french-toast',
 'Cottage Cheese & Avocado Toast': 'new-avocado-toast', 'Cottage Cheese & Smoked Salmon Toast': 'salmon-toast',
 'Banana Bread': 'banana-bread', 'Peanut Butter & Banana Toast': 'new-pb-banana-toast', 'Ricotta & Blueberry Jam Toast': 'new-ricotta-blueberry-toast',
 'Spinach & Feta Egg Muffins': 'new-egg-muffins', 'Tofu Scramble on Toast': 'new-tofu-scramble',
 'Smoked Salmon & Scrambled Egg Toast': 'salmon-scrambled', 'Breakfast Quesadilla': 'new-quesadilla',
 'Sweet Potato & Egg Hash': 'new-sweet-potato-hash', 'Classic Fluffy Omelette': 'new-omelette',
 'Banoffee Smoothie': 'banoffee', 'Green Pineapple & Yogurt Smoothie': 'green-smoothie', 'Tropical Yogurt Smoothie': 'tropical-smoothie',
 'The Athlete’s Banana & Blueberry Smoothie': 'athlete-smoothie', 'Berry Recovery Smoothie Bowl': 'new-smoothie-bowl',
}
# photos that only show an ingredient (Marine's own, kept): show them a little shorter

CHAPTERS = [
 ('Chia seed puddings', 'Fibre, plant omega-3 and make-ahead convenience', 'Chia seeds absorb liquid and thicken as they rest. Prepare these puddings the night before, then add yogurt and toppings in the morning.', ['CHIA SEED PUDDINGS']),
 ('Overnight oats', 'No cooking, endless variations', 'Overnight oats are an easy way to combine carbohydrate-rich oats with dairy, fruit, seeds and nuts. Mix the base in a jar and refrigerate overnight.', ['OVERNIGHT OATS']),
 ('Porridge & warm grains', 'Oats, rice and quinoa: warm, filling and ready to fuel training', 'Porridge is easy to adapt to appetite and training demands. Stir yogurt through after cooking rather than boiling it, to keep the texture creamy.', ['PORRIDGE', 'Warm Quinoa & Berry Bowl']),
 ('Granola & breakfast bowls', 'Build a bowl around what you need', 'Granola adds crunch and energy. Pair it with yogurt, milk or skyr and fruit for a simple breakfast that can be adjusted to your appetite.', ['GRANOLA & BREAKFAST BOWLS']),
 ('Pancakes & French toast', 'Carbohydrate-rich favourites with satisfying toppings', 'Pancakes and French toast can be useful before or after training. Add yogurt, eggs, cottage cheese or milk to make the meal more substantial.', ['PANCAKES & FRENCH TOAST']),
 ('Toasts, breads & spreads', 'Simple staples and batch-friendly bakes', 'Bread-based breakfasts are quick to assemble and easy to adapt. Add eggs, cottage cheese, yogurt or fish when you want a more protein-rich option.', ['TOASTS, BREADS & SPREADS']),
 ('Eggs & savoury breakfasts', 'A savoury start with flexible portions', 'Eggs, tofu, fish and dairy foods make useful savoury breakfast ingredients. Add bread, potatoes or other carbohydrate foods to match the session ahead.', ['Cottage Cheese & Avocado Toast', 'Cottage Cheese & Smoked Salmon Toast', 'EGGS & SAVOURY BREAKFASTS']),
 ('Smoothies & smoothie bowls', 'Quick fuel and easy-to-adjust portions', 'Smoothies can be useful when appetite or time is limited. Blending fruit does not remove its carbohydrate content; pair smoothies with a protein-rich ingredient when they are intended to replace a meal.', ['SMOOTHIES & SMOOTHIE BOWLS']),
]

MOVED = {k for c in CHAPTERS for k in c[3] if not k.isupper()}   # recipes moved to another chapter
def chapter_recipes(keys):
    out = []
    for k in keys:
        if k.isupper():
            out += [r for r in R if r['cat'] == k and r['title'] not in MOVED]
        else:
            out += [r for r in R if r['title'] == k]
    return out

CH = [(t, s, i, chapter_recipes(k)) for t, s, i, k in CHAPTERS]
assert sum(len(c[3]) for c in CH) == len(R) == 38
assert all(r['title'] in PHOTO for r in R)

POS = {'new-avocado-toast': '50% 70%'}   # crop focus for photos whose subject is off-centre
def pos(n):
    return f' style="object-position:{POS[n]}"' if n in POS else ''

def img(n):
    return 'img/' + n + '.jpg'

def macros(m, big=False):
    lab = ['kcal', 'protein', 'carbs', 'fat']
    return '<div class="mac' + (' big' if big else '') + '">' + ''.join(
        f'<div><b>{e(v.replace("g", " g") if i else v)}</b><span>{lab[i]}</span></div>' for i, v in enumerate(m)) + '</div>'

pages = []   # (html, show_footer)
def page(body, cls='', foot=True):
    pages.append((cls, body, foot))

# --- page numbers (fixed structure): cover 1, contents 2, balanced 3, author 4, then each chapter = opener + recipes
start = {}
n = 5
for t, s, i, rs in CH:
    start[t] = n
    n += 1
    for r in rs:
        r['page'] = n; n += 1
FINAL = n

# --- cover
page(f'''
<div class="cover-photos"><img src="{img('cover-chia')}" alt="Raspberry chia seed puddings in glasses"><img src="{img('cover-pancakes')}" alt="Stack of blueberry pancakes"><img src="{img('cover-smoothie')}" alt="Berry smoothie in a jar"></div>
<div class="cover-body">
 <img class="logo" src="../site/img/vivify-logo-white.webp" alt="Vivify Sports">
 <span class="eyebrow">Recipe e-book · {len(R)} recipes</span>
 <h1>Breakfasts<br>to ignite<br><em>your potential</em></h1>
 <p class="lead">Recipes for energy, recovery and performance</p>
 <p class="by">Marine Lenehan · Sports Nutritionist</p>
</div>''', 'cover', foot=False)

# --- contents
rows = [('—', 'Build a balanced breakfast', 'The four food groups, protein at breakfast and how to read the recipes', 3),
        ('—', 'A word on the author', 'Marine, sports nutritionist', 4)]
rows += [(f'{k + 1:02d}', t, f'{len(rs)} recipes', start[t]) for k, (t, s, i, rs) in enumerate(CH)]
rows += [('—', 'A final note on fuelling', 'Real food, flexible portions', FINAL)]
page('<span class="eyebrow">Inside this book</span><h2 class="pt">Contents</h2><ol class="toc">' + ''.join(
    f'<li><span class="no">{no}</span><span class="tt"><b>{e(t)}</b><small>{e(d)}</small></span><span class="pg">{p}</span></li>' for no, t, d, p in rows) + '</ol>')

# --- build a balanced breakfast
page('''<span class="eyebrow">Before you start</span><h2 class="pt">Build a balanced breakfast</h2>
<p>A useful breakfast combines foods that support your training and help you meet your overall nutritional needs. Think in terms of four groups:</p>
<div class="groups">
 <div><h3>Protein-rich foods</h3><p>Eggs, Greek yogurt, skyr, cottage cheese, milk, tofu and fish.</p></div>
 <div><h3>Carbohydrate foods</h3><p>Oats, wholegrain bread, fruit, quinoa, potatoes and cereals.</p></div>
 <div><h3>Fruit &amp; vegetables</h3><p>Berries, banana, apples, spinach, tomatoes and peppers.</p></div>
 <div><h3>Healthy fats</h3><p>Nuts, seeds, olive oil, nut butter and avocado.</p></div>
</div>
<h3 class="sub">Protein at breakfast</h3>
<p>Including a protein-rich food at breakfast is one practical way to distribute protein across the day. A broad target of around 25–40 g at a main meal can be useful for many athletes, but needs vary with body size, training load, total daily intake and individual goals. Not every breakfast needs to hit the same number.</p>
<p>You can build a protein-containing breakfast without supplements: combine dairy foods, eggs, fish or tofu with oats, bread, fruit and other toppings. If a breakfast is naturally lower in protein, add a side of yogurt, milk or eggs rather than forcing every recipe to be a high-protein meal.</p>
<div class="callout"><b>Training soon?</b><p>If you have 1.5–3 hours before training, choose a breakfast that provides carbohydrate and sits comfortably. If you have only 30–60 minutes, a smaller, easier-to-digest option may work better. Reduce fibre and fat close to exercise if they cause gastrointestinal discomfort. Match portion size to the session and your own tolerance.</p></div>
<h3 class="sub">How to read the recipes</h3>
''' + macros(['420', '28g', '44g', '14g']) + '''
<ul class="dots">
 <li>Recipes use everyday ingredients and no protein powder. Use the stated portions as a starting point and adjust quantities to appetite and training demands.</li>
 <li>Every recipe shows calories, protein, carbs and fat per serving, calculated from the ingredient quantities listed.</li>
 <li>Where a range is given, values use the midpoint. Optional items and toppings without a quantity are not counted.</li>
 <li>Values are estimates based on typical ingredient data. Brands differ, so check labels and weigh ingredients for the most accurate numbers.</li>
</ul>''', 'dense')

# --- author
page(f'''<span class="eyebrow">Meet your nutritionist</span><h2 class="pt">A word on the author</h2>
<div class="author"><img src="{img('marine')}" alt="Marine Lenehan, sports nutritionist, in a UCI rainbow-stripe jersey">
<div>
<p>Marine is an experienced sports nutritionist who brings you these breakfast recipes to ignite your potential.</p>
<p>The recommendations for living a healthy life sound simple: eat well, be regularly active, get proper sleep and practise self-care. But you probably know it is easier said than done, and life can get in the way.</p>
<p>With Marine’s healthy recipes you will feel full and ready to start your day with joy and energy.</p>
<p class="enjoy">Enjoy!</p>
</div></div>
<div class="quote"><span class="eyebrow">Healthy habits to ignite your potential</span>
<p>Vivify Sports helps cyclists, triathletes and active people fuel their training with real food: personalised nutrition coaching in English, French and Italian, online and in Ireland.</p>
<p class="link">vivifysports.com</p></div>''')

# --- chapters
for k, (t, s, intro, rs) in enumerate(CH):
    cards = ''.join(f'<li><img src="{img(PHOTO[r["title"]])}"{pos(PHOTO[r["title"]])} alt=""><span><b>{e(r["title"])}</b><small>{r["macros"][0]} kcal · {r["macros"][1].replace("g", " g")} protein</small></span><em>{r["page"]}</em></li>' for r in rs)
    page(f'''<div class="ch-no">{k + 1:02d}</div><span class="eyebrow">Chapter {k + 1:02d}</span><h2 class="ch">{e(t)}</h2>
<p class="ch-sub">{e(s)}</p><p class="ch-intro">{e(intro)}</p>
<span class="eyebrow small">In this chapter</span><ul class="ch-list n{len(rs)}">{cards}</ul>''', 'chapter')
    for r in rs:
        ph = PHOTO[r['title']]
        tips = ''.join(f'<div class="tip"><b>Vivify tip</b><p>{e(x[len("VIVIFY TIP "):])}</p></div>' for x in r['notes'] if x.startswith('VIVIFY TIP'))
        small = ' '.join(e(x) for x in r['notes'] if not x.startswith('VIVIFY TIP'))
        long = len(' '.join(r['method'])) > 520 or len(r['ing']) > 9
        page(f'''<div class="photo"><img src="{img(ph)}"{pos(ph)} alt="{e(r['title'])}"></div>
<span class="eyebrow">{e(t)}</span><h2 class="rt">{e(r['title'])}</h2><p class="serves">{e(r['serves'])}</p>
{macros(r['macros'], True)}
<div class="cols"><div class="ing"><h3>Ingredients</h3><ul>{''.join(f'<li>{e(x)}</li>' for x in r['ing'])}</ul></div>
<div class="meth"><h3>Method</h3><ol>{''.join(f'<li>{e(x)}</li>' for x in r['method'])}</ol></div></div>
{tips}{f'<p class="note">{small}</p>' if small else ''}<div class="spacer"></div>''', 'recipe')

# --- final note
credits = json.load(open(E + 'photo-credits.json'))
page(f'''<span class="eyebrow">Real food, flexible portions</span><h2 class="pt">A final note on fuelling</h2>
<p>There is no single perfect breakfast. The best option is one that you enjoy, tolerate well and can fit around your training, appetite and schedule. On harder or longer training days, increase the carbohydrate portion or add an extra side. On lighter days, choose portions that leave you comfortably satisfied.</p>
<p>Whole foods first does not mean supplements are never useful. It simply means these recipes are designed to work without protein powder, using familiar ingredients that also bring other nutrients, flavour and texture.</p>
<div class="cta">
 <a href="https://vivifysports.com/blog/"><span class="eyebrow">Keep cooking</span><b>More recipes, fuelling tips and articles from Marine on the Vivify Sports blog.</b><em>vivifysports.com/blog</em></a>
 <a href="https://vivifysports.com/sports-nutritionist-ireland/"><span class="eyebrow">Personalised recipes</span><b>For personalised recipes and nutrition coaching for all diets.</b><em>vivifysports.com/sports-nutritionist-ireland</em></a>
</div>
<div class="end"><img class="logo" src="../site/img/vivify-logo-white.webp" alt="Vivify Sports"><p>Healthy habits to ignite your potential</p></div>
<p class="credits">Photography: Marine Lenehan / Vivify Sports. Additional photos are free-to-use public-domain (CC0) images from the WordPress Photo Directory and Openverse.
© Vivify Sports. For personal use only; please do not share or resell.</p>''', 'final')

CSS = r'''
@page{size:A4;margin:0}
:root{--bg:#0C2226;--teal:#19444B;--panel:#123338;--border:rgba(177,216,221,.16);--text:#f4f8f8;--text-2:#d2e1e3;--text-3:#8fb0b4;--aqua:#B1D8DD;--lime:#80A315;--lime-text:#9cc21f}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg)}
body{font:10.5pt/1.6 Montserrat,sans-serif;color:var(--text-2);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:210mm;height:297mm;position:relative;overflow:hidden;padding:18mm 18mm 22mm;page-break-after:always;break-after:page;
 background:radial-gradient(140mm 90mm at 100% 0,rgba(177,216,221,.08),transparent 70%),radial-gradient(120mm 90mm at 0 100%,rgba(128,163,21,.07),transparent 70%),var(--bg)}
.page:last-child{page-break-after:auto;break-after:auto}
h1,h2,h3{font-family:Anton,Impact,sans-serif;font-weight:400;text-transform:uppercase;color:var(--text);margin:0;line-height:1.05;letter-spacing:.01em}
p{margin:0 0 3.2mm;text-align:justify;hyphens:auto}
.eyebrow{display:block;font:600 8pt/1.4 Montserrat,sans-serif;letter-spacing:.2em;text-transform:uppercase;color:var(--lime-text);margin:0 0 2.5mm}
.eyebrow.small{margin-top:7mm}
.pt{font-size:34pt;margin-bottom:6mm}
.pt::after,.ch::after{content:"";display:block;width:16mm;height:1mm;background:var(--aqua);border-radius:1mm;margin-top:4mm}
.foot{flex:none!important;position:absolute;left:18mm;right:18mm;bottom:9mm;display:flex;justify-content:space-between;border-top:1px solid var(--border);padding-top:2.5mm;font:600 7pt/1 Montserrat,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--text-3)}
.foot b{color:var(--aqua);font-weight:600}
/* cover */
.cover{padding:0}
.cover-photos{display:grid;grid-template-columns:1fr 1.25fr 1fr;height:132mm;gap:0}
.cover-photos img{width:100%;height:100%;object-fit:cover}
.cover-photos::after{content:"";position:absolute;left:0;right:0;top:80mm;height:53mm;background:linear-gradient(transparent,var(--bg))}
.cover-body{position:relative;padding:0 18mm;margin-top:-8mm;z-index:2}
.cover .logo{width:30mm;margin-bottom:8mm}
.cover h1{font-size:52pt;line-height:.98;margin:2mm 0 6mm}
.cover h1 em{font-style:normal;color:var(--aqua)}
.lead{font-size:13pt;color:var(--text);text-align:left}
.by{font:600 9pt/1.4 Montserrat,sans-serif;letter-spacing:.18em;text-transform:uppercase;color:var(--text-3);margin-top:10mm;border-top:1px solid var(--border);padding-top:5mm;text-align:left}
/* contents */
.toc{list-style:none;margin:2mm 0 0;padding:0}
.toc li{display:grid;grid-template-columns:14mm 1fr 14mm;align-items:center;padding:3.6mm 0;border-bottom:1px solid var(--border)}
.toc .no{font:400 17pt/1 Anton,sans-serif;color:var(--lime-text)}
.toc b{display:block;font:400 14pt/1.15 Anton,sans-serif;text-transform:uppercase;color:var(--text)}
.toc small{display:block;color:var(--text-3);font-size:8.5pt;margin-top:1mm}
.toc .pg{text-align:right;font:600 11pt/1 Montserrat,sans-serif;color:var(--aqua)}
/* balanced */
.dense p{font-size:9.6pt;margin-bottom:2.6mm}
.groups{display:grid;grid-template-columns:1fr 1fr;gap:3mm;margin:3mm 0 5mm}
.groups div{background:var(--panel);border:1px solid var(--border);border-radius:3mm;padding:3.5mm 4.5mm;border-top:1mm solid var(--lime)}
.groups h3{font-size:12pt;margin-bottom:1.5mm}
.groups p{margin:0;text-align:left}
.sub{font-size:15pt;margin:4mm 0 2.5mm;color:var(--aqua)}
.callout,.tip{background:rgba(128,163,21,.12);border-left:1mm solid var(--lime);border-radius:0 3mm 3mm 0;padding:3.5mm 5mm;margin:3mm 0}
.callout b,.tip b{display:block;font:600 8pt/1.4 Montserrat,sans-serif;letter-spacing:.18em;text-transform:uppercase;color:var(--lime-text);margin-bottom:1mm}
.callout p,.tip p{margin:0}
.dots{margin:3mm 0 0;padding-left:5mm;font-size:9.2pt}
.dots li{margin-bottom:1.4mm;text-align:justify}
.dots li::marker{color:var(--lime-text)}
/* macros */
.mac{display:grid;grid-template-columns:repeat(4,1fr);gap:2.5mm;margin:2mm 0 3mm}
.mac div{background:var(--panel);border:1px solid var(--border);border-radius:3mm;text-align:center;padding:2.6mm 1mm}
.mac b{display:block;font:400 17pt/1 Anton,sans-serif;color:var(--text)}
.mac span{display:block;font:600 6.8pt/1 Montserrat,sans-serif;letter-spacing:.18em;text-transform:uppercase;color:var(--aqua);margin-top:1.6mm}
.mac div:first-child{background:var(--aqua);border-color:var(--aqua)}
.mac div:first-child b{color:var(--bg)}.mac div:first-child span{color:var(--teal)}
/* author */
.author{display:grid;grid-template-columns:62mm 1fr;gap:9mm;align-items:start}
.author img{width:100%;border-radius:4mm;border:1px solid var(--border)}
.author p{font-size:11.5pt}
.enjoy{font:400 22pt/1 Anton,sans-serif!important;text-transform:uppercase;color:var(--aqua);margin-top:5mm}
.quote{margin-top:12mm;background:var(--panel);border:1px solid var(--border);border-radius:4mm;padding:7mm 8mm}
.quote .link{font-weight:600;color:var(--aqua);margin:0}
/* chapter */
.ch-no{position:absolute;right:14mm;top:6mm;font:400 120pt/1 Anton,sans-serif;color:rgba(177,216,221,.08)}
.ch{font-size:40pt;margin:0 0 4mm;max-width:150mm}
.ch-sub{font-size:12.5pt;color:var(--aqua);font-weight:500;text-align:left}
.ch-intro{font-size:11pt;max-width:165mm}
.chapter>*{flex:0 0 auto}
.ch-list{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;grid-auto-rows:1fr;gap:4mm;flex:1 1 0!important;min-height:0}
.ch-list li{display:grid;grid-template-columns:48% 1fr 9mm;grid-template-rows:100%;gap:4mm;align-items:center;background:var(--panel);border:1px solid var(--border);border-radius:3mm;padding:2.5mm;overflow:hidden;min-height:0}
.ch-list.n3 li,.ch-list.n5 li:last-child{grid-column:span 2}
.ch-list.n3{grid-template-columns:1fr}
.ch-list img{width:100%;height:100%;object-fit:cover;border-radius:2mm}
.ch-list b{display:block;font:400 11.5pt/1.15 Anton,sans-serif;text-transform:uppercase;color:var(--text)}
.ch-list small{display:block;font-size:8pt;color:var(--text-3);margin-top:1.2mm}
.ch-list em{font:600 10pt/1 Montserrat,sans-serif;font-style:normal;color:var(--aqua);text-align:right;padding-right:2mm}
.ch-list.n3 li,.ch-list.n5 li:last-child{grid-template-columns:55% 1fr 10mm}.ch-list.n3 b{font-size:15pt}
/* recipe */
.recipe,.chapter{display:flex;flex-direction:column}
.recipe{padding-top:14mm}
.recipe>*{flex:0 0 auto}
.photo{flex:1 1 0!important;min-height:66mm;border-radius:4mm;overflow:hidden;margin-bottom:6mm;border:1px solid var(--border)}
.photo img{width:100%;height:100%;object-fit:cover;display:block}
.rt{font-size:27pt;margin:0 0 1.5mm}
.serves{font-size:9pt;color:var(--text-3);margin-bottom:3mm;text-align:left}
.cols{display:grid;grid-template-columns:62mm 1fr;gap:7mm;margin-top:2mm}
.cols h3{font-size:12pt;color:var(--aqua);margin-bottom:2.5mm;letter-spacing:.06em}
.ing{background:var(--panel);border:1px solid var(--border);border-radius:3mm;padding:4mm 4.5mm}
.ing ul{list-style:none;margin:0;padding:0;font-size:10pt;line-height:1.45}
.ing li{padding:1.1mm 0 1.1mm 4mm;position:relative;border-bottom:1px solid rgba(177,216,221,.08)}
.ing li:last-child{border:0}
.ing li::before{content:"";position:absolute;left:0;top:2.9mm;width:1.6mm;height:1.6mm;border-radius:50%;background:var(--lime)}
.meth ol{list-style:none;margin:0;padding:0;counter-reset:s;font-size:10.2pt;line-height:1.55}
.meth li{counter-increment:s;position:relative;padding-left:9mm;margin-bottom:2.4mm;text-align:justify;hyphens:auto}
.meth li::before{content:counter(s);position:absolute;left:0;top:.2mm;width:6mm;height:6mm;border-radius:50%;background:var(--teal);color:var(--aqua);font:600 8pt/6mm Montserrat,sans-serif;text-align:center}
.tip{margin-top:4mm}
.spacer{height:6mm}
.tip p{font-size:9.4pt}
.note{font-size:8pt;color:var(--text-3);font-style:italic;margin-top:3mm;text-align:left}
/* final */
.cta{display:grid;grid-template-columns:1fr 1fr;gap:5mm;margin:8mm 0}
.cta a{display:block;text-decoration:none;background:var(--panel);border:1px solid var(--border);border-top:1mm solid var(--aqua);border-radius:3mm;padding:6mm}
.cta b{display:block;color:var(--text);font-weight:500;font-size:10.5pt;line-height:1.5}
.cta em{display:block;font-style:normal;font-weight:600;color:var(--aqua);margin-top:4mm;font-size:9pt}
.end{text-align:center;margin-top:16mm}
.end .logo{width:34mm;margin:0 auto 4mm;display:block}
.end p{text-align:center;font:600 8.5pt/1.4 Montserrat,sans-serif;letter-spacing:.2em;text-transform:uppercase;color:var(--text-3)}
.credits{position:absolute;left:18mm;right:18mm;bottom:20mm;font-size:7.2pt;color:var(--text-3);text-align:center}
'''

def build():
    out = []
    for k, (cls, body, foot) in enumerate(pages, 1):
        f = f'<div class="foot"><span><b>Vivify Sports</b> · Breakfasts to ignite your potential</span><span>vivifysports.com · {k}</span></div>' if foot else ''
        out.append(f'<section class="page {cls}">{body}{f}</section>')
    assert len(pages) == FINAL, (len(pages), FINAL)
    doc = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Breakfasts to Ignite Your Potential | Vivify Sports</title>'
           '<link href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">'
           f'<style>{CSS}</style></head><body>' + '\n'.join(out) + '</body></html>')
    open(E + 'ebook.html', 'w').write(doc)
    js = r'''
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + process.argv[2], { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  // Chrome's print layout does not grow flex items inside fixed-height pages: freeze the screen sizes first
  await p.evaluate(() => document.querySelectorAll('.photo,.ch-list').forEach(el => { el.style.height = el.offsetHeight + 'px'; el.style.setProperty('flex', 'none', 'important'); }));
  const fonts = await p.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight));
  // any recipe page whose content overflows the page?
  const over = await p.evaluate(() => [...document.querySelectorAll('.page')].map((s, i) => {
    const foot = s.querySelector('.foot'); const lim = foot ? foot.offsetTop : s.clientHeight;
    let max = 0; for (const c of s.children) if (c !== foot && !c.classList.contains('ch-no') && !c.classList.contains('credits')) max = Math.max(max, c.offsetTop + c.offsetHeight);
    return max > lim ? (i + 1) + ':' + (max - lim) : null }).filter(Boolean));
  console.log('fonts', JSON.stringify(fonts)); console.log('overflow', JSON.stringify(over));
  await p.pdf({ path: process.argv[3], preferCSSPageSize: true, printBackground: true });
  await b.close();
})();'''
    js_path = E + '.render.js'
    open(js_path, 'w').write(js)
    subprocess.run(['node', js_path, E + 'ebook.html', E + 'Breakfasts-to-Ignite-Your-Potential.pdf'], check=True, cwd=E)
    os.remove(js_path)

if __name__ == '__main__':
    build()
    print(len(pages), 'pages')

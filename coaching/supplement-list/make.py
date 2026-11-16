# Builds supplements.html (Cigala brand-kit version of Marine Lenehan's Supplement List).
# Re-uses the Nutritional Guide stylesheet so both documents match. Text is Marine's, word for word.
# Run: python3 -I coaching/supplement-list/make.py && node coaching/supplement-list/build.js [previewDir]
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
guide = open(os.path.join(HERE, '..', 'nutrition-guide', 'guide.html')).read()
style = guide[guide.index('<style>') + 7:guide.index('</style>')]
style = style.replace('url(assets/', 'url(../nutrition-guide/assets/')
A = '../nutrition-guide/assets/'

style += '''
/* supplement list: one colour per moment, matching the Nutritional Guide key */
:root{--c-daily:#34c46a;--c-before:#4aa8e8;--c-proto:#f2cf4a;--c-during:#f28c38;--c-after:#e8606a}
.sup td{font-size:11.5px;padding:7px 12px}
.sup td:first-child{font-weight:600;color:var(--text);width:30%}
.sup td:nth-child(2){font-weight:600;color:var(--text);width:24%}
.sup td.e{color:var(--text-3);font-weight:400}
.sup th{border-bottom:2px solid var(--topic)}
.chips{display:flex;flex-wrap:wrap;gap:7px}
.chip{display:inline-block;border-radius:999px;padding:5px 12px;font-size:11px;font-weight:600;color:#08090a;background:var(--topic)}
.chip.o{background:transparent;color:var(--text);border:1px solid var(--border-strong)}
.ph{background:var(--panel);border:1px solid var(--border);border-top:3px solid var(--topic);border-radius:12px;padding:14px 16px}
.ph .hd{display:flex;align-items:center;gap:8px}
.ph .hd i{width:9px;height:9px;border-radius:50%;background:var(--topic);display:inline-block}
.ph .anton{font-size:20px}
.ph .sb{font-size:10px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--text-3);margin:2px 0 10px}
.ph .dots li::before{background:var(--topic)}
.flow{display:grid;grid-template-columns:1fr 18px 1fr 18px 1fr;align-items:stretch;gap:6px}
.flow .ar{display:flex;align-items:center;justify-content:center;color:var(--text-3);font-size:16px}
.down{text-align:center;color:var(--text-3);font-size:18px;margin:6px 0}
.mantra{text-align:center;margin-top:14px;padding:12px;border-top:1px solid var(--border-strong);border-bottom:1px solid var(--border-strong);font-family:Anton,sans-serif;text-transform:uppercase;font-size:19px;color:var(--text);letter-spacing:.03em}
.mantra span{color:var(--green-text);margin:0 10px}
.sport .dots{gap:9px}
.sport .dots li::before{background:var(--text-2)}
.italic{font-style:italic;color:var(--text-3);font-size:11px;margin-top:8px}
.buy p{margin:0 0 8px}.buy p:last-child{margin:0}
'''

FOOT = '  <div class="foot"><span>Cigala Cycling × Vivify Sports · Supplement List</span><span class="n">{n}</span></div>\n'
RUN = '  <div class="run"><span>Supplements are here to support your training, not replace a healthy diet</span></div>\n'

def table(rows):
    h = '<div class="tbl sup"><table>\n    <tr><th>Supplement</th><th>Dose / detail</th><th>Notes</th></tr>\n'
    for r in rows:
        cells = ''.join(f'<td class="e">–</td>' if c in ('', '–') else f'<td>{c}</td>' for c in r)
        h += f'    <tr>{cells}</tr>\n'
    return h + '  </table></div>\n'

def sec(num, title, sub, label):
    return f'''  <div class="sec">
    <span class="big">{num}</span>
    <div class="eyebrow">Section {num}<span class="topic"><i></i>{label}</span></div>
    <h2>{title}</h2>
    <div class="bar"></div>
    <p class="sub">{sub}</p>
  </div>
'''

pages = []
# 1 cover
pages.append(f'''<section class="page cover">
  <div class="in">
    <div class="logos">
      <img class="cc" src="{A}cigala-cycling-logo-square-print.png" alt="Cigala Cycling logo">
      <span class="x">×</span>
      <img class="vv" src="{A}vivify-sports-logo-white-print.png" alt="Vivify Sports logo">
    </div>
    <div class="eyebrow">Cigala Cycling × Vivify Sports</div>
    <h1 style="margin-top:12px">Supplement<br>List</h1>
    <div class="bar"></div>
    <p class="tag">Evidence-based support for cyclists and triathletes.</p>
  </div>
  <div class="photo" style="height:92mm"><img src="{A}matteo-cigala-gravel-worlds-silver.jpg" alt="Matteo Cigala, silver at the World Championship Gravel 19-34" style="object-position:0% 26%"></div>
  <div class="by">
    <div class="avrow"><img class="av viv" src="{A}avatar-marine-lenehan.jpg" alt="Marine Lenehan"><div><div class="who">Marine Lenehan</div><div class="role">Sports Nutritionist · Vivify Sports</div></div></div>
  </div>
</section>''')

# 2 essentials at a glance
pages.append(f'''<section class="page">
{RUN}  <div class="sec">
    <div class="eyebrow">The essentials</div>
    <h2>The essentials at a glance</h2>
    <div class="bar"></div>
  </div>
  <div class="ph" style="--topic:var(--c-daily)">
    <div class="hd"><i></i><span class="anton">Every day</span></div>
    <div class="chips" style="margin-top:10px"><span class="chip">Multivitamin A–Z</span><span class="chip">Vitamin D3</span><span class="chip">Omega-3</span><span class="chip">Zinc (men) / Evening primrose (women)</span></div>
    <p style="margin:12px 0 7px;font-size:11px;color:var(--text-3)">Useful, but not daily essentials:</p>
    <div class="chips"><span class="chip o">Vitamin C</span><span class="chip o">B complex</span><span class="chip o">Creatine</span><span class="chip o">Probiotics</span><span class="chip o">Ashwagandha (advice first)</span></div>
  </div>
  <div class="down">↓</div>
  <div class="flow">
    <div class="ph" style="--topic:var(--c-before)"><div class="hd"><i></i><span class="anton">Before</span></div><div class="sb">Hard and long sessions</div>
      <ul class="dots"><li>Caffeine 100 mg</li><li>Beetroot juice: threshold or VO2 sessions only, 120 min before</li><li>Arginine 3 g</li><li>Electrolyte drink in heat or indoors</li></ul></div>
    <div class="ar">→</div>
    <div class="ph" style="--topic:var(--c-during)"><div class="hd"><i></i><span class="anton">During</span></div><div class="sb">Races and long sessions</div>
      <ul class="dots"><li>Carbohydrate 30–90 g per hour</li><li>Gels with 40 g of carbs each</li><li>Electrolytes</li><li>Caffeine: max 420 mg per race</li></ul></div>
    <div class="ar">→</div>
    <div class="ph" style="--topic:var(--c-after)"><div class="hd"><i></i><span class="anton">After</span></div><div class="sb">Races and hard sessions</div>
      <ul class="dots"><li>Whey protein 25–30 g (ALWAYS)</li><li>Carbohydrate if next session is within 8 h</li><li>Magnesium bisglycinate 400 mg</li><li>Collagen 20 g with vitamin C</li><li>Electrolytes</li></ul></div>
  </div>
  <div class="ph" style="--topic:var(--c-proto);margin-top:14px">
    <div class="hd"><i></i><span class="anton">Race day only</span></div><div class="sb" style="color:var(--c-proto)">Specific protocol required</div>
    <div class="chips"><span class="chip">Beta-alanine</span><span class="chip">Creatine</span><span class="chip">Glycerol</span><span class="chip">Sodium bicarbonate</span></div>
  </div>
  <div class="mantra">Food first<span>•</span>Test, don’t guess<span>•</span>Trial everything in training</div>
  <div class="panel" style="margin-top:14px;padding:11px 16px"><div class="eyebrow" style="margin-bottom:6px">Colour key</div>
    <div class="key"><span><i style="background:var(--c-daily)"></i>Every day</span><span><i style="background:var(--c-before)"></i>Before</span><span><i style="background:var(--c-during)"></i>During (fuel)</span><span><i style="background:var(--c-after)"></i>After (recovery)</span><span><i style="background:var(--c-proto)"></i>Specific protocol</span></div>
    <p style="margin:6px 0 0;font-size:10.5px;color:var(--text-3)">The same colours as the Nutritional Guide: green for vitamins and minerals, orange for carbohydrate fuel, rose for protein and recovery.</p></div>
''' + FOOT + '</section>')

# 3 quick guide by sport
pages.append(f'''<section class="page">
{RUN}  <div class="sec">
    <div class="eyebrow">By discipline</div>
    <h2>Quick guide by sport</h2>
    <div class="bar"></div>
    <p class="sub">A general starting point by discipline and event length. The right choices depend on your event, your blood results and what you tolerate. Practise everything in training.</p>
  </div>
  <div class="g2 sport" style="align-items:start">
    <div class="hc"><div class="hd">Cyclists</div><ul class="dots">
      <li><b>Road races and long rides:</b> 60–90 g of carbs per hour from a glucose + fructose drink mix and gels (40 g each). Add electrolytes, and sodium capsules in the heat.</li>
      <li><b>Time trials, threshold and VO2 sessions:</b> beetroot juice (500 mg nitrates) at least 120 minutes before, and caffeine 100 mg.</li>
      <li><b>Late in a race:</b> a carbohydrate &amp; caffeine gel. Stay under 420 mg of caffeine per race.</li>
      <li><b>Sprint and track:</b> creatine 3–5 g/day if used. Trial any sodium bicarbonate protocol in training.</li>
      <li><b>Indoor training:</b> an electrolyte drink, as sweat rates are higher without airflow.</li>
      <li><b>Recovery:</b> whey protein 25–30 g, plus a carbohydrate recovery drink if the next session is within 8 hours.</li></ul></div>
    <div class="hc"><div class="hd">Triathletes</div><ul class="dots">
      <li><b>Sprint and Olympic (1–2.5 h):</b> 30–60 g of carbs per hour, mostly on the bike. Caffeine chews or gum before the run.</li>
      <li><b>Half distance (4–6 h):</b> 60–90 g of carbs per hour from a glucose + fructose mix on the bike, with electrolytes. Sodium capsules in the heat.</li>
      <li><b>Full distance (8 h +):</b> 90 g of carbs per hour or more with gut training. Spread caffeine across the race, max 420 mg.</li>
      <li><b>Training blocks:</b> omega-3 and vitamin D, and magnesium bisglycinate 400 mg/day after sessions.</li>
      <li><b>Brick and indoor sessions:</b> an electrolyte drink and a gel or chews to practise race fuelling.</li>
      <li><b>Recovery:</b> whey protein 25–30 g after every hard session, and collagen 20 g with vitamin C.</li></ul></div>
  </div>
  <div class="mphoto" style="height:78mm;margin-top:16px"><img src="{A}cigala-cycling-jersey-wicklow.jpg" alt="Cigala Cycling rider in team kit looking over the Wicklow mountains, Ireland" style="object-position:50% 40%"></div>
''' + FOOT + '</section>')

# 4 daily
daily = [('Multivitamin A–Z','','Broad cover for gaps in the diet.'),
 ('Vitamin D (D3)','','Bone health and immune function. Check levels, especially in low-sunlight months.'),
 ('Omega-3','','Specifically during high training loads, or if the diet is low in fish.'),
 ('Zinc','','Immune system and men’s health.'),
 ('Evening primrose','','Women’s health.'),
 ('Iron','Only if deficient','Common in female and endurance athletes. Supplement only after a blood test.'),
 ('Vitamin B12','','For vegan and plant-based athletes.')]
useful = [('Vitamin C','','Prefer natural sources like acerola, or directly from food. Useful, not a daily essential.'),
 ('B complex','','For specific cases only. Useful, not a daily essential.'),
 ('Creatine monohydrate','3–5 g / day when used','Strength, power and recovery. Useful, not a daily essential. May add around 1 kg of water weight.'),
 ('Probiotics','','Gut health and travel. Useful, not a daily essential. Effects are strain-specific.'),
 ('Ashwagandha','','Attention to thyroid conditions. <b>Do not supplement without advice.</b>')]
pages.append('<section class="page" style="--topic:var(--c-daily)">\n' + RUN + sec('01','Daily','The everyday foundation, ideally guided by a blood panel','Every day')
 + table(daily) + '  <h3>Useful, but not daily essentials</h3><div class="bar"></div>\n' + table(useful) + FOOT + '</section>')

# 5 before training + before races
before = [('Arginine','3 g',''),('Caffeine','100 mg',''),
 ('Beetroot juice','Delivering 500 mg nitrates','Only before threshold or VO2 sessions, at least 120 minutes before.'),
 ('Electrolyte drink','With pre-session fluids','Useful in the heat, for heavy sweaters and for indoor training.')]
races = [('Beta-alanine','','Taken over several weeks. Can cause harmless tingling.'),
 ('Creatine','','Loading or daily maintenance, depending on the plan.'),
 ('Glycerol','','Hyperhydration for hot races. Trial in training.'),
 ('Sodium bicarbonate','','Buffers acidity in high-intensity efforts. Can upset the stomach, so trial in training.'),
 ('Caffeine','','Typically 3–6 mg/kg about 60 minutes before. Trial in training.'),
 ('Beetroot juice','','Nitrate loading ahead of the event.'),
 ('Electrolytes','Potassium, chloride, calcium, magnesium, sodium','')]
pages.append('<section class="page">\n' + RUN + '<div style="--topic:var(--c-before)">' + sec('02','Before training','Before hard and long sessions','Before') + table(before) + '</div>'
 + '<div style="--topic:var(--c-proto);margin-top:22px">' + sec('03','Before races','Specific protocol required','Specific protocol') + table(races)
 + '<p class="italic">Each of these needs an individual protocol covering dose, timing and loading. Trial everything in training, never for the first time on race day.</p></div>\n' + FOOT + '</section>')

# 6 during races
during = [('Gels','','Prefer gels with 40 g of carbs per gel.'),
 ('Carbohydrate bars','','A minimum of 20 g of carbs per bar.'),
 ('Carbohydrate &amp; caffeine gels','','Don’t take more than 420 mg of caffeine per race.'),
 ('Carbohydrate jellies','',''),('Pickle juice','','Cramp prevention.'),('Quinine','','Perception of effort.'),('Electrolytes','',''),
 ('Carbohydrate drink mix','60–90 g carbs / hour','Glucose plus fructose for long events. Practise in training.'),
 ('Caffeine chews or gum','','Fast-acting option when gels are impractical, such as the run leg of a triathlon.'),
 ('Sodium capsules or salt tablets','','Hot conditions and heavy sweaters. Trial in training.')]
pages.append('<section class="page" style="--topic:var(--c-during)">\n' + RUN + sec('04','During races','Fuel, fluids and electrolytes','During') + table(during) + FOOT + '</section>')

# 7 after
after = [('Whey protein (ALWAYS)','25–30 g',''),('L-Leucine','4 g','If using a vegan protein powder.'),
 ('Cherry juice','30 ml','Stage races or altitude camps.'),
 ('BCAA','1000 mg (500 mg L-Leucine, 250 mg L-Isoleucine, 250 mg L-Valine)','If using a vegan protein powder or unable to have a protein shake.'),
 ('Magnesium bisglycinate','400 mg / day',''),('Electrolytes','Potassium, chloride, calcium, magnesium, sodium',''),
 ('Food polyphenols','','NZ blackcurrants, cherry juice, grape juice, blueberries, mixed berries, quercetin.'),
 ('Collagen','20 g with vitamin C',''),
 ('Carbohydrate recovery drink','1–1.2 g/kg per hour for the first 4 hours','When the next hard session is within 8 hours.'),
 ('Casein protein','30–40 g before sleep','Supports overnight recovery.')]
pages.append('<section class="page" style="--topic:var(--c-after)">\n' + RUN + sec('05','After races &amp; training','After races and hard or long training','After') + table(after) + FOOT + '</section>')

# 8 before you buy + bottom line + contact
pages.append(f'''<section class="page">
{RUN}  <div class="sec">
    <div class="eyebrow">Checklist</div>
    <h2>Before you buy</h2>
    <div class="bar"></div>
  </div>
  <div class="callout buy" style="margin-top:0">
    <p><b>Test first.</b> The best way to know if you need supplements is a <b>full blood panel</b>.</p>
    <p><b>Choose batch-tested products.</b> Look for independent testing such as Informed Sport, especially if you are subject to anti-doping rules.</p>
    <p><b>Trial in training.</b> Never try a new supplement or dose for the first time on race day.</p>
    <p><b>Check with a professional</b> if you have a medical condition or take medication.</p>
  </div>
  <h3 style="font-size:26px;margin-top:24px">The bottom line</h3><div class="bar"></div>
  <p>A healthy diet is always the 1st option. Healthy foods provide many substances, including vitamins and minerals, to keep us strong and healthy.</p>
  <p>You can’t just eat an orange or pop in a vitamin pill and expect one quick burst of vitamin C to prevent a cold and boost the immune system, for example. Also, it’s best for some vitamins and minerals to come from our foods rather than pill form.</p>
  <div class="anton" style="font-size:19px;margin:14px 0 10px">A balanced diet is the key to a healthy and performing body.</div>
  <p>If you would like more tailored advice on food supplements, VIVIFY SPORTS can provide you with a complete nutritional assessment. Supplements are here to support your training. If taken wrong they can actually be detrimental and decrease performance.</p>
  <div class="consult" style="margin-top:16px">
    <div class="l" style="display:flex;gap:18px;align-items:center">
      <img class="av viv" style="width:96px;height:96px" src="{A}avatar-marine-lenehan.jpg" alt="Marine Lenehan">
      <div><div class="k">Book a discovery call with Marine</div>
      <div class="person" style="margin:0"><div class="nm">Marine Lenehan</div><div class="rl">Sports Nutritionist &amp; World Tour Cyclist</div></div>
      <a class="btn" style="margin-top:8px" href="https://www.vivifysports.com/nutritionalcoaching">Book a discovery call</a></div>
    </div>
    <div class="r" style="display:flex;align-items:center">
      <div class="person" style="margin:0"><div class="k">Vivify Sports</div>
        <a href="https://vivifysports.com">vivifysports.com</a><a href="mailto:marine@vivifysports.com">marine@vivifysports.com</a><div class="c">+353 87 224 7402</div></div>
    </div>
  </div>
''' + FOOT + '</section>')

body = ''
for i, p in enumerate(pages, 1):
    body += '\n<!-- page ' + str(i) + ' -->\n' + p.replace('{n}', str(i)) + '\n'
html = f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<title>Supplement List | Cigala Cycling × Vivify Sports</title>
<link rel="stylesheet" href="{A}fonts.css">
<style>{style}</style>
</head>
<body>
{body}
</body>
</html>
'''
open(os.path.join(HERE, 'supplements.html'), 'w').write(html)
print('pages', len(pages))

"""'What your coaching looks like': an example week of Marine's nutrition coaching, for the Vivify coaching page.

Marine 17 Nov 2026: "give an example of what my coaching can look like; Cigala Cycling did a page on nutrition
where they show my services". Same sample week and notes as tools/build_coaching_nutrition.py (Cigala Coaching,
approved by Matteo 15 Nov), redrawn in Vivify's colours. Everything is labelled as a sample.
"""
from html import escape as E

WEEK = [('Mon 20', '8/28', ['Nutritional note: focus on nutrient-dense foods that support immune function'], [('str', '45m', '', 'Core & Strength Circuit | 2 lap', '', 0, None)]),
        ('Tue 21', '8/28', ['Daily macronutrient intake: 300 g carbohydrates · 160 g protein · 75 g fat'], [('ride', '1h31m', '54 km', '4×6 min torque efforts alternating + bursts', 'TEM', 1, [3, 3, 7, 7, 3, 7, 7, 3, 7, 7, 3, 2])]),
        ('Wed 22', '8/28', ['Daily macronutrient intake: 300 g carbohydrates · 160 g protein · 75 g fat'], [('ride', '58m', '33 km', 'Dynamic Efforts', 'AN', 0, [3, 4, 9, 3, 9, 3, 9, 3, 4, 2])]),
        ('Thu 23', '8/28', ['Daily macros: 280 g carbohydrates · 140 g protein'], [('str', '30m', '', 'Stretch Routine', '', 0, None)]),
        ('Fri 24', '9/28', ['Daily macronutrient intake: 560 g carbohydrates = 2,240 kcal (62.2%)'], [('ride', '3h23m', '102 km', 'LDT + 3×10′ at SS, high cadence', 'THR', 13, [4, 4, 4, 6, 6, 4, 6, 6, 4, 6, 6, 4, 4, 3])]),
        ('Sat 25', '8/28', ['Daily macros: 280 g carbohydrates · 140 g protein'], [('ride', '2h05m', '63 km', 'Active Recovery 1h30', 'AER', 0, [3, 3, 3, 3, 3, 3, 3, 3, 3, 3])]),
        ('Sun 26', '8/28', ['Daily macronutrient intake: 560 g carbohydrates = 2,240 kcal (62.2%)'], [('ride', '4h23m', '110 km', 'LDT 4h aim at 2000 m elevation', 'AER', 3, [4, 5, 4, 6, 4, 5, 6, 4, 5, 4, 6, 5, 4, 3])])]
TAGC = {'TEM': '#0e8a95', 'AN': '#7c4dff', 'THR': '#5f8f10', 'AER': '#2f80ed'}
CPH = {'4×6 min torque efforts alternating + bursts': '40–50 g/h', 'LDT + 3×10′ at SS, high cadence': '60 g/h', 'LDT 4h aim at 2000 m elevation': '60 g/h'}
CI = {'ride': '<circle cx="5.5" cy="17.5" r="3.5"/><circle cx="18.5" cy="17.5" r="3.5"/><path d="M15 6h2l3 11.5M5.5 17.5 9 9h7l-4 8.5"/>',
      'str': '<path d="M6 7v10M18 7v10M3 10v4M21 10v4M6 12h12"/>',
      'leaf': '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10Z"/><path d="M2 21c0-3 1.9-5.4 5.1-6"/>',
      'msg': '<path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 8.5 8.5 0 0 1-3.8-.9L3 21l1.9-5.7A8.5 8.5 0 1 1 21 11.5z"/>',
      'ok': '<circle cx="12" cy="12" r="10"/><path d="m8 12 3 3 5-6"/>'}
RECIPE = ('Post-ride recovery bowl', 'Serves 1 · 15 minutes', 'Approx. 85 g carbs · 50 g protein · 19 g fat',
          ['100 g basmati rice (dry weight)', '150 g chicken breast', '1 small sweet pepper and a handful of spinach', '1 tbsp olive oil', 'Lemon, salt, pepper, paprika'],
          ['Cook the rice.', 'Slice the chicken, season with paprika and pan-fry in the olive oil for 6–8 minutes.', 'Add the pepper and spinach for the last 2 minutes, then serve on the rice with a squeeze of lemon.'])
BREAKFAST = ('Pre-ride overnight oats', 'Serves 1 · 5 minutes, the night before', 'Approx. 115 g carbs · 35 g protein · 13 g fat',
             ['80 g rolled oats', '250 ml milk', '150 g Greek yoghurt', '1 banana', '1 tbsp honey', 'A handful of berries'],
             ['Mix the oats, milk and yoghurt in a jar and leave in the fridge overnight.', 'In the morning, top with sliced banana, berries and honey.', 'Eat 2–3 hours before a long or hard ride.'])
SUPPS = [('Morning', 'Vitamin D3 with breakfast, in the winter months'), ('Before key sessions', 'Caffeine, about 3 mg per kg, 45–60 minutes before hard sessions and races only'),
         ('During long rides', 'Electrolytes in your bottles, more sodium on hot days'), ('After training', '20–30 g protein (whey or food) if your next meal is more than an hour away'),
         ('Only if needed', 'Iron, only when your blood panel shows low ferritin')]
POINTS = [('One calendar', 'Your nutrition sits next to your training in TrainingPeaks or Vekta: daily macros and carbs, written for the sessions you are doing that day.'),
          ('Planned from your training load', 'Marine sees your sessions and adjusts your plan as your training changes: more carbs on the big days, less on the easy ones.'),
          ('Food diary review', 'Log what you eat in MyFitnessPal. Marine reviews your diary and sends suggestions.'),
          ('Race & event fuelling', 'A fuelling strategy for each race, with gut training so your stomach can take it on the day.')]

def svgi(k, c='cal-ic'):
    return f'<svg class="{c}" viewBox="0 0 24 24" aria-hidden="true">{CI[k]}</svg>'

def trace(v):
    w = 100 / len(v)
    return ('<svg class="cal-trace" viewBox="0 0 100 10" preserveAspectRatio="none" aria-hidden="true">'
            + ''.join(f'<rect x="{i * w:.2f}" y="{10 - h}" width="{w - .6:.2f}" height="{h}"/>' for i, h in enumerate(v)) + '</svg>')

def card(kind, d, km, t, tag, com, tr):
    tg = f'<span class="cal-tag" style="background:{TAGC[tag]}">{tag}</span>' if tag else ''
    cm = f'<span class="cal-com">{svgi("msg", "cal-ic2")}<b>{com}</b></span>' if com else ''
    return (f'<div class="cal-w"><div class="cal-wt">{svgi(kind)}<span>{E(d)}{" · " + E(km) if km else ""}</span>{tg}</div>'
            f'<div class="cal-wn"><span>{E(t)}</span><span class="cal-st">{cm}{svgi("ok", "cal-ic2 cal-done")}</span></div>'
            + (f'<span class="cal-cph"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.7s6 6.6 6 11.3a6 6 0 0 1-12 0c0-4.7 6-11.3 6-11.3z"/></svg>{CPH[t]}</span>' if t in CPH else '')
            + f'{trace(tr) if tr else ""}</div>')

def note(r, tag):
    return (f'<div class="cal-note"><div class="cal-nh"><span>Note</span><b>Nutrition</b><em>{tag}</em></div>'
            f'<p class="cal-rt">{E(r[0])}</p><p class="cal-rm">{E(r[1])}</p><p class="cal-rmac">{E(r[2])}</p>'
            f'<p class="cal-rh">Ingredients</p><ul>{"".join(f"<li>{E(x)}</li>" for x in r[3])}</ul>'
            f'<p class="cal-rh">Method</p><ol>{"".join(f"<li>{E(x)}</li>" for x in r[4])}</ol></div>')

def section(head, discovery):
    days = ''.join(f'<div class="cal-d"><div class="cal-h"><b>{d}</b></div><div class="cal-cnt">{c}</div>'
                   + ''.join(f'<div class="cal-n"><b>{svgi("leaf")}Nutrition</b><span>{E(n)}</span></div>' for n in ns)
                   + ''.join(card(*w) for w in ws) + '</div>' for d, c, ns, ws in WEEK)
    notes = (note(RECIPE, 'Recipe') + note(BREAKFAST, 'Breakfast')
             + '<div class="cal-note"><div class="cal-nh"><span>Note</span><b>Nutrition</b><em>Supplements</em></div><p class="cal-rt">Supplement plan</p>'
               '<p class="cal-rm">Food first: supplements only where they help</p><dl class="cal-sup">'
             + ''.join(f'<dt>{E(t)}</dt><dd>{E(d)}</dd>' for t, d in SUPPS) + '</dl></div>')
    pts = ''.join(f'<li><span class="h3">{E(t)}</span><p>{E(d)}</p></li>' for t, d in POINTS)
    return f"""<section class="example"><div class="wrap">
 {head('An example week', 'What your coaching looks like', center=True, lead='Train like a pro, with everything in one place: Marine works from your training calendar, so your training and your nutrition are planned together.')}
 <ul class="ex-pts">{pts}</ul>
 <figure class="ex-cal">
  <div class="cal-scroll" tabindex="0" aria-label="Example training week with nutrition notes"><div class="cal-row">{days}</div></div>
  <figcaption>An athlete’s week: every session, Marine’s nutrition for each day and the carbs per hour on the big rides. <span class="cal-swipe">Swipe to see the whole week →</span></figcaption>
  <div class="cal-notes">{notes}</div>
  <p class="cal-sample">These are samples only: Marine writes your recipes, meal plans and any supplement plan for you, after your assessment.</p>
 </figure>
 <p class="center" style="margin-top:24px"><a class="btn btn-primary" href="{discovery}">Book a free discovery call</a> <a class="btn btn-secondary" href="#plans">See the plans ↓</a></p>
</div></section>"""

CSS = r"""
/* example week (tools/vivify_example.py) */
.ex-pts{list-style:none;margin:28px 0 24px;padding:0;display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.ex-pts li{padding:18px 20px;border:1px solid var(--border);border-left:3px solid var(--lime);border-radius:12px;background:var(--panel)}
.ex-pts .h3{display:block;font-size:19px;margin-bottom:6px}
.ex-pts p{margin:0;font-size:14px}
@media (max-width:980px){.ex-pts{grid-template-columns:1fr 1fr}}@media (max-width:560px){.ex-pts{grid-template-columns:1fr}}
.ex-cal{margin:0;display:grid;gap:14px}
.ex-cal figcaption{color:var(--text-3);font-size:13px}
.cal-scroll{border-radius:14px;border:1px solid var(--border-strong);background:var(--panel-solid)}
.cal-row{display:grid;grid-template-columns:repeat(7,minmax(0,1fr))}
.cal-d{border-right:1px solid var(--border);padding:0 7px 10px;display:grid;align-content:start;gap:7px;min-width:0}
.cal-d:last-child{border-right:0}
.cal-h{margin:0 -7px;padding:8px 10px;border-bottom:1px solid var(--border);background:rgba(177,216,221,.06)}
.cal-h b{font:400 17px/1 Anton,sans-serif;color:var(--text);text-transform:uppercase}
.cal-cnt{text-align:center;font-size:11px;color:var(--text-3);border:1px solid var(--border);border-radius:6px;padding:3px 0}
.cal-n{background:rgba(128,163,21,.10);border:1px solid rgba(128,163,21,.35);border-radius:8px;padding:7px 8px;display:grid;gap:4px}
.cal-n b{display:flex;align-items:center;gap:5px;font-size:12px;color:var(--text)}
.cal-n span{font-size:11px;line-height:1.4;color:var(--text-2)}
.cal-w{border:1.5px solid rgba(177,216,221,.55);border-radius:8px;background:rgba(255,255,255,.03);display:grid;gap:5px;overflow:hidden}
.cal-wt{display:flex;flex-wrap:wrap;align-items:center;gap:4px 5px;padding:7px 8px 0;font-size:11px;font-weight:700;color:var(--text)}
.cal-ic{width:14px;height:14px;fill:none;stroke:var(--lime-text);stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex:none}
.cal-ic2{width:14px;height:14px;fill:none;stroke:var(--text-3);stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex:none}
.cal-done{stroke:var(--aqua)}
.cal-tag{margin-left:auto;flex:none;color:#fff;font-size:9px;font-weight:700;padding:2px 4px;border-radius:3px}
.cal-wn{display:flex;justify-content:space-between;gap:6px;padding:0 8px 7px;font-size:12px;color:var(--text);line-height:1.35}
.cal-st{display:inline-flex;align-items:flex-start;gap:4px;flex:none}
.cal-com{display:inline-flex;align-items:center;gap:2px;font-size:10px;color:var(--text-3)}
.cal-com b{color:#f0bf00}
.cal-cph{justify-self:start;display:inline-flex;align-items:center;gap:4px;margin:0 8px 4px;padding:2px 9px;border:1px solid var(--aqua);border-radius:999px;color:var(--aqua);font-size:11px;font-weight:700}
.cal-cph svg{width:11px;height:11px;fill:none;stroke:currentColor;stroke-width:2.2}
.cal-trace{display:block;width:100%;height:22px;margin-top:-4px}
.cal-trace rect{fill:rgba(177,216,221,.22)}
.cal-swipe{display:none;color:var(--lime-text)}
@media (max-width:1100px){.cal-scroll{overflow-x:auto;scroll-snap-type:x mandatory}.cal-row{grid-template-columns:repeat(7,165px)}.cal-d{scroll-snap-align:start}.cal-swipe{display:inline}}
.cal-notes{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px;align-items:start}
.cal-note{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:16px 18px;color:var(--text-2);font-size:13px;line-height:1.55}
.cal-nh{display:flex;align-items:center;gap:8px;margin-bottom:10px}
.cal-nh span{font-weight:700;color:var(--text)}
.cal-nh b{background:rgba(128,163,21,.18);color:var(--lime-text);border-radius:6px;padding:3px 9px;font-size:12px}
.cal-nh em{font-style:normal;font-size:12px;color:var(--text-3)}
.cal-note p{margin:0;text-align:left!important}
.cal-rt{font:400 20px/1.15 Anton,sans-serif!important;text-transform:uppercase;color:var(--text)}
.cal-rm{color:var(--text-3);font-size:12px;margin-top:2px!important}
.cal-rmac{color:var(--lime-text);font-weight:700;margin:6px 0 4px!important}
.cal-rh{font-weight:700;color:var(--text);margin-top:10px!important}
.cal-note ul,.cal-note ol{margin:4px 0 0;padding-left:18px}
.cal-sup{margin:6px 0 0;display:grid;gap:2px}.cal-sup dt{font-weight:700;color:var(--text);margin-top:8px}.cal-sup dd{margin:0}
.cal-sample{margin:0;color:var(--text-3);font-size:13px;font-style:italic}
"""

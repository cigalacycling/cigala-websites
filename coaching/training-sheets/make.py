# Builds the four Cigala Cycling training sheets (3 gym circuits + Stretches & Core) in the brand kit.
# Re-uses the Nutritional Guide stylesheet and assets. Exercise wording is Matteo's, with spelling fixes only.
# Run: python3 -I coaching/training-sheets/make.py && node coaching/training-sheets/build.js [previewDir]
import os, html
HERE = os.path.dirname(os.path.abspath(__file__))
guide = open(os.path.join(HERE, '..', 'nutrition-guide', 'guide.html')).read()
style = guide[guide.index('<style>') + 7:guide.index('</style>')].replace('url(assets/', 'url(../nutrition-guide/assets/')
A = '../nutrition-guide/assets/'

style += '''
/* training sheets: green = strength & core, blue = bike & cardio, yellow = stretching & mobility */
:root{--c-str:#34c46a;--c-bike:#4aa8e8;--c-mob:#f2cf4a}
.head{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px}
.head h1{font-size:54px;line-height:.95;margin-top:10px}
.head h1 span{display:block;color:var(--text-2);font-size:30px;margin-top:6px}
.head .bar{margin-top:14px}
.head img{width:26mm;height:26mm}
.ex{display:grid;grid-template-columns:54px 50mm 1fr;align-items:center;gap:16px;background:var(--panel);border:1px solid var(--border);border-left:3px solid var(--topic);border-radius:12px;padding:8px 16px 8px 12px;margin-bottom:8px;break-inside:avoid}
.ex .no{font-family:Anton,sans-serif;font-size:34px;color:var(--topic);text-align:center;line-height:1}
.ex .im{height:26mm;background:#fff;border-radius:8px;overflow:hidden;display:flex;align-items:center;justify-content:center}
.ex .im img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.ex .im.ph{background:#000}
.ex .im.ph img{width:100%;height:100%;object-fit:cover}
.ex .im.two{flex-direction:column;gap:2px;background:#000}
.ex .im.two img{height:50%;width:100%;object-fit:cover}
.ex .nm{font-family:Anton,sans-serif;text-transform:uppercase;font-size:19px;color:var(--text);line-height:1.1}
.ex .ld{display:inline-block;margin:5px 0 3px;padding:2px 10px;border-radius:999px;border:1px solid var(--topic);color:var(--text);font-size:10.5px;font-weight:600}
.ex .ds{font-size:11.5px;color:var(--text-2);line-height:1.5}
.ex .ds div{margin-top:1px}
.ex.sc{grid-template-columns:54px 56mm 1fr}
.ex.sc .im{height:40mm}
.ex.sc .ds{font-size:12px}
.wu{display:grid;grid-template-columns:34mm 1fr;gap:16px;align-items:center;background:var(--panel);border:1px solid var(--border);border-top:3px solid var(--c-bike);border-radius:12px;padding:12px 16px;margin-bottom:14px}
.wu .im{height:24mm;background:#fff;border-radius:8px;display:flex;align-items:center;justify-content:center;overflow:hidden}
.wu .im img{max-height:100%;max-width:100%}
.wu .k{font-size:10.5px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--c-bike);margin-bottom:4px}
.wu .ds{font-size:12.5px;color:var(--text);line-height:1.55}
.div{display:flex;align-items:center;gap:14px;margin:10px 0 12px;font-family:Anton,sans-serif;text-transform:uppercase;font-size:17px;color:var(--text);letter-spacing:.04em}
.div::before,.div::after{content:"";flex:1;height:1px;background:var(--border-strong)}
.imp{background:var(--panel);border:1px solid var(--border);border-left:3px solid var(--red);border-radius:12px;padding:14px 18px;margin-top:6px}
.imp .anton{font-size:20px;margin-bottom:8px}
.imp .dots li::before{background:var(--red)}
.made{display:grid;grid-template-columns:auto 1fr auto;gap:18px;align-items:center;margin-top:14px;padding:18px 20px;border:1px solid var(--border-strong);border-radius:12px;background:var(--panel)}
.made .av{width:76px;height:76px}
.made .k{font-size:10.5px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--red-text);margin-bottom:4px}
.made .nm{font-family:Anton,sans-serif;text-transform:uppercase;font-size:21px;color:var(--text)}
.made .c{font-size:11.5px;color:var(--text);line-height:1.6;margin-top:4px}
.made .c a{color:var(--text);text-decoration:none}
.made .btn{margin:0;white-space:nowrap}
.key{margin:0 0 14px}
'''

PHONE = '+353 83 477 7697'
RUN_TXT = 'Cigala Cycling Coaching · Training sheet'

def foot(n, title):
    return f'  <div class="foot"><span>Cigala Cycling – www.cigalacycling.com · {title}</span><span class="n">{n}</span></div>\n'

def keybar(items):
    names = {'str': 'Strength &amp; core', 'bike': 'Bike &amp; cardio', 'mob': 'Stretching &amp; mobility'}
    return '<div class="key">' + ''.join(f'<span><i style="background:var(--c-{k})"></i>{names[k]}</span>' for k in items) + '</div>\n'

def ex_gym(doc, n, name, load, lines, kind='str'):
    ld = f'<div class="ld">{load}</div>' if load else ''
    ds = ''.join(f'<div>{l}</div>' for l in lines)
    return (f'<div class="ex" style="--topic:var(--c-{kind})"><div class="no">{n}</div>'
            f'<div class="im"><img src="img/{doc}-{n:02d}.jpg" alt="{html.escape(name)} exercise"></div>'
            f'<div><div class="nm">{name}</div>{ld}<div class="ds">{ds}</div></div></div>\n')

def made_card(email):
    return f'''<div class="made">
  <img class="av" src="{A}avatar-matteo-cigala.jpg" alt="Matteo Cigala">
  <div><div class="k">Gym circuit made by</div><div class="nm">Cigala Cycling</div>
    <div class="c"><a href="https://www.cigalacycling.com">www.cigalacycling.com</a><br>{PHONE}<br><a href="mailto:{email}">{email}</a></div></div>
  <a class="btn" href="https://calendly.com/cigalacycling">Book a free call with Matteo</a>
</div>
'''

def gym_doc(doc, title, sub, warm_k, warm, exercises, important, email, per_page):
    """exercises: list of (name, load, [lines], kind). per_page: how many exercise rows on each page."""
    pages, i, n = [], 0, 1
    for pi, count in enumerate(per_page):
        body = ''
        if pi == 0:
            body += f'''  <div class="head"><div><div class="eyebrow">Cigala Cycling Coaching</div><h1>{title}{f"<span>{sub}</span>" if sub else ""}</h1><div class="bar"></div></div>
    <img src="{A}cigala-cycling-logo-square-print.png" alt="Cigala Cycling logo"></div>
  {keybar(['str','bike'])}  <div class="wu"><div class="im"><img src="img/{doc}-warmup.jpg" alt="Warm-up"></div><div><div class="k">{warm_k}</div><div class="ds">{"<br>".join(warm)}</div></div></div>
  <div class="div">Start of the circuit</div>
'''
        for e in exercises[i:i + count]:
            body += '  ' + ex_gym(doc, n, *e)
            n += 1
        i += count
        if i >= len(exercises):
            body += '  <div class="div">End of the circuit</div>\n'
            body += '  <div class="imp"><div class="anton">Important</div><ul class="dots">' + ''.join(f'<li>{t}</li>' for t in important) + '</ul></div>\n'
            body += '  ' + made_card(email)
        pages.append(body)
    return pages

def page_wrap(pages, title):
    out = ''
    for k, b in enumerate(pages, 1):
        run = '' if k == 1 else f'  <div class="run"><span>{title}</span><span>Cigala Cycling Coaching</span></div>\n'
        out += f'<section class="page">\n{run}{b}{foot(k, title)}</section>\n'
    return out

def write(fname, title, body):
    open(os.path.join(HERE, fname), 'w').write(f'''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><title>{title} | Cigala Cycling</title>
<link rel="stylesheet" href="{A}fonts.css"><style>{style}</style></head>
<body>
{body}</body></html>
''')

W70 = 'weight around 70% of your max'
IMPORTANT_WINTER = [
    'It is important to pick the right weight for the exercises. To do so, you need to try your maximum and then make the calculation for the percentage that you need.',
    'Don’t overdo it. Accomplish the exercises correctly.',
    'If you can utilise the Wattbike instead of an exercise bike, better, as you can adapt more to the bike position.',
    None,
    'Try to stick with the order of the circuit.']
TREADMILL = ['2’ W/U', '11’ ZONE 3 at 10/15% gradient', '2’ W/D']

# ---------- Winter, first month
w1 = [
 ('Back extension', '', ['(Set pad height at mid height of your thighs)', '15 reps']),
 ('Back extension on side', '', ['15 reps']),
 ('Chest press', W70, ['10 reps']),
 ('Farmer walk', 'With a suitable weight on hands', ['15 reps']),
 ('Moving plank', 'Keep moving following picture 1 and 2', ['Hold 45 secs']),
 ('Push-up', '', ['10/15 reps']),
 ('Calf machine', 'weight about 70% of your max', ['10 reps']),
 ('Pull machine', W70, ['10 reps']),
 ('Leg curl', 'weight about 70% of your max', ['10 reps']),
 ('Triceps pushdown', W70, ['10 reps']),
 ('Leg press', '', ['5 rep at 90% of max - rec 30”', '10 rep at 80% of max - rec 1’', '15 rep 50% of max', '+ 3’ on the bike 110 rpm']),
 ('Abs on bench', '', ['20/25 reps']),
 ('Explosive jumps on step', '', ['10 reps']),
 ('Shoulder press', W70, ['10 reps']),
 ('Leg extension', '', ['5 rep at 90% of max - rec 30”', '10 rep at 80% of max - rec 1’', '15 at 50% of max']),
 ('Bike', '', ['5’ on your bike at 110 rpm'], 'bike'),
]
w1 = [e if len(e) == 4 else e + ('str',) for e in w1]
imp = [t if t else 'Make sure you recover well after the gym and get 20/25 g of whey protein straight afterwards.' for t in IMPORTANT_WINTER]
write('Gym-Circuit-Winter-First-Month.html', 'Gym Circuit Winter – First Month',
      page_wrap(gym_doc('w1', 'Gym circuit winter', 'First month', 'As a warm up, on the treadmill:', TREADMILL, w1, imp, 'info@cigalacycling.com', [5, 7, 4]), 'Gym Circuit Winter · First Month'))

# ---------- Winter, second and third month
w23 = [
 ('Farmer walk', 'With a suitable weight on hands', ['15/20 reps']),
 ('Moving plank', 'Keep moving following picture 1 and 2', ['Hold 1’/ 1’30”']),
 ('Calf machine', '', ['15/20 reps']),
 ('Shoulder press', W70, ['15/20 reps']),
 ('Leg curl', 'weight about 70% of your max', ['15/20 reps']),
 ('Pull machine', W70, ['15/20 reps']),
 ('Abs on bench', '', ['25/30 reps']),
 ('Leg press', '', ['5 rep at 90% of max - rec 30”', '10 rep at 80% of max - rec 1’', '15 rep 50% of max', '+ 3’ on the bike 110 rpm']),
 ('Triceps pushdown', W70, ['15/20 reps']),
 ('Explosive jumps on step', '', ['15/20 reps']),
 ('Push-up', '', ['20/25 reps']),
 ('Leg extension', '', ['5 rep at 90% of max - rec 30”', '10 rep at 80% of max - rec 1’', '15 at 50% of max']),
 ('Bike', '', ['5’ on your bike at 110 rpm'], 'bike'),
]
w23 = [e if len(e) == 4 else e + ('str',) for e in w23]
imp = [t if t else 'Make sure you recover well after the gym and get 20/25 g of protein straight afterwards.' for t in IMPORTANT_WINTER]
write('Gym-Circuit-Winter-Second-Third-Month.html', 'Gym Circuit Winter – Second and Third Month',
      page_wrap(gym_doc('w23', 'Gym circuit winter', 'Second and third month', 'As a warm up, on the treadmill:', TREADMILL, w23, imp, 'info@cigalacycling.com', [4, 7, 2]), 'Gym Circuit Winter · Second and Third Month'))

# ---------- In season
R = '30” to 1’ rec between'
ins = [
 ('Back extension', 'If you need to, hold a weight', ['(Set pad height at mid height of your thighs)', '2x 10 to 20 reps', R]),
 ('Back extension on side', 'If you need to, hold a weight', ['10 to 20 reps on each side', R]),
 ('Pull machine', 'weight around 60% of your max', ['2x 10 to 15 reps', R]),
 ('Farmer walk', 'With a suitable weight on hands', ['2x 10 to 20 reps on each side', R]),
 ('Moving plank', 'Keep moving following picture 1 and 2', ['Hold 1’']),
 ('Swing with kettlebell', 'with suitable weight', ['2x 15 to 30 seconds', R]),
 ('Push-up', '', ['2x 15 to 30 reps', R]),
 ('Jump rope', '2 jumps on each side consecutive', ['2x 20 to 30 seconds', R]),
 ('Calf machine', 'weight about 50% of your max', ['2x 15 to 20 quick reps', R]),
 ('Leg press', 'weight around 50% of your max, no need to go back down all the way', ['3x 15 to 20 quick reps', R, '+ 10” sprint on the bike with a big gear + 3’ Zone 2 @110']),
 ('Abs on bench', '', ['2x 20 to 30 reps', R]),
 ('Explosive jumps on step', '', ['2x 5 jumps', R]),
 ('Leg curl', 'weight about 50% of your max', ['2x 15 to 20 quick reps', R]),
 ('Leg extension', 'weight around 50% of your max, no need to go up all the way', ['3x 15 to 20 quick reps', R, '+ 10” sprint on the bike with a big gear']),
 ('Bike', '', ['continue on the bike for 10’ Zone 2 @110'], 'bike'),
]
ins = [e if len(e) == 4 else e + ('str',) for e in ins]
imp_in = [
 'In-season gym should not be traumatic. Focus more on lower weights and faster/quicker repetitions to simulate the pedalling motion.',
 'On the leg press, you do not need to go back down and bend the knee at 90 degrees. Same with leg extension, you do not need to go up all the way.',
 'It is important to pick the right weight for the exercises. To do so, you need to try your maximum and then make the calculation for the percentage that you need.',
 'If you can utilise the Wattbike instead of an exercise bike, better, as you can adapt more to the race position.',
 'Make sure you recover well after the gym, including 20/25 g of whey protein straight afterwards.',
 'Try to stick with the order of the circuit.']
write('Gym-Circuit-In-Season.html', 'Gym Circuit In Season',
      page_wrap(gym_doc('in', 'Gym circuit', 'In season', 'As a warm up, on the bike:', ['5’ W/U @100', '5’ ZONE 3 @90', '5’ W/D @100'], ins, imp_in, 'matteo@cigalacycling.com', [5, 7, 3]), 'Gym Circuit In Season'))

# ---------- Stretches & core
SC = [
 'On your back, flex your right leg and extend your left leg. With the left ankle make 20 clockwise circles. Repeat with the right ankle.',
 'On your back, put your right hand on your stomach and your left hand on your chest. Take 20 deep, slow diaphragmatic breaths: when you breathe in, inflate your stomach.',
 'On your back, flex your right leg as much as you can and bring it to the left, while your body and head rotate to the right. Hold for 30 seconds and reverse.',
 'On your back, cross and flex both legs. Keep your hands under your knees, hold the position for 1 minute and reverse.',
 'From a face-down position, sit on your heels and stretch your arms out forward. 1 minute.',
 'From the four-point position, do the “cat” movement, repeating 15 times.',
 'Sitting, extend your legs straight and together. Flex your body forward as much as you can and hold for 45 seconds.',
 'Sitting with your right leg extended and your left leg flexed, leaning backward, reach to the ankle and hold the position for 45 seconds, then reverse.',
 'Sitting with your legs crossed, flex your body forward as much as you can for 1 minute.',
 'From the four-point position, bring your left leg to the height of your left arm and extend your right leg for 1 minute, then reverse.',
 'Standing, flex your left leg for 30 seconds, then reverse.',
 'Standing, bring your left arm behind your neck and pull with your right hand. Hold for 30 seconds and reverse.',
 'Standing, bring your left arm behind your neck and pull with your right hand. Hold for 30 seconds and reverse.',
 'Standing with your legs extended, touch the floor with your hands without flexing your knees.',
 'As the exercise before, but open your legs as much as you can. Hold for 30 seconds.',
 'Sitting, flex your legs and try to keep your feet as close as possible to your body. Move your legs like wings, 50 times.',
 'On your back, cross your feet and do abs exercises, coming halfway up without touching your legs. 3 series of 50 each.',
 'On your back, bring your right foot onto your left knee. Do abs exercises touching your right knee with your left elbow. 50 times on both sides.',
 'Hold the plank position for 1 minute, keeping your body straight and contracting your abs. Repeat 3 times.',
 'As the exercise before, but hold the position on your hands instead of your elbows. Hold for 1 minute contracting your abs. Repeat 2 times.',
 'In a four-point position, raise your right arm and left leg together and hold them in position for 30 seconds. Repeat 5 times.',
 'From a face-down position, cross your legs and extend your body upwards. Do 3 series of 10 each (front, right, left).',
 'On your back, bring your legs straight up in front of you. Move your legs together to the right, keeping them straight and contracting your abs, until they almost touch the floor. Continue to the left side. Do 2 series of 20 each.',
 'On your back with your arms along your body, raise your shoulders from the floor contracting your abs and hold the position for 30 seconds. Repeat 3 times.',
 'From a face-down position, extend your arms in front of you. Raise your shoulders from the floor, going up and down with your arms straight. Do 2 series of 30 seconds each.',
 'Do 30 push-ups. On the last one, hold the position without touching the floor with your body.',
 'Standing, flex your knees and hold the position as long as you can. Recover and repeat.',
 'Standing, go down flexing your knees and come back up (squat). Do 2 series of 30 squats each. In the last series, jump on the way up.',
 'As the exercise before, but squat bending to the side: first to the right, then to the left. Do 2 series of squats on each side.',
 'Standing, put one foot behind the other and rise up onto your toes, then come back down slowly. Do 2 series of 15 for each foot (better done on the stairs).',
 'Hold the position for 1 minute on both sides, contracting your abs. Repeat moving just the body, or better the hips, up and down.',
 'On your back, contracting your abs, move your legs slowly as if you were pedalling your bike. Do it for 1 minute.',
 'With the bench behind you, standing, flex your knee and keep the left leg straight. Flex until almost sitting on the bench. Come back to the starting position and repeat 15 times for each leg.',
 'With the bench in front of you, do a strong jump landing on one foot, bringing the knee of the other leg to your stomach. Do 20 times and repeat with the other leg.',
 'With the bench in front of you, do a strong jump landing with both feet. Repeat 30 times.',
 'From this position, raise your right leg and move your hips up and down. Do 20 times for each leg.',
]
nums = [1, 2, 3, 4, 5, '6+7'] + list(range(8, 38))
assert len(SC) == len(nums) == 36
rows = []
for no, txt in zip(nums, SC):
    kind = 'mob' if (no == '6+7' or no <= 17) else 'str'
    if no == '6+7':
        im = '<div class="im two"><img src="img/sc-06a.jpg" alt="Cat stretch, back down"><img src="img/sc-06b.jpg" alt="Cat stretch, back up"></div>'
    else:
        im = f'<div class="im ph"><img src="img/sc-{no:02d}.jpg" alt="Exercise {no}"></div>'
    rows.append((no, f'<div class="ex sc" style="--topic:var(--c-{kind})"><div class="no">{no}</div>{im}<div class="ds">{txt}</div></div>\n'))
per = [4, 5, 5, 5, 5, 5, 5, 2]
pages, i = [], 0
for pi, c in enumerate(per):
    b = ''
    if pi == 0:
        b += f'''  <div class="head"><div><div class="eyebrow">Cigala Cycling Coaching</div><h1>Stretches &amp; core</h1><div class="bar"></div></div>
    <img src="{A}cigala-cycling-logo-square-print.png" alt="Cigala Cycling logo"></div>
  {keybar(['mob','str'])}  <div class="div">Stretches</div>
'''
    for no, r in rows[i:i + c]:
        if no == 18:
            b += '  <div class="div">Core &amp; strength</div>\n'
        b += '  ' + r
    i += c
    if i >= len(rows):
        b += '  ' + made_card('info@cigalacycling.com').replace('Gym circuit made by', 'Stretches &amp; core made by')
    pages.append(b)
write('Stretches-and-Core.html', 'Stretches & Core', page_wrap(pages, 'Stretches &amp; Core'))
print('ok')

"""Build the Free Tools pages (new pages, Matteo 15 Nov 2026): coachingpages/tools*.html

  /tools/                          hub
  /tools/training-zones-calculator/  power zones from FTP (or a 20-min test) + heart-rate zones from threshold HR
  /tools/carbs-per-hour-calculator/  fuelling plan: grams of carbs per hour, gels and bottles
  /tools/critical-power-calculator/  CP and W' from two maximal efforts, predicted power by duration

Everything is calculated in the visitor's browser; nothing is sent or stored. The optional newsletter sign-up posts to a
Brevo form for the separate Coaching list (NL_URL, set once Matteo has created it in Brevo; until then the box is not shown).
Class names start with tl- so the merged kit CSS can't clash with other pages.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_common import *

NL_URL = ''   # Brevo form URL for the Coaching list (…sibforms.com/serve/…?isAjax=1). Empty = no sign-up, tools open.
# Matteo 15 Nov: people must sign up before they see their results. Only active once NL_URL is set (otherwise nobody
# could unlock the tools). Once signed up, a flag in the browser keeps all three tools open for that visitor.
GATE = True
CAL = 'https://calendly.com/cigalacycling'
B = C + '/blog/'
HERO = img('IMG_4003AWDWWWU', 'tools-hero')   # Matteo coaching a group of riders (live photo)
HERO_ALT = live_alt('IMG_4003AWDWWWU')

IC = {  # line icons, same style as the packages page
    'zones': '<path d="M3 3v18h18"/><path d="M7 15v3M11 11v7M15 8v10M19 5v13"/>',
    'carbs': '<path d="M12 2v4M5 7l2.5 2.5M19 7l-2.5 2.5"/><rect x="7" y="9" width="10" height="13" rx="3"/><path d="M7 14h10"/>',
    'cp': '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    'climb': '<path d="M2 20h20L14 6l-4 6-2-3-6 11z"/><path d="M14 6l2 3"/>',
    'sweat': '<path d="M12 2.7l5.7 5.6a8 8 0 1 1-11.4 0z"/>',
    'swim': '<path d="M2 18c2 0 2-1.5 4-1.5S8 18 10 18s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><path d="M2 13c2 0 2-1.5 4-1.5S8 13 10 13s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><circle cx="16" cy="5" r="2"/><path d="M6 9l4-3 3 3"/>',
}
TOOLS = [
    ('zones', '/tools/training-zones-calculator/', 'Training Zones Calculator', 'Your 7 power zones from FTP or a 20-minute test, plus heart-rate zones from your threshold heart rate.'),
    ('carbs', '/tools/carbs-per-hour-calculator/', 'Carbs per Hour Calculator', 'How many grams of carbs to take each hour, and what that means in gels and bottles, for your ride.'),
    ('cp', '/tools/critical-power-calculator/', 'Critical Power &amp; W′ Calculator', 'Your Critical Power and W′ from two all-out efforts, and the power you can hold from 2 to 20 minutes.'),
    ('climb', '/tools/climb-time-calculator/', 'Climb Time Calculator', 'How long a famous climb, or your own, will take at your power and weight, and the power you need for a target time.'),
    ('sweat', '/tools/sweat-rate-calculator/', 'Sweat Rate Calculator', 'Weigh yourself before and after a ride to find how much you sweat, and how much to drink per hour.'),
    ('swim', '/tools/swim-pace-calculator/', 'Swim Pace (CSS) Calculator', 'For triathletes: your Critical Swim Speed from a 400 m and a 200 m time trial, and your training paces.'),
]

def hero(eyebrow, h1, lede):
    return f'''<div class="hero hero-sm tl-hero">
  <img src="{HERO}" alt="{E(HERO_ALT)}" width="2560" height="1707">
  <div class="in">
    <div class="eyebrow eb-pill"><span class="dot"></span>{eyebrow}</div>
    <h1>{h1}</h1>
    <p class="lede">{lede}</p>
  </div>
</div>'''

def gate():
    if not (GATE and NL_URL): return ''
    return f'''<div class="tl-gate" hidden>
          <form class="tl-gate-form" novalidate>
            <h3 class="h-sm">See your results</h3>
            <p>Enter your email to unlock all our free tools, and get training tips from Head Coach Matteo Cigala.</p>
            <label class="vh" for="tl-g-email">Email</label>
            <input id="tl-g-email" type="email" name="EMAIL" required autocomplete="email" inputmode="email" placeholder="Your email address *">
            <label class="tl-ok"><input type="checkbox" required><span>Yes, email me training tips and news from Cigala Cycling Coaching. I can unsubscribe at any time. See our <a href="{C}/privacy-policy/" {EXT}>privacy policy</a>.</span></label>
            <input type="text" name="email_address_check" value="" tabindex="-1" autocomplete="off" class="tl-hp" aria-hidden="true">
            <button class="btn btn-go" type="submit">Show my results</button>
            <p class="tl-nl-msg" role="status" aria-live="polite"></p>
          </form>
        </div>'''

def signup(topic):
    if not NL_URL or GATE: return ''
    return f'''<div class="tl-nl panel">
      <div><h3 class="h-sm">Get free training tips by email</h3><p>Sessions, fuelling and racing advice from Head Coach Matteo Cigala. No spam; unsubscribe any time.</p></div>
      <form class="tl-nl-form" novalidate data-topic="{topic}">
        <label class="vh" for="tl-email">Email</label>
        <div class="tl-nl-row"><input id="tl-email" type="email" name="EMAIL" required autocomplete="email" inputmode="email" placeholder="Your email address *"><button class="btn btn-go" type="submit">Subscribe</button></div>
        <label class="tl-ok"><input type="checkbox" required><span>Yes, email me training tips and news from Cigala Cycling Coaching. See our <a href="{C}/privacy-policy/" {EXT}>privacy policy</a>.</span></label>
        <input type="text" name="email_address_check" value="" tabindex="-1" autocomplete="off" class="tl-hp" aria-hidden="true">
        <p class="tl-nl-msg" role="status" aria-live="polite"></p>
      </form>
    </div>'''

def cta(text):
    return f'''<section>
  <div class="in">
    <div class="tl-cta panel">
      <div><h3 class="h-sm">Want a plan built around these numbers?</h3><p>{text}</p></div>
      <div class="ctas"><a class="btn btn-go" href="{CAL}" {EXT}>Book a free consultation →</a><a class="btn btn-ghost" href="{C}/individual-packages/" {EXT}>See the coaching packages</a></div>
    </div>
  </div>
</section>'''

def more_tools(skip):
    cards = ''.join(f'<a class="tl-card panel" href="{C}{u}" {EXT}><svg viewBox="0 0 24 24" aria-hidden="true">{IC[k]}</svg><h3>{t}</h3><p>{d}</p><span class="arrow-link">Open the calculator →</span></a>'
                    for k, u, t, d in TOOLS if k != skip)
    return f'''<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Free tools</div><h2>MORE FREE TOOLS</h2><div class="bar"></div></div></div>
    <div class="tl-cards">{cards}</div>
  </div>
</section>'''

def reads(links):
    return '<ul class="tl-reads">' + ''.join(f'<li><a href="{B}{slug}/" {EXT}>{t} →</a></li>' for slug, t in links) + '</ul>'

# ---------- shared CSS + JS ----------
TCSS = '''<style>
.tl-hero > img { object-position: 50% 40%; }
.tl-box { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: 20px; align-items: start; }
.tl-in, .tl-out { padding: 24px; }
.tl-in h2, .tl-out h2 { font-size: clamp(22px, 2.4vw, 28px); margin: 0 0 16px; }
.tl-f { display: grid; gap: 6px; margin-bottom: 16px; }
.tl-f > span, .tl-f legend { font-size: 12px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--text-3); }
.tl-f small { font-size: 12.5px; color: var(--text-3); }
.tl-f input[type=number], .tl-f select { font: 400 16px/1.4 var(--body); color: var(--text); background: rgba(255,255,255,.04); border: 1px solid var(--border-strong); border-radius: 8px; padding: 12px 14px; width: 100%; }
.tl-f select option { background: #0f1011; }
.tl-f input:focus, .tl-f select:focus { outline: 2px solid var(--green); outline-offset: 1px; border-color: transparent; }
.tl-two { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.tl-two[hidden] { display: none !important; }
fieldset.tl-f { border: 0; padding: 0; margin: 0 0 16px; }
.tl-seg { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; background: rgba(255,255,255,.04); border: 1px solid var(--border-strong); border-radius: 10px; padding: 4px; }
.tl-seg label { position: relative; text-align: center; font-size: 14px; font-weight: 600; color: var(--text-2); padding: 9px 6px; border-radius: 7px; cursor: pointer; }
.tl-seg input { position: absolute; opacity: 0; inset: 0; cursor: pointer; }
.tl-seg label:has(input:checked) { background: var(--green); color: #fff; }
.tl-seg label:has(input:focus-visible) { outline: 2px solid var(--green); outline-offset: 2px; }
.tl-check { display: flex; gap: 10px; align-items: flex-start; font-size: 14px; color: var(--text-2); margin-bottom: 16px; }
.tl-check input { width: 20px; height: 20px; accent-color: #009a44; flex: none; margin-top: 1px; }
.tl-big { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 18px; }
.tl-big div { flex: 1 1 140px; background: rgba(0,154,68,.08); border: 1px solid rgba(0,154,68,.35); border-radius: 12px; padding: 14px 16px; }
.tl-big b { display: block; font: 400 clamp(30px, 3.4vw, 40px)/1 var(--head); color: var(--text); text-transform: none; }
.tl-big span { display: block; margin-top: 6px; font-size: 12px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--text-3); }
.tl-empty { color: var(--text-3); font-size: 15px; margin: 0; }
.tl-err { color: #ff6b63; font-size: 14px; margin: 0 0 12px; }
.tl-tbl { width: 100%; border-collapse: collapse; font-size: 14.5px; margin-bottom: 18px; }
.tl-tbl caption { text-align: left; font-size: 12px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--text-3); padding: 0 0 8px; }
.tl-tbl th, .tl-tbl td { text-align: left; padding: 10px 10px; border: 0 !important; border-bottom: 1px solid var(--border) !important; background: none !important; }
.tl-tbl, .tl-tbl tr, .tl-tbl tbody, .tl-tbl thead { border: 0 !important; background: none !important; }
.tl-tbl thead th { font-size: 11.5px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--text-3); }
.tl-tbl td:last-child, .tl-tbl th:last-child { text-align: right; font-weight: 700; color: var(--text); white-space: nowrap; }
.tl-tbl tbody th { font-weight: 600; color: var(--text); }
.tl-z { display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 8px; vertical-align: 1px; }
.tl-note { font-size: 13.5px; color: var(--text-3); margin: 0; }
.tl-note a, .tl-txt a { color: var(--green-text); }
.tl-txt { max-width: 760px; }   /* left-aligned with the rest of the page, like the other sections */
.tl-txt .bar { margin-bottom: 22px; }
.tl-txt p { color: var(--text-2); font-size: 16px; line-height: 1.65; margin: 0 0 14px; }
.tl-txt ul { margin: 0 0 14px; padding-left: 20px; }
.tl-txt li { color: var(--text-2); font-size: 16px; line-height: 1.65; margin-bottom: 6px; }
.tl-txt h3 { font-size: 22px; margin: 30px 0 10px !important; }
.tl-txt ul.tl-reads { padding-left: 0; margin-top: 20px; }
.tl-reads { list-style: none; padding: 0; margin: 18px 0 0; display: grid; gap: 8px; }
.tl-reads a { color: var(--green-text); font-weight: 600; text-decoration: none; }
.tl-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }
.tl-card { display: flex; flex-direction: column; gap: 10px; padding: 24px; text-decoration: none; transition: border-color .2s, transform .2s; }
.tl-card:hover { border-color: rgba(0,154,68,.6); transform: translateY(-2px); }
.tl-card svg, .tl-ic { width: 44px; height: 44px; padding: 10px; border-radius: 10px; background: var(--green-wash); fill: none; stroke: var(--green-text); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.tl-card h3 { font-size: 24px; margin: 4px 0 0; color: var(--text); }
.tl-card p { margin: 0; font-size: 15px; color: var(--text-2); flex: 1; }
.tl-cta { display: flex; align-items: center; justify-content: space-between; gap: 24px; padding: 28px; flex-wrap: wrap; }
.tl-cta p { margin: 8px 0 0; color: var(--text-2); max-width: 60ch; }
.tl-cta .ctas { margin: 0; }
.tl-nl { margin-top: 20px; padding: 24px; display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: 24px; align-items: center; }
.tl-nl p { margin: 8px 0 0; color: var(--text-2); font-size: 15px; }
.tl-nl-row { display: flex; gap: 10px; }
.tl-nl-row input { flex: 1; min-width: 0; font: 400 16px/1.4 var(--body); color: var(--text); background: rgba(255,255,255,.04); border: 1px solid var(--border-strong); border-radius: 8px; padding: 12px 14px; }
.tl-ok { display: flex; gap: 10px; align-items: flex-start; margin-top: 12px; font-size: 13.5px; color: var(--text-2); line-height: 1.5; }
.tl-ok input { width: 18px; height: 18px; accent-color: #009a44; flex: none; margin-top: 2px; }
.tl-ok a { color: var(--green-text); }
.vh { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.tl-hp { position: absolute; left: -9999px; width: 1px; height: 1px; opacity: 0; }
.tl-nl-msg { margin: 10px 0 0; font-size: 14px; min-height: 1em; }
.tl-nl-msg.err { color: #ff6b63; } .tl-nl-msg.ok { color: var(--green-text); }
.tl-nl-form.done .tl-nl-row, .tl-nl-form.done .tl-ok { display: none; }
.tl-out { position: relative; }
.tl-out.locked [id$="-out"] { filter: blur(7px); pointer-events: none; user-select: none; }
.tl-gate { position: absolute; inset: 64px 16px auto; z-index: 2; display: grid; place-items: center; }
.tl-gate-form { width: min(440px, 100%); display: grid; gap: 12px; padding: 24px; border-radius: 14px; background: rgba(8,9,10,.94); border: 1px solid rgba(0,154,68,.5); box-shadow: 0 24px 60px rgba(0,0,0,.5); }
.tl-gate-form h3 { margin: 0; }
.tl-gate-form p { margin: 0; color: var(--text-2); font-size: 14.5px; }
.tl-gate-form input[type=email] { font: 400 16px/1.4 var(--body); color: var(--text); background: rgba(255,255,255,.04); border: 1px solid var(--border-strong); border-radius: 8px; padding: 12px 14px; width: 100%; }
.tl-gate-form .tl-ok { margin: 0; }
.tl-gate-form .btn { justify-self: start; }
@media (max-width: 900px) { .tl-box, .tl-nl { grid-template-columns: minmax(0, 1fr); } .tl-cards { grid-template-columns: minmax(0, 1fr); } }
@media (max-width: 640px) { .tl-in, .tl-out { padding: 18px; } .tl-tbl { font-size: 13.5px; } .tl-tbl th, .tl-tbl td { padding: 9px 6px; } .tl-nl-row { flex-direction: column; } }
</style>'''

NLJS = '''<script>
(function () {   /* newsletter: Brevo form for the Coaching list; only sends after the consent box is ticked */
  var f = document.querySelector('.tl-nl-form'); if (!f) return;
  var URL = %s, em = f.querySelector('input[type=email]'), ok = f.querySelector('.tl-ok input'), msg = f.querySelector('.tl-nl-msg'), btn = f.querySelector('button');
  f.addEventListener('submit', function (e) {
    e.preventDefault(); msg.className = 'tl-nl-msg';
    if (!em.value.trim() || !em.checkValidity()) { msg.className += ' err'; msg.textContent = 'Please enter a valid email address.'; em.focus(); return; }
    if (!ok.checked) { msg.className += ' err'; msg.textContent = 'Please tick the box to agree to receive our emails.'; ok.focus(); return; }
    if (f.querySelector('[name=email_address_check]').value) return;
    var fd = new FormData(); fd.append('EMAIL', em.value.trim()); fd.append('email_address_check', ''); fd.append('locale', 'en');
    btn.disabled = true; btn.textContent = 'Sending…';
    fetch(URL, { method: 'POST', body: fd }).then(function (r) { return r.json(); }).then(function (d) {
      if (!d || !d.success) throw new Error('fail');
      f.classList.add('done'); msg.className = 'tl-nl-msg ok'; msg.textContent = 'Thanks, you’re subscribed! Watch your inbox for our next tips.';
      try { if (typeof gtag === 'function') gtag('event', 'sign_up', { method: 'newsletter_tools' }); if (window.fbq) fbq('track', 'Lead'); } catch (x) {}
    }).catch(function () { msg.className = 'tl-nl-msg err'; msg.textContent = 'Sorry, that didn’t work. Please try again.'; })
      .then(function () { btn.disabled = false; btn.textContent = 'Subscribe'; });
  });
})();
</script>''' % ('"' + NL_URL + '"')

GATEJS = '''<script>
(function () {   /* sign up to see the results (Matteo 15 Nov); the flag keeps every tool open afterwards */
  var out = document.querySelector('.tl-out'), g = document.querySelector('.tl-gate'); if (!out || !g) return;
  var K = 'cc_tools_ok', open = false; try { open = localStorage.getItem(K) === '1'; } catch (e) {}
  if (open) return;
  out.classList.add('locked'); g.hidden = false;
  var f = g.querySelector('form'), em = f.querySelector('input[type=email]'), ok = f.querySelector('.tl-ok input'), msg = f.querySelector('.tl-nl-msg'), btn = f.querySelector('button');
  f.addEventListener('submit', function (e) {
    e.preventDefault(); msg.className = 'tl-nl-msg';
    if (!em.value.trim() || !em.checkValidity()) { msg.className += ' err'; msg.textContent = 'Please enter a valid email address.'; em.focus(); return; }
    if (!ok.checked) { msg.className += ' err'; msg.textContent = 'Please tick the box to continue.'; ok.focus(); return; }
    if (f.querySelector('[name=email_address_check]').value) return;
    var fd = new FormData(); fd.append('EMAIL', em.value.trim()); fd.append('email_address_check', ''); fd.append('locale', 'en');
    btn.disabled = true; btn.textContent = 'One moment…';
    fetch(%s, { method: 'POST', body: fd }).then(function (r) { return r.json(); }).then(function (d) {
      if (!d || !d.success) throw new Error('fail');
      try { localStorage.setItem(K, '1'); } catch (x) {}
      out.classList.remove('locked'); g.hidden = true;
      try { if (typeof gtag === 'function') gtag('event', 'sign_up', { method: 'tools' }); if (window.fbq) fbq('track', 'Lead'); } catch (x) {}
    }).catch(function () { msg.className = 'tl-nl-msg err'; msg.textContent = 'Sorry, that didn’t work. Please try again.'; })
      .then(function () { btn.disabled = false; btn.textContent = 'Show my results'; });
  });
})();
</script>''' % ('"' + NL_URL + '"')

def page(name, path, h1, title, meta, main, js):
    extra = (GATEJS if GATE else NLJS) if NL_URL else ''
    build(name, path, main, f'New page: {h1}. Calculated in the browser; nothing is stored.', h1=h1,
          extra_css=TCSS, extra_js=js + extra, new_page={'title': title, 'meta': meta})

# =====================================================================================================================
# 1. Training zones
ZMAIN = hero('Free tool', 'Training Zones Calculator', 'Work out your cycling power zones from your FTP or a 20-minute test, and your heart-rate zones from your threshold heart rate.') + f'''

<section class="tl-sec">
  <div class="in">
    <div class="tl-box">
      <form class="tl-in panel" id="tl-zones" onsubmit="return false">
        <h2>Your numbers</h2>
        <fieldset class="tl-f"><legend>I know</legend>
          <div class="tl-seg"><label><input type="radio" name="src" value="ftp" checked>My FTP</label><label><input type="radio" name="src" value="t20">A 20-min test</label></div>
        </fieldset>
        <label class="tl-f"><span id="tl-p-lab">FTP (watts)</span><input type="number" id="tl-p" inputmode="numeric" min="50" max="600" placeholder="e.g. 250"><small id="tl-p-help">Your Functional Threshold Power.</small></label>
        <div class="tl-two">
          <label class="tl-f"><span>Threshold HR (bpm)</span><input type="number" id="tl-hr" inputmode="numeric" min="100" max="220" placeholder="optional"></label>
          <label class="tl-f"><span>Weight (kg)</span><input type="number" id="tl-kg" inputmode="decimal" min="30" max="160" step="0.1" placeholder="optional"></label>
        </div>
        <p class="tl-note">Threshold heart rate is your average heart rate for the last 20 minutes of a 30-minute solo all-out effort. Leave it empty if you don't know it.</p>
      </form>
      <div class="tl-out panel" aria-live="polite">
        <h2>Your zones</h2>
        {gate()}<div id="tl-zones-out"><p class="tl-empty">Enter your FTP or 20-minute power to see your zones.</p></div>
      </div>
    </div>
    {signup('zones')}
  </div>
</section>

<section>
  <div class="in"><div class="tl-txt">
    <div class="eyebrow">How it works</div>
    <h2>HOW TO USE YOUR TRAINING ZONES</h2>
    <div class="bar"></div>
    <p>Training zones turn one number, your FTP, into clear targets for every session. Riding in the right zone makes sure an easy day is really easy and a hard day is hard enough to make you faster.</p>
    <h3>Power zones</h3>
    <p>These are the classic 7 power zones, each a percentage of your FTP. If you did a 20-minute test, your FTP is 95% of your average power for the 20 minutes.</p>
    <ul>
      <li><b>Zones 1–2:</b> recovery and endurance. Most of your weekly riding, building your aerobic base.</li>
      <li><b>Zone 3:</b> tempo. Steady and controlled, useful in long efforts and Gran Fondo pacing.</li>
      <li><b>Zone 4:</b> threshold. Intervals that raise your FTP.</li>
      <li><b>Zones 5–7:</b> VO2max, anaerobic and sprint. Short, very hard efforts.</li>
    </ul>
    <h3>Heart-rate zones</h3>
    <p>Heart rate reacts slowly and drifts with heat, tiredness and caffeine, so use it alongside power, or on its own if you don't have a power meter.</p>
    <h3>Keep your zones up to date</h3>
    <p>Your zones change as you get fitter. Re-test every 6 to 8 weeks. Our coached riders get adaptive zones that change every week, and testing with Critical Power or INSCYD, which goes beyond FTP.</p>
    {reads([('what-is-ftp-cycling', 'What is FTP in cycling?'), ('zone-2-training', 'The power of Zone 2 training'), ('zone-2-isnt-easy', 'Zone 2 isn’t easy')])}
  </div></div>
</section>

{cta('These zones are a starting point. With coaching, your zones adapt every week to your training and your plan is built around your goals and your time.')}

{more_tools('zones')}'''

ZJS = '''<script>
(function () {
  var f = document.getElementById('tl-zones'), out = document.getElementById('tl-zones-out');
  var P = [['1', 'Active recovery', 0, .55, '#6b7280'], ['2', 'Endurance', .56, .75, '#3b82f6'], ['3', 'Tempo', .76, .90, '#22c55e'], ['4', 'Threshold', .91, 1.05, '#eab308'],
           ['5', 'VO2max', 1.06, 1.20, '#f97316'], ['6', 'Anaerobic capacity', 1.21, 1.50, '#ef4444'], ['7', 'Neuromuscular power', 1.51, 0, '#a855f7']];
  var H = [['1', 'Recovery', 0, .81], ['2', 'Aerobic', .81, .89], ['3', 'Tempo', .90, .93], ['4', 'Sub-threshold', .94, .99], ['5a', 'Super-threshold', 1.00, 1.02], ['5b', 'Aerobic capacity', 1.03, 1.06], ['5c', 'Anaerobic capacity', 1.07, 0]];
  function num(id) { var v = parseFloat(document.getElementById(id).value); return isFinite(v) ? v : 0; }
  /* zones join up: each one starts 1 above the previous zone's top, so no watt or beat falls between two zones */
  function rows(x, Z) { var prev = 0; return Z.map(function (z) { var top = z[3] ? Math.round(x * z[3]) : 0, s = z[2] === 0 ? 'up to ' + top : (top ? (prev + 1) + '–' + top : (prev + 1) + '+'); prev = top; return s; }); }
  function pct(lo, hi) { return lo === 0 ? '< ' + Math.round(hi * 100) + '%' : (hi === 0 ? '> ' + Math.round(lo * 100 - 1) + '%' : Math.round(lo * 100) + '–' + Math.round(hi * 100) + '%'); }
  function run() {
    var t20 = f.querySelector('input[name=src]:checked').value === 't20';
    document.getElementById('tl-p-lab').textContent = t20 ? '20-min average power (watts)' : 'FTP (watts)';
    document.getElementById('tl-p-help').textContent = t20 ? 'Your FTP will be 95% of this.' : 'Your Functional Threshold Power.';
    var p = num('tl-p'), hr = num('tl-hr'), kg = num('tl-kg');
    if (p < 50 || p > 700) { out.innerHTML = '<p class="tl-empty">Enter your ' + (t20 ? '20-minute power' : 'FTP') + ' (50–700 W) to see your zones.</p>'; return; }
    var ftp = t20 ? p * 0.95 : p, h = '<div class="tl-big"><div><b>' + Math.round(ftp) + ' W</b><span>FTP</span></div>';
    if (kg >= 30 && kg <= 160) h += '<div><b>' + (ftp / kg).toFixed(2) + '</b><span>W/kg</span></div>';
    h += '</div><table class="tl-tbl"><caption>Power zones</caption><thead><tr><th scope="col">Zone</th><th scope="col">% FTP</th><th scope="col">Watts</th></tr></thead><tbody>';
    var pw = rows(ftp, P); P.forEach(function (z, i) { h += '<tr><th scope="row"><span class="tl-z" style="background:' + z[4] + '"></span>Z' + z[0] + ' ' + z[1] + '</th><td>' + pct(z[2], z[3]) + '</td><td>' + pw[i] + ' W</td></tr>'; });
    h += '</tbody></table>';
    if (hr >= 100 && hr <= 220) {
      h += '<table class="tl-tbl"><caption>Heart-rate zones</caption><thead><tr><th scope="col">Zone</th><th scope="col">% threshold HR</th><th scope="col">bpm</th></tr></thead><tbody>';
      var hz = rows(hr, H); H.forEach(function (z, i) { h += '<tr><th scope="row">Z' + z[0] + ' ' + z[1] + '</th><td>' + pct(z[2], z[3]) + '</td><td>' + hz[i] + '</td></tr>'; });
      h += '</tbody></table>';
    }
    out.innerHTML = h + '<p class="tl-note">Power zones: the 7-zone model based on FTP. Heart-rate zones: based on threshold heart rate. A guide, not medical advice.</p>';
  }
  f.addEventListener('input', run); f.addEventListener('change', run); run();
})();
</script>'''

# =====================================================================================================================
# 2. Carbs per hour
CMAIN = hero('Free tool', 'Carbs per Hour Calculator', 'How many grams of carbohydrate to take each hour on the bike, and what that means in gels and bottles, for your ride length and intensity.') + f'''

<section class="tl-sec">
  <div class="in">
    <div class="tl-box">
      <form class="tl-in panel" id="tl-carbs" onsubmit="return false">
        <h2>Your ride</h2>
        <div class="tl-two">
          <label class="tl-f"><span>Hours</span><select id="tl-h">{''.join(f'<option value="{i}"{" selected" if i == 2 else ""}>{i}</option>' for i in range(0, 13))}</select></label>
          <label class="tl-f"><span>Minutes</span><select id="tl-m">{''.join(f'<option value="{i}"{" selected" if i == 30 else ""}>{i:02d}</option>' for i in range(0, 60, 15))}</select></label>
        </div>
        <label class="tl-f"><span>Intensity</span><select id="tl-i">
          <option value="0">Easy / recovery ride</option><option value="1" selected>Endurance ride (Zone 2)</option>
          <option value="2">Tempo, sweet spot or group ride</option><option value="3">Race, sportive or Gran Fondo</option></select></label>
        <label class="tl-check"><input type="checkbox" id="tl-gut"> My gut is trained to take a lot of carbs (I regularly take 80 g/h or more)</label>
        <div class="tl-two">
          <label class="tl-f"><span>Carbs per gel (g)</span><input type="number" id="tl-gel" inputmode="numeric" min="10" max="60" value="25"></label>
          <label class="tl-f"><span>Carbs per bottle (g)</span><input type="number" id="tl-bot" inputmode="numeric" min="0" max="120" value="40"><small>0 if you only drink water</small></label>
        </div>
      </form>
      <div class="tl-out panel" aria-live="polite">
        <h2>Your fuelling plan</h2>
        {gate()}<div id="tl-carbs-out"></div>
      </div>
    </div>
    {signup('carbs')}
  </div>
</section>

<section>
  <div class="in"><div class="tl-txt">
    <div class="eyebrow">How it works</div>
    <h2>HOW MUCH TO EAT ON THE BIKE</h2>
    <div class="bar"></div>
    <p>Carbohydrate is your main fuel at higher intensities. Your body only stores enough for a couple of hours of hard riding, so on longer or harder rides you need to top it up as you go, before you feel hungry or empty.</p>
    <h3>The rule of thumb</h3>
    <ul>
      <li><b>Under 1 hour:</b> water is usually enough; for a hard session a small amount of carbs helps.</li>
      <li><b>1 to 2.5 hours:</b> around 30–60 g per hour, more as the intensity goes up.</li>
      <li><b>Over 2.5 hours:</b> 60–90 g per hour, and up to 100–120 g for riders who have trained their gut.</li>
    </ul>
    <h3>Train your gut</h3>
    <p>Your gut can learn to absorb more carbs. Practise your race fuelling in training, starting lower and building up over a few weeks, and never try something new on race day. Products that mix glucose and fructose are absorbed better at high amounts.</p>
    <h3>Don't forget to drink</h3>
    <p>Most riders need around 500–750 ml of fluid per hour, more in the heat. Bottles with carbs and electrolytes help you cover both.</p>
    {reads([('effective-fuelling-techniques-for-winter-training', 'Fuelling for winter training'), ('homemade-sports-drinks', 'Homemade sports drinks'), ('hydration-tips', 'Hydration tips'), ('diet-of-a-cyclist', 'Diet of a cyclist')])}
  </div></div>
</section>

{cta('Our Advanced and Premium riders get carbs recommendations for every session, and a nutritional consult with our sports nutritionist.')}

{more_tools('carbs')}'''

CJS = '''<script>
(function () {
  var f = document.getElementById('tl-carbs'), out = document.getElementById('tl-carbs-out');
  /* g/h by ride length (under 1h, 1-1.5h, 1.5-2.5h, over 2.5h) and intensity (easy, endurance, tempo, race) */
  var T = [[0, 0, 20, 30], [0, 30, 45, 60], [30, 45, 60, 75], [40, 60, 75, 90]];
  function v(id) { var x = parseFloat(document.getElementById(id).value); return isFinite(x) ? x : 0; }
  function run() {
    var min = v('tl-h') * 60 + v('tl-m'), it = v('tl-i'), gut = document.getElementById('tl-gut').checked, gel = v('tl-gel') || 25, bot = Math.max(0, v('tl-bot'));
    if (min < 15) { out.innerHTML = '<p class="tl-empty">Choose how long your ride is.</p>'; return; }
    var row = min < 60 ? 0 : min < 90 ? 1 : min <= 150 ? 2 : 3, g = T[row][it];
    if (gut && min >= 90 && it >= 2) g = Math.min(120, g + 20);
    var hrs = min / 60, total = Math.round(g * hrs / 5) * 5, h = '<div class="tl-big"><div><b>' + g + ' g</b><span>Carbs per hour</span></div><div><b>' + total + ' g</b><span>For the whole ride</span></div></div>';
    if (g === 0) {
      h += '<p class="tl-note">For this ride, water is enough. Make sure you eat a normal meal with carbs 2–3 hours before, and eat well after.</p>';
    } else {
      var fromBot = Math.min(g, bot), gels = Math.max(0, (g - fromBot) / gel);
      h += '<table class="tl-tbl"><caption>Each hour</caption><tbody>';
      if (bot > 0) h += '<tr><th scope="row">Bottle with ' + bot + ' g carbs</th><td>' + (fromBot >= bot ? '1 bottle' : Math.round(fromBot / bot * 10) / 10 + ' bottle') + '</td></tr>';
      h += '<tr><th scope="row">Gels of ' + gel + ' g' + (bot > 0 ? ' (on top)' : '') + '</th><td>' + (Math.round(gels * 2) / 2 === 0 ? (gels > 0 ? 'a few bites of a bar' : 'none') : (Math.round(gels * 2) / 2) + ' gel' + (gels > 1.25 ? 's' : '')) + '</td></tr>';
      h += '<tr><th scope="row">Little and often</th><td>~' + Math.round(g / 3) + ' g every 20 min</td></tr>';
      h += '<tr><th scope="row">Fluid</th><td>500–750 ml</td></tr></tbody></table>';
      h += '<p class="tl-note">Start eating in the first 20–30 minutes, before you feel hungry. Bars, rice cakes and bananas count too: check the grams of carbohydrate on the pack.</p>';
    }
    out.innerHTML = h + '<p class="tl-note" style="margin-top:10px">A general guide for healthy adults, not medical advice.</p>';
  }
  f.addEventListener('input', run); f.addEventListener('change', run); run();
})();
</script>'''

# =====================================================================================================================
# 3. Critical Power & W'
PMAIN = hero('Free tool', 'Critical Power &amp; W′ Calculator', 'Enter two or three all-out efforts to get your Critical Power and W′ (W prime), and see the power you can hold for any effort from 2 to 20 minutes.') + f'''

<section class="tl-sec">
  <div class="in">
    <div class="tl-box">
      <form class="tl-in panel" id="tl-cp" onsubmit="return false">
        <h2>Your two efforts</h2>
        <div class="tl-two">
          <label class="tl-f"><span>Effort 1 (minutes)</span><input type="number" id="tl-t1" inputmode="decimal" min="2" max="20" step="0.5" value="3"></label>
          <label class="tl-f"><span>Average power (W)</span><input type="number" id="tl-p1" inputmode="numeric" min="50" max="1200" placeholder="e.g. 380"></label>
        </div>
        <div class="tl-two">
          <label class="tl-f"><span>Effort 2 (minutes)</span><input type="number" id="tl-t2" inputmode="decimal" min="3" max="30" step="0.5" value="12"></label>
          <label class="tl-f"><span>Average power (W)</span><input type="number" id="tl-p2" inputmode="numeric" min="50" max="1000" placeholder="e.g. 290"></label>
        </div>
        <div class="tl-two">
          <label class="tl-f"><span>Effort 3 (optional, min)</span><input type="number" id="tl-t3" inputmode="decimal" min="2" max="30" step="0.5" placeholder="e.g. 7"></label>
          <label class="tl-f"><span>Average power (W)</span><input type="number" id="tl-p3" inputmode="numeric" min="50" max="1200" placeholder="optional"></label>
        </div>
        <label class="tl-f"><span>Weight (kg)</span><input type="number" id="tl-cpkg" inputmode="decimal" min="30" max="160" step="0.1" placeholder="optional"></label>
        <p class="tl-note">Use maximal efforts, fully paced, ideally on the same day with at least 30 minutes easy riding between them, or on fresh days. 3 and 12 minutes work well; a third effort (for example 7 minutes) makes the result more reliable.</p>
      </form>
      <div class="tl-out panel" aria-live="polite">
        <h2>Your results</h2>
        {gate()}<div id="tl-cp-out"></div>
      </div>
    </div>
    {signup('cp')}
  </div>
</section>

<section>
  <div class="in"><div class="tl-txt">
    <div class="eyebrow">How it works</div>
    <h2>WHAT CRITICAL POWER AND W′ TELL YOU</h2>
    <div class="bar"></div>
    <p><b>Critical Power (CP)</b> is the highest power you can sustain for a long time without your fatigue running away. It sits close to your FTP, but it comes from more than one effort, so it describes you better.</p>
    <p><b>W′ (W prime)</b> is your energy above Critical Power, in kilojoules: a battery you use every time you go over CP, in an attack, a climb or a sprint, and that recharges when you ride below it. Two riders with the same CP can race very differently because of their W′.</p>
    <h3>How the calculation works</h3>
    <p>The work you do in each effort is power × time. Plotting work against time for your efforts gives a straight line: its slope is your Critical Power and the point where it starts is your W′. From those two numbers we can predict your best power for any effort from about 2 to 20 minutes.</p>
    <h3>Get reliable numbers</h3>
    <p>The result is only as good as your efforts: they must be truly all-out and well paced. Our coaching uses Critical Power and W′ with Vekta to set your training zones and track your fatigue.</p>
    {reads([('critical-power', 'What is Critical Power?'), ('w-prime', 'What is W Prime?'), ('critical-power-testing', 'Critical Power testing: how to get reliable data')])}
  </div></div>
</section>

{cta('With coaching, your Critical Power and W′ are tracked in Vekta and every session is built on them.')}

{more_tools('cp')}'''

PJS = '''<script>
(function () {
  var f = document.getElementById('tl-cp'), out = document.getElementById('tl-cp-out');
  function v(id) { var x = parseFloat(document.getElementById(id).value); return isFinite(x) ? x : 0; }
  function mmss(s) { s = Math.round(s); return Math.floor(s / 60) + ':' + ('0' + s % 60).slice(-2); }
  function run() {
    var kg = v('tl-cpkg'), E = [[v('tl-t1') * 60, v('tl-p1')], [v('tl-t2') * 60, v('tl-p2')], [v('tl-t3') * 60, v('tl-p3')]].filter(function (e) { return e[0] > 0 && e[1] > 0; });
    if (E.length < 2) { out.innerHTML = '<p class="tl-empty">Enter the duration and average power of at least two efforts.</p>'; return; }
    E.sort(function (a, b) { return a[0] - b[0]; });
    for (var i = 0; i < E.length; i++) {
      if (E[i][0] < 120 || E[i][0] > 1800) { out.innerHTML = '<p class="tl-err">Use efforts between 2 and 30 minutes.</p>'; return; }
      if (i && (E[i][0] === E[i - 1][0] || E[i][1] >= E[i - 1][1])) { out.innerHTML = '<p class="tl-err">Each longer effort should have a lower power than the shorter ones, and the durations should be different. Check your numbers.</p>'; return; }
    }
    /* work = CP x time + W': a straight line through the efforts (least squares when there are 3) */
    var n = E.length, sx = 0, sy = 0, sxx = 0, sxy = 0;
    E.forEach(function (e) { var x = e[0], y = e[0] * e[1]; sx += x; sy += y; sxx += x * x; sxy += x * y; });
    var cp = (n * sxy - sx * sy) / (n * sxx - sx * sx), w = (sy - cp * sx) / n;
    if (cp <= 0 || w <= 0) { out.innerHTML = '<p class="tl-err">These numbers don’t give a valid result. Check both efforts were all-out.</p>'; return; }
    var h = '<div class="tl-big"><div><b>' + Math.round(cp) + ' W</b><span>Critical Power</span></div><div><b>' + (w / 1000).toFixed(1) + ' kJ</b><span>W′</span></div>';
    if (kg >= 30 && kg <= 160) h += '<div><b>' + (cp / kg).toFixed(2) + '</b><span>CP W/kg</span></div>';
    h += '</div><table class="tl-tbl"><caption>Your predicted best power</caption><thead><tr><th scope="col">Effort</th><th scope="col">Watts</th></tr></thead><tbody>';
    [2, 3, 5, 8, 10, 12, 15, 20].forEach(function (m) { h += '<tr><th scope="row">' + m + ' min</th><td>' + Math.round(cp + w / (m * 60)) + ' W</td></tr>'; });
    h += '</tbody></table><table class="tl-tbl"><caption>How long your W′ lasts</caption><thead><tr><th scope="col">Riding at</th><th scope="col">Time</th></tr></thead><tbody>';
    [1.05, 1.1, 1.2, 1.3].forEach(function (k) { h += '<tr><th scope="row">' + Math.round(cp * k) + ' W (' + Math.round(k * 100) + '% of CP)</th><td>' + mmss(w / (cp * k - cp)) + '</td></tr>'; });
    out.innerHTML = h + '</tbody></table><p class="tl-note">2-parameter Critical Power model, from ' + n + ' efforts. Most accurate for efforts between about 2 and 20 minutes.</p>';
  }
  f.addEventListener('input', run); run();
})();
</script>'''

# =====================================================================================================================
# 4. Climb time
# Famous climbs: distance (km), average gradient (%), summit altitude (m). Commonly published figures for the classic sides;
# the time uses the average gradient, so real climbs with steeper ramps take a little longer.
CLIMBS = [
    ('Stelvio (from Prato)', 24.3, 7.4, 2758),
    ('Mortirolo (from Mazzo)', 12.4, 10.5, 1852),
    ('Passo Giau (from Selva)', 9.9, 9.3, 2236),
    ('Alpe d’Huez', 13.8, 8.1, 1850),
    ('Mont Ventoux (from Bédoin)', 21.5, 7.5, 1910),
    ('Tourmalet (from Luz)', 19.0, 7.4, 2115),
    ('Sa Calobra (Mallorca)', 9.4, 7.1, 682),
]
copts = ''.join(f'<option value="{d},{g},{top}">{E(n)} · {d} km, {g}%</option>' for n, d, g, top in CLIMBS)
CLMAIN = hero('Free tool', 'Climb Time Calculator', 'How long will a climb take you? Enter your weight and power to get your time on the Stelvio, Alpe d’Huez, Ventoux or your own climb, and the power you need for a target time.') + f"""

<section class="tl-sec">
  <div class="in">
    <div class="tl-box">
      <form class="tl-in panel" id="tl-climb" onsubmit="return false">
        <h2>You and the climb</h2>
        <label class="tl-f"><span>Climb</span><select id="tl-c">{copts}<option value="custom">My own climb…</option></select></label>
        <div class="tl-two tl-custom" hidden>
          <label class="tl-f"><span>Distance (km)</span><input type="number" id="tl-cd" inputmode="decimal" min="0.5" max="60" step="0.1" placeholder="e.g. 8"></label>
          <label class="tl-f"><span>Avg gradient (%)</span><input type="number" id="tl-cg" inputmode="decimal" min="1" max="20" step="0.1" placeholder="e.g. 6.5"></label>
        </div>
        <div class="tl-two">
          <label class="tl-f"><span>Your weight (kg)</span><input type="number" id="tl-rw" inputmode="decimal" min="35" max="150" step="0.1" placeholder="e.g. 72"></label>
          <label class="tl-f"><span>Bike + kit (kg)</span><input type="number" id="tl-bw" inputmode="decimal" min="5" max="25" step="0.1" value="9"></label>
        </div>
        <div class="tl-two">
          <label class="tl-f"><span>Your power (W)</span><input type="number" id="tl-pw" inputmode="numeric" min="50" max="600" placeholder="e.g. 250"><small>Power you can hold for the climb</small></label>
          <label class="tl-f"><span>Target time (min)</span><input type="number" id="tl-tt" inputmode="numeric" min="5" max="400" placeholder="optional"><small>Power needed for it</small></label>
        </div>
      </form>
      <div class="tl-out panel" aria-live="polite">
        <h2>Your climb</h2>
        {gate()}<div id="tl-climb-out"></div>
      </div>
    </div>
    {signup('climb')}
  </div>
</section>

<section>
  <div class="in"><div class="tl-txt">
    <div class="eyebrow">How it works</div>
    <h2>HOW WE WORK OUT YOUR CLIMB TIME</h2>
    <div class="bar"></div>
    <p>On a climb, most of your power goes into lifting you and your bike against gravity, which is why watts per kilo matter so much. The rest goes into rolling resistance and, a little, the air.</p>
    <p>We use the standard cycling power equation: gravity, rolling resistance (good road tyres), air resistance for a rider on the hoods, and 2.5% lost in the drivetrain. Air is thinner higher up, so the summit altitude is taken into account.</p>
    <h3>Why your real time can differ</h3>
    <ul>
      <li><b>Steeper ramps:</b> the calculation uses the average gradient. Climbs with steep sections and flatter parts usually take a little longer.</li>
      <li><b>Pacing:</b> riding evenly is fastest. Going too hard at the bottom costs time at the top.</li>
      <li><b>Wind, heat and altitude:</b> above about 2,000 m, most riders can't hold their usual power.</li>
    </ul>
    <h3>Use it to plan</h3>
    <p>Enter a target time to see the power you need, then train for it. Your coach can build that target into your plan.</p>
    {reads([('how-to-improve-on-descents', 'How to improve on descents'), ('what-is-ftp-cycling', 'What is FTP in cycling?'), ('the-secrets-of-weight-loss', 'The secrets of weight loss')])}
  </div></div>
</section>

{cta('Want to ride the Stelvio or the Mortirolo faster? A plan built for your target climb, by a former pro who races them.')}

<section>
  <div class="in">
    <div class="tl-cta panel">
      <div><h3 class="h-sm">Ride these climbs with us</h3><p>Cigala Cycling Tours rides the Stelvio, the Dolomites, the Alps and the Pyrenees, with guides and support.</p></div>
      <div class="ctas"><a class="btn btn-ghost" href="{T}/" {EXT}>See the bike tours →</a></div>
    </div>
  </div>
</section>

{more_tools('climb')}"""

CLJS = """<script>
(function () {
  var f = document.getElementById('tl-climb'), out = document.getElementById('tl-climb-out'), sel = document.getElementById('tl-c'), cus = f.querySelector('.tl-custom');
  var G = 9.81, CRR = 0.004, CDA = 0.40, EFF = 0.975;
  function v(id) { var x = parseFloat(document.getElementById(id).value); return isFinite(x) ? x : 0; }
  function hms(s) { s = Math.round(s); var h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = s % 60; return (h ? h + ':' + ('0' + m).slice(-2) : m) + ':' + ('0' + x).slice(-2); }
  /* wheel power needed at speed u (m/s) on gradient gr, total mass m, air density rho */
  function need(u, m, gr, rho) { var th = Math.atan(gr); return (m * G * (Math.sin(th) + CRR * Math.cos(th)) * u + 0.5 * rho * CDA * u * u * u) / EFF; }
  function speed(P, m, gr, rho) { var lo = 0.1, hi = 30; for (var i = 0; i < 60; i++) { var mid = (lo + hi) / 2; if (need(mid, m, gr, rho) > P) hi = mid; else lo = mid; } return (lo + hi) / 2; }
  function run() {
    var c = sel.value, d, gp, top;
    cus.hidden = c !== 'custom';
    if (c === 'custom') { d = v('tl-cd'); gp = v('tl-cg'); top = 0; } else { c = c.split(','); d = +c[0]; gp = +c[1]; top = +c[2]; }
    var rw = v('tl-rw'), bw = v('tl-bw') || 9, P = v('tl-pw'), tt = v('tl-tt');
    if (!(d > 0) || !(gp > 0)) { out.innerHTML = '<p class="tl-empty">Enter the distance and average gradient of your climb.</p>'; return; }
    if (rw < 35 || rw > 150) { out.innerHTML = '<p class="tl-empty">Enter your weight, then your power or a target time.</p>'; return; }
    if (!P && !tt) { out.innerHTML = '<p class="tl-empty">Enter the power you can hold, or a target time.</p>'; return; }
    var m = rw + bw, gr = gp / 100, gain = d * 1000 * gr, mid = Math.max(0, top - gain / 2), rho = 1.225 * Math.exp(-mid / 8500), h = '';
    if (P) {
      var u = speed(P, m, gr, rho), t = d * 1000 / u;
      h += '<div class="tl-big"><div><b>' + hms(t) + '</b><span>Your time</span></div><div><b>' + (P / rw).toFixed(2) + '</b><span>W/kg</span></div></div>';
      h += '<table class="tl-tbl"><tbody><tr><th scope="row">Average speed</th><td>' + (u * 3.6).toFixed(1) + ' km/h</td></tr>';
      h += '<tr><th scope="row">Climbing speed (VAM)</th><td>' + Math.round(gain / t * 3600) + ' m/h</td></tr>';
      h += '<tr><th scope="row">Elevation gain</th><td>' + Math.round(gain) + ' m</td></tr></tbody></table>';
      h += '<table class="tl-tbl"><caption>At other powers</caption><thead><tr><th scope="col">Power</th><th scope="col">Time</th></tr></thead><tbody>';
      [-30, -15, 15, 30].forEach(function (k) { var q = P + k; if (q > 40) h += '<tr><th scope="row">' + q + ' W (' + (q / rw).toFixed(1) + ' W/kg)</th><td>' + hms(d * 1000 / speed(q, m, gr, rho)) + '</td></tr>'; });
      h += '</tbody></table>';
    }
    if (tt) {
      var ut = d * 1000 / (tt * 60), pn = need(ut, m, gr, rho);
      h += '<div class="tl-big"><div><b>' + Math.round(pn) + ' W</b><span>For ' + hms(tt * 60) + '</span></div><div><b>' + (pn / rw).toFixed(2) + '</b><span>W/kg needed</span></div></div>';
    }
    out.innerHTML = h + '<p class="tl-note">Average gradient, good road tyres, rider on the hoods, no wind. A guide: real climbs with steeper ramps take a little longer.</p>';
  }
  f.addEventListener('input', run); f.addEventListener('change', run); run();
})();
</script>"""

# =====================================================================================================================
# 5. Sweat rate
SWMAIN = hero('Free tool', 'Sweat Rate Calculator', 'Weigh yourself before and after a ride to find out how much you sweat per hour, and how much you should drink on your next ride.') + f"""

<section class="tl-sec">
  <div class="in">
    <div class="tl-box">
      <form class="tl-in panel" id="tl-sweat" onsubmit="return false">
        <h2>Your ride</h2>
        <div class="tl-two">
          <label class="tl-f"><span>Weight before (kg)</span><input type="number" id="tl-w0" inputmode="decimal" min="35" max="150" step="0.1" placeholder="e.g. 72.4"></label>
          <label class="tl-f"><span>Weight after (kg)</span><input type="number" id="tl-w1" inputmode="decimal" min="35" max="150" step="0.1" placeholder="e.g. 71.3"></label>
        </div>
        <div class="tl-two">
          <label class="tl-f"><span>Drank during (ml)</span><input type="number" id="tl-dr" inputmode="numeric" min="0" max="10000" step="50" placeholder="e.g. 1000"><small>A standard bottle is 500–750 ml</small></label>
          <label class="tl-f"><span>Toilet stops (ml)</span><input type="number" id="tl-ur" inputmode="numeric" min="0" max="3000" step="50" value="0"><small>Rough guess, or 0</small></label>
        </div>
        <div class="tl-two">
          <label class="tl-f"><span>Ride time: hours</span><select id="tl-sh">{''.join(f'<option value="{i}"{" selected" if i == 1 else ""}>{i}</option>' for i in range(0, 9))}</select></label>
          <label class="tl-f"><span>Minutes</span><select id="tl-sm">{''.join(f'<option value="{i}">{i:02d}</option>' for i in range(0, 60, 5))}</select></label>
        </div>
        <p class="tl-note">Weigh yourself with no clothes (or the same dry clothes) just before and just after the ride, after towelling off. A ride of about an hour at your usual effort works best.</p>
      </form>
      <div class="tl-out panel" aria-live="polite">
        <h2>Your sweat rate</h2>
        {gate()}<div id="tl-sweat-out"></div>
      </div>
    </div>
    {signup('sweat')}
  </div>
</section>

<section>
  <div class="in"><div class="tl-txt">
    <div class="eyebrow">How it works</div>
    <h2>WHY YOUR SWEAT RATE MATTERS</h2>
    <div class="bar"></div>
    <p>Everyone sweats differently: from under half a litre to more than two litres an hour. Generic advice like “one bottle per hour” can leave one rider short and another drinking far too much. Your own number takes the guesswork away.</p>
    <h3>The calculation</h3>
    <p>Fluid lost = weight before − weight after + what you drank − what you passed. One kilo of body weight lost is about one litre of sweat. Divide by the ride time to get your sweat rate per hour.</p>
    <h3>How much to drink</h3>
    <p>Aim to lose no more than about 2% of your body weight on a ride: beyond that, performance starts to drop. You don't need to replace every drop, and you should never finish a ride heavier than you started: that means you drank too much.</p>
    <h3>Test in different conditions</h3>
    <p>Your sweat rate rises in the heat and at higher intensity. Test on a cool day and a hot day, and at an easy and a hard effort, and you'll know what to drink for any ride. Hot rides also need more salt (sodium) in your bottles.</p>
    {reads([('hydration-tips', 'Hydration tips'), ('why-is-hydration-vital-to-optimise-athletic-performance-2', 'Why hydration is vital for performance'), ('heat-training', 'Heat training'), ('homemade-sports-drinks', 'Homemade sports drinks')])}
  </div></div>
</section>

{cta('Our Advanced and Premium riders get fuelling and hydration advice for every session, and a nutritional consult with our sports nutritionist.')}

{more_tools('sweat')}"""

SWJS = """<script>
(function () {
  var f = document.getElementById('tl-sweat'), out = document.getElementById('tl-sweat-out');
  function v(id) { var x = parseFloat(document.getElementById(id).value); return isFinite(x) ? x : 0; }
  function ml(x) { return (Math.round(x / 50) * 50).toLocaleString('en-IE') + ' ml'; }
  function run() {
    var w0 = v('tl-w0'), w1 = v('tl-w1'), dr = v('tl-dr'), ur = v('tl-ur'), h = (v('tl-sh') * 60 + v('tl-sm')) / 60;
    if (w0 < 35 || w1 < 35) { out.innerHTML = '<p class="tl-empty">Enter your weight before and after the ride.</p>'; return; }
    if (h < 0.25) { out.innerHTML = '<p class="tl-empty">Choose how long the ride was (at least 15 minutes).</p>'; return; }
    var lost = (w0 - w1) * 1000 + dr - ur;   /* ml: 1 kg = about 1 litre */
    if (Math.abs(w0 - w1) > 5 || lost < 0) { out.innerHTML = '<p class="tl-err">These numbers don’t add up. Check the weights and the amount you drank.</p>'; return; }
    var rate = lost / h, pct = (w0 - w1) / w0 * 100, keep = Math.max(0, (lost - 0.02 * w0 * 1000) / h);
    var o = '<div class="tl-big"><div><b>' + ml(rate) + '</b><span>Sweat per hour</span></div><div><b>' + pct.toFixed(1) + '%</b><span>Body weight lost</span></div></div>';
    o += '<table class="tl-tbl"><tbody><tr><th scope="row">Total sweat on this ride</th><td>' + ml(lost) + '</td></tr>';
    o += '<tr><th scope="row">To stay under 2% loss on a ride like this</th><td>at least ' + ml(keep) + ' per hour</td></tr>';
    o += '<tr><th scope="row">Upper limit (don’t drink more than you sweat)</th><td>' + ml(rate) + ' per hour</td></tr></tbody></table>';
    var msg = pct > 2 ? 'You lost more than 2% of your body weight: next time drink more, especially in the heat.' : (w1 > w0 ? 'You finished heavier than you started: you drank more than you needed.' : 'You stayed under 2%: well done, your drinking was about right for this ride.');
    out.innerHTML = o + '<p class="tl-note">' + msg + ' One ride is a guide: your sweat rate changes with heat and intensity. Not medical advice.</p>';
  }
  f.addEventListener('input', run); f.addEventListener('change', run); run();
})();
</script>"""

# =====================================================================================================================
# 6. Swim pace (CSS)
def mmss_in(idp, label, mm, ss):
    return f"""<fieldset class="tl-f"><legend>{label}</legend><div class="tl-two">
          <label><span class="vh">{label} minutes</span><input type="number" id="{idp}m" inputmode="numeric" min="1" max="30" placeholder="{mm}" aria-label="{label}: minutes"></label>
          <label><span class="vh">{label} seconds</span><input type="number" id="{idp}s" inputmode="numeric" min="0" max="59" placeholder="{ss}" aria-label="{label}: seconds"></label>
        </div><small>minutes · seconds</small></fieldset>"""
CSSMAIN = hero('Free tool', 'Swim Pace (CSS) Calculator', 'For triathletes: find your Critical Swim Speed from a 400 m and a 200 m time trial, and the pace for every swim session.') + f"""

<section class="tl-sec">
  <div class="in">
    <div class="tl-box">
      <form class="tl-in panel" id="tl-css" onsubmit="return false">
        <h2>Your time trials</h2>
        {mmss_in('tl-a', '400 m time', '6', '40')}
        {mmss_in('tl-b', '200 m time', '3', '10')}
        <p class="tl-note">Warm up well, swim 400 m all-out but evenly paced, rest 5–10 minutes easy, then swim 200 m all-out. Use a pool and push off the wall to start (no dive).</p>
      </form>
      <div class="tl-out panel" aria-live="polite">
        <h2>Your swim paces</h2>
        {gate()}<div id="tl-css-out"></div>
      </div>
    </div>
    {signup('swim')}
  </div>
</section>

<section>
  <div class="in"><div class="tl-txt">
    <div class="eyebrow">How it works</div>
    <h2>WHAT IS CRITICAL SWIM SPEED?</h2>
    <div class="bar"></div>
    <p>Critical Swim Speed (CSS) is the fastest pace you can hold for a long swim without tiring quickly: the swimming version of your threshold. It's the most useful number for training in the pool, because it turns every session into a clear target pace per 100 m.</p>
    <h3>The calculation</h3>
    <p>CSS = (400 − 200) ÷ (400 m time − 200 m time). Using the difference between two efforts cancels out the push-offs and your sprint speed, so it reflects your real aerobic swimming. We show it as a pace per 100 m.</p>
    <h3>Using your paces</h3>
    <ul>
      <li><b>Easy:</b> warm-ups, drills and recovery.</li>
      <li><b>Endurance:</b> longer sets that build your aerobic base.</li>
      <li><b>Threshold (CSS):</b> sets like 8–10 × 100 m with short rests. The key session for faster triathlon swims.</li>
      <li><b>Fast:</b> short, hard repeats with longer rests.</li>
    </ul>
    <p>Re-test every 4–6 weeks: as your CSS gets faster, so do all your paces.</p>
  </div></div>
</section>

<section>
  <div class="in">
    <div class="tl-cta panel">
      <div><h3 class="h-sm">Triathlon coaching</h3><p>Swim, bike and run plans from Sprint to Ironman, with paces and zones set from your own testing.</p></div>
      <div class="ctas"><a class="btn btn-go" href="{C}/tri-individual-packages/" {EXT}>See the triathlon packages →</a><a class="btn btn-ghost" href="{CAL}" {EXT}>Book a free consultation</a></div>
    </div>
  </div>
</section>

{more_tools('swim')}"""

CSSJS = """<script>
(function () {
  var f = document.getElementById('tl-css'), out = document.getElementById('tl-css-out');
  function v(id) { var x = parseFloat(document.getElementById(id).value); return isFinite(x) ? x : 0; }
  function pace(s) { s = Math.round(s); return Math.floor(s / 60) + ':' + ('0' + s % 60).slice(-2); }
  function run() {
    var a = v('tl-am') * 60 + v('tl-as'), b = v('tl-bm') * 60 + v('tl-bs');
    if (!a || !b) { out.innerHTML = '<p class="tl-empty">Enter your 400 m and 200 m times.</p>'; return; }
    if (a <= b * 2) { out.innerHTML = '<p class="tl-err">Your 400 m should be slower per 100 m than your 200 m. Check both times.</p>'; return; }
    if (b < 100 || a > 1500) { out.innerHTML = '<p class="tl-err">Check your times: they look outside the usual range.</p>'; return; }
    var css = (a - b) / 2;   /* seconds per 100 m */
    var o = '<div class="tl-big"><div><b>' + pace(css) + '</b><span>CSS pace per 100 m</span></div><div><b>' + (100 / css).toFixed(2) + ' m/s</b><span>Critical Swim Speed</span></div></div>';
    o += '<table class="tl-tbl"><caption>Training paces per 100 m</caption><thead><tr><th scope="col">Session</th><th scope="col">Pace</th></tr></thead><tbody>';
    [['Easy', 10, 15], ['Endurance', 5, 8], ['Threshold (CSS)', -1, 2], ['Fast', -6, -3]].forEach(function (z) { o += '<tr><th scope="row">' + z[0] + '</th><td>' + pace(css + z[1]) + '–' + pace(css + z[2]) + '</td></tr>'; });
    o += '</tbody></table><table class="tl-tbl"><caption>At CSS pace</caption><tbody>';
    [[750, 'Sprint swim (750 m)'], [1500, 'Olympic swim (1,500 m)']].forEach(function (d) { o += '<tr><th scope="row">' + d[1] + '</th><td>' + pace(css * d[0] / 100) + '</td></tr>'; });
    out.innerHTML = o + '</tbody></table><p class="tl-note">Pool times. Open water, wetsuits and drafting change race pace. A guide for training.</p>';
  }
  f.addEventListener('input', run); run();
})();
</script>"""

# =====================================================================================================================
# hub
cards = ''.join(f'<a class="tl-card panel" href="{C}{u}" {EXT}><svg viewBox="0 0 24 24" aria-hidden="true">{IC[k]}</svg><h2 class="h-sm">{t}</h2><p>{d}</p><span class="arrow-link">Open the calculator →</span></a>' for k, u, t, d in TOOLS)
HMAIN = hero('Free tools', 'Free Cycling Training Tools', 'Free calculators from Head Coach Matteo Cigala to help you train and race smarter: training zones, fuelling, hydration, Critical Power, climb times and swim pace.') + f'''

<section class="tl-sec">
  <div class="in">
    <div class="tl-cards">{cards}</div>
    {signup('hub')}
  </div>
</section>

{cta('Our coaching takes these numbers further: a plan built around your goals, your time and your testing, with feedback from Matteo.')}'''

page('tools', '/tools/', 'Free Cycling Training Tools', 'Free Cycling Training Tools | Cigala Cycling Coaching',
     'Free cycling calculators from Cigala Cycling Coaching: training zones from FTP and heart rate, carbs per hour for your rides, and Critical Power and W′.', HMAIN, '')
page('tools-training-zones', '/tools/training-zones-calculator/', 'Training Zones Calculator', 'Cycling Training Zones Calculator (Power & Heart Rate) | Cigala Cycling Coaching',
     'Free cycling training zones calculator: your 7 power zones from FTP or a 20-minute test, and heart-rate zones from threshold heart rate, with W/kg.', ZMAIN, ZJS)
page('tools-carbs-per-hour', '/tools/carbs-per-hour-calculator/', 'Carbs per Hour Calculator', 'Carbs per Hour Calculator for Cycling | Cigala Cycling Coaching',
     'How many carbs per hour should you eat on the bike? Free fuelling calculator: grams per hour, gels and bottles for your ride length and intensity.', CMAIN, CJS)
page('tools-critical-power', '/tools/critical-power-calculator/', 'Critical Power & W′ Calculator', 'Critical Power & W Prime Calculator for Cycling | Cigala Cycling Coaching',
     'Free Critical Power and W′ (W prime) calculator: enter two all-out efforts to get your CP, W′ and predicted best power from 2 to 20 minutes.', PMAIN, PJS)
page('tools-climb-time', '/tools/climb-time-calculator/', 'Climb Time Calculator', 'Cycling Climb Time Calculator (Stelvio, Alpe d’Huez, Ventoux) | Cigala Cycling Coaching',
     'How long will a climb take you? Free cycling climb time calculator for the Stelvio, Alpe d’Huez, Ventoux or any climb, from your power and weight.', CLMAIN, CLJS)
page('tools-sweat-rate', '/tools/sweat-rate-calculator/', 'Sweat Rate Calculator', 'Sweat Rate Calculator for Cyclists | Cigala Cycling Coaching',
     'Free sweat rate calculator: weigh yourself before and after a ride to find how much you sweat per hour and how much to drink on the bike.', SWMAIN, SWJS)
page('tools-swim-pace', '/tools/swim-pace-calculator/', 'Swim Pace (CSS) Calculator', 'CSS Swim Pace Calculator for Triathletes | Cigala Cycling Coaching',
     'Free Critical Swim Speed (CSS) calculator: your CSS pace per 100 m from a 400 m and 200 m time trial, plus training paces for every swim session.', CSSMAIN, CSSJS)

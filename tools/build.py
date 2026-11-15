import re, html, os
S=__import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))) + '/'
OUT=S+'home/'
css=open(S+'brand.css').read()
header=open(S+'part_header.html').read(); footer=open(S+'part_footer.html').read(); home_main=open(S+'part_home_main.html').read()
LINKS={'https://cigalacycling.com/about/':'about.html','https://cigalacycling.com/contact/':'contact.html','https://cigalacycling.com/terms-conditions/':'terms.html','https://cigalacycling.com/privacy-policy/':'privacy.html','https://cigalacycling.com/':'./'}
def local(x):
    for k,v in LINKS.items():
        x=x.replace(f'href="{k}" target="_blank" rel="noopener"',f'href="{v}"')
    return x
header=local(header).replace(' aria-current="page"',''); footer=local(footer); home_main=local(home_main)
# footer phone format to match contact page
footer=footer.replace('+353 40478107','+353 404 78107'); home_main=home_main.replace('+353 40478107','+353 404 78107')
def hdr(cur):
    h=header
    if cur: h=h.replace(f'<a href="{cur}">',f'<a href="{cur}" aria-current="page">')
    return h
EXTRA='''
/* inner pages */
.hero .in.proof-wrap { display: block; padding-block: 0; }
.proof-mob { display: none; }
@media (max-width: 640px) { .hero .in.proof-wrap { display: none; } .proof-mob { display: block; } .proof-mob .proof { margin-top: 28px; } }
.proof { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); margin-top: 36px; border: 1px solid var(--border); border-radius: var(--r); background: var(--panel-grad), var(--panel); }
.proof > div { padding: 18px 20px; border-left: 1px solid var(--border); min-width: 0; }
.proof > div:first-child { border-left: 0; }
.proof b { display: block; font-family: var(--head); font-weight: 400; font-size: clamp(30px, 3.6vw, 44px); line-height: 1; color: var(--text); }
.proof span { display: block; margin-top: 8px; font-size: 11.5px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--text-3); }
@media (max-width: 640px) { .proof { grid-template-columns: repeat(2, minmax(0, 1fr)); } .proof > div:nth-child(3) { border-left: 0; } .proof > div:nth-child(n+3) { border-top: 1px solid var(--border); } }
.hero.page-hero .in { padding-block: 64px 8px; display: block; }
.page-hero h1 { font-size: clamp(44px, 7vw, 84px); }
.crumbs { font-size: 12.5px; color: var(--text-3); margin-bottom: 14px; }
.page-hero .eyebrow { margin-bottom: 10px; }
.crumbs a { color: var(--text-3); text-decoration: none; } .crumbs a:hover { color: #fff; }
.feature { display: grid; grid-template-columns: minmax(0, 6fr) minmax(0, 6fr); gap: clamp(24px, 5vw, 64px); align-items: center; }
.feature.flip > .ph { order: 2; }
.feature .ph { border-radius: var(--r); overflow: hidden; border: 1px solid var(--border); aspect-ratio: 4 / 3; max-width: 100%; }
.feature .ph img { width: 100%; height: 100%; object-fit: cover; }
.feature p { margin: 0 0 12px; max-width: 62ch; }
.feature .big { font-family: var(--head); text-transform: uppercase; color: var(--text); font-size: clamp(22px, 2.4vw, 28px); line-height: 1.25; letter-spacing: .015em; margin: 22px 0 18px; }
.list-places { display: grid; gap: 6px; margin: 4px 0 14px; padding: 0; list-style: none; }
.list-places li { padding-left: 16px; position: relative; }
.list-places li::before { content: ""; position: absolute; left: 0; top: .7em; width: 7px; height: 7px; border-radius: 50%; background: var(--red); }
.panel { background: var(--panel-grad), var(--panel); border: 1px solid var(--border); border-radius: var(--r); padding: clamp(20px, 3vw, 32px); min-width: 0; }
.contact-grid { display: grid; grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); gap: 16px; align-items: start; }
.form { display: grid; gap: 14px; }
.form label { font-size: 12px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--text-3); display: grid; gap: 6px; }
.form label i { color: var(--red-text); font-style: normal; }
.form input, .form textarea { font: 15px/1.5 var(--body); color: var(--text); background: rgba(8,9,10,.6); border: 1px solid var(--border-strong); border-radius: 8px; padding: 12px 14px; width: 100%; }
.form input:focus, .form textarea:focus { outline: none; border-color: var(--green); box-shadow: 0 0 0 3px var(--green-wash); }
.form textarea { min-height: 150px; resize: vertical; }
.form .btn { justify-self: start; }
.form .note { font-size: 13px; color: var(--green-text); min-height: 1.2em; margin: 0; }
.info { display: grid; gap: 16px; }
.info .row { display: grid; grid-template-columns: 44px minmax(0, 1fr); gap: 14px; align-items: center; }
.info .ic { width: 44px; height: 44px; border-radius: 10px; display: grid; place-items: center; background: var(--green-wash); border: 1px solid rgba(0,154,68,.35); }
.info .ic svg { width: 20px; height: 20px; fill: none; stroke: var(--green-text); stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
.info h2 { font-size: 15px; font-family: var(--body); font-weight: 600; letter-spacing: .1em; color: var(--text-3); }
.info h2::after { display: none; }
.info .val { color: var(--text); font-weight: 600; font-size: 17px; overflow-wrap: anywhere; }
.info .val a { text-decoration: none; }
.social { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.social a { font-size: 13px; font-weight: 600; text-decoration: none; color: var(--text); border: 1px solid var(--border-strong); background: var(--wash); border-radius: 999px; padding: 7px 14px; }
.social a:hover { border-color: var(--green); }
.info .h2s { font-size: 15px; font-family: var(--body); font-weight: 600; letter-spacing: .1em; color: var(--text-3); text-transform: uppercase; margin: 0; }
.terms { display: grid; grid-template-columns: 240px minmax(0, 1fr); gap: 32px; align-items: start; }
.toc { position: sticky; top: calc(env(safe-area-inset-top, 0px) + 96px); display: grid; gap: 2px; font-size: 13px; }
.toc a { color: var(--text-3); text-decoration: none; padding: 5px 10px; border-left: 2px solid var(--border); }
.toc a:hover { color: #fff; border-left-color: var(--green); }
.toc b { font-size: 11px; letter-spacing: .1em; text-transform: uppercase; color: var(--text-3); margin: 0 0 8px; font-weight: 600; }
.legal-doc { display: grid; gap: 14px; }
.legal-doc ol { margin: 0; padding: 0; list-style: none; counter-reset: t; display: grid; gap: 14px; }
.legal-doc ol > li { counter-increment: t; }
.legal-doc h3 { font-size: 22px; display: flex; gap: 12px; align-items: baseline; scroll-margin-top: 100px; }
.legal-doc h3::before { content: counter(t, decimal-leading-zero); font-size: 14px; color: var(--red-text); font-family: var(--head); letter-spacing: .06em; }
.legal-doc p { margin: 10px 0 0; max-width: 72ch; overflow-wrap: anywhere; }
.legal-doc ul { margin: 8px 0 0; padding-left: 20px; max-width: 72ch; display: grid; gap: 4px; }
.legal-doc ul li::marker { color: var(--green); }
.legal-doc .waiver-head { margin-top: 28px; }
.legal-doc .waiver-head h2 { font-size: clamp(24px, 3vw, 34px); }
.legal-doc .waiver-head .provider { font-family: var(--body); text-transform: none; font-weight: 600; font-size: 15px; color: var(--text-2); letter-spacing: 0; margin-top: 14px; }
.legal-doc .provider::after { display: none; }
@media (max-width: 900px) {
  .feature, .feature.flip { grid-template-columns: minmax(0, 1fr); }
  .feature.flip > .ph { order: 0; }
  .contact-grid { grid-template-columns: minmax(0, 1fr); }
  .terms { grid-template-columns: minmax(0, 1fr); }
  .toc { position: static; display: none; }
}
'''
def page(title, cur, main, full=True):
    head=f'''<title>{title}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;500;600;700&display=swap">
<style>{css}{EXTRA}</style>'''
    ribbon='<div class="ribbon"><div class="in"><b>Design preview</b><span>A concept of cigalacycling.com in the Cigala Cycling brand. The menu moves between the preview pages; other links go to the live sites.</span></div></div>'
    body=f'<div class="topo" aria-hidden="true"></div>\n<div class="page">\n{ribbon}\n{hdr(cur)}\n{main}\n{footer}\n</div>'
    if full:
        return f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{body}\n<script>document.querySelectorAll("form.form").forEach(f=>f.addEventListener("submit",e=>{{e.preventDefault();f.querySelector(".note").textContent="Preview only: on the live site this sends your message to info@cigalacycling.com.";}}));</script>\n</body>\n</html>\n'
    return head+'\n'+body+'\n'
EXT='target="_blank" rel="noopener"'
# ---------- HOME
open(OUT+'index.html','w').write(page('Cigala Cycling Homepage','./',home_main,full=False))
# ---------- ABOUT
about=f'''
<div class="hero page-hero">
  <div class="in">
    <div class="crumbs"><a href="./">Home</a> / About</div>
    <div class="eyebrow">About Cigala Cycling</div>
    <h1>Our mission</h1>
    <div class="bar"></div>
    <p class="lede">Since its founding in 2016, Cigala Cycling’s mission is to bring all of the cyclist’s needs in one location and make them easily available at the consumer’s fingertips.</p>
    <p class="lede">Whether it is to help you improve your cycling &amp; triathlon abilities, to help you shop the right product or to provide you with the most unforgettable bike tour, Cigala Cycling has you covered.</p>
  </div>
</div>

<section>
  <div class="in feature">
    <div class="ph"><img src="img/coaching.jpg" alt="Three Cigala Cycling riders climbing a mountain road together" loading="lazy"></div>
    <div>
      <div class="eyebrow">Coaching</div>
      <h2>Cycling &amp; Triathlon Coaching</h2>
      <div class="bar"></div>
      <p class="big">Coaching is our CORE.<br>#TrainSmarterRideFaster is our vision.</p>
      <p>Cigala Cycling was founded by the Italian head coach Matteo Cigala when he moved to Ireland.</p>
      <p>A former pro cyclist with 28 years in the sport, Matteo combines sports science, racing experience and close links with professional teams to help riders of every level train smarter and ride faster.</p>
      <p>Cigala Cycling offers the highest level of cycling coaching and triathlon coaching.</p>
      <p>Individual coaching packages, sportive coaching packages and group coaching packages available.</p>
      <p>To date, Matteo has coached more than 1,000 athletes all over the world.</p>
      <div class="ctas"><a class="btn btn-go" href="https://coaching.cigalacycling.com/" {EXT}>Go to coaching site →</a></div>
    </div>
  </div>
</section>

<section>
  <div class="in feature flip">
    <div class="ph"><img src="img/tours.jpg" alt="Cigala Cycling Tours riders in white team jerseys celebrating on the coast in Cyprus" loading="lazy"></div>
    <div>
      <div class="eyebrow">Bike tours</div>
      <h2>Tours</h2>
      <div class="bar"></div>
      <p class="big">Memorable Adventures. New Friends. Shared Passion. Lifetime Experience.</p>
      <p>Cigala Cycling Tours provides fully supported road and gravel tours across Europe’s best cycling roads, in small groups led by former pros.</p>
      <p>For over a decade we have guided more than 700 cyclists on our tours.</p>
      <p>We ride in more than 20 destinations across Europe, from the Dolomites, the Alps and Tuscany to Sicily, Sardinia and Puglia, from the Pyrenees and Provence to the Algarve, and on to Slovenia, Croatia and Cyprus.</p>
      <p>Cigala Cycling Tours is the Official Tour Operator of the Maratona dles Dolomites, offers official event entry packages for the Gran Fondo Strade Bianche &amp; Gran Fondo Il Lombardia, and is an Official Event Partner of the Algarve Granfondo.</p>
      <div class="ctas"><a class="btn btn-go" href="https://tours.cigalacycling.com/" {EXT}>Go to tours site →</a></div>
    </div>
  </div>
</section>

<section>
  <div class="in feature">
    <div class="ph"><img src="img/retail.jpg" alt="Rider training on a Wahoo smart bike in front of a mountain backdrop" loading="lazy"></div>
    <div>
      <div class="eyebrow">Online shop</div>
      <h2>Retail Store</h2>
      <div class="bar"></div>
      <p class="big">Ireland’s #1 Online Cycling Store.</p>
      <p>Cigala Cycling Retail is a leading online Irish Retailer. On our store, you can find and shop a superb range of cycling and triathlon products.</p>
      <p>For 10 years, cyclists, triathletes and sports enthusiasts in Ireland and across Europe have trusted us as their go-to online store.</p>
      <div class="ctas"><a class="btn btn-go" href="https://retail.cigalacycling.com/" {EXT}>Go to retail store →</a></div>
    </div>
  </div>
</section>

<section>
  <div class="in">
    <div class="band">
      <img src="img/team-white.jpg" alt="Cigala Cycling riders in white jerseys celebrating on the coast" loading="lazy" style="object-position:65% 40%">
      <div class="tx">
        <div class="eyebrow">Since 2016</div>
        <h2>Cigala Cycling</h2>
        <div class="bar"></div>
        <p class="lede">All of your cycling needs at your fingertips</p>
        <div class="ctas"><a class="btn btn-go" href="contact.html">Contact us →</a></div>
      </div>
    </div>
  </div>
</section>
'''
open(OUT+'about.html','w').write(page('About Cigala Cycling','about.html',about))
# ---------- CONTACT
ic_mail='<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>'
ic_phone='<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="7" y="2.5" width="10" height="19" rx="2"/><path d="M11 18h2"/></svg>'
ic_soc='<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="m8.2 10.8 7.6-4.6M8.2 13.2l7.6 4.6"/></svg>'
contact=f'''
<div class="hero page-hero">
  <div class="in">
    <div class="crumbs"><a href="./">Home</a> / Contact</div>
    <div class="eyebrow">Get in touch</div>
    <h1>Contact us</h1>
    <div class="bar"></div>
    <p class="lede">Questions about coaching, guided tours or an order from our store? Send us a message, call, or reach us on WhatsApp.</p>
  </div>
</div>
<section style="padding-top:40px">
  <div class="in contact-grid">
    <div class="panel">
      <form class="form" id="contact-form" novalidate>
        <label for="f-name"><span>Name</span><input id="f-name" name="name" type="text" placeholder="Name" autocomplete="name"></label>
        <label for="f-email"><span>Email <i>*</i></span><input id="f-email" name="email" type="email" placeholder="Email" autocomplete="email" required></label>
        <label for="f-msg"><span>Message</span><textarea id="f-msg" name="message" placeholder="Your Message"></textarea></label>
        <button class="btn btn-go" type="submit">Send →</button>
        <p class="note" role="status"></p>
      </form>
    </div>
    <div class="panel info">
      <div class="row"><div class="ic">{ic_mail}</div><div><h2>Email</h2><div class="val">info@cigalacycling.com</div></div></div>
      <div class="row"><div class="ic">{ic_phone}</div><div><h2>Phone</h2><div class="val">+353 404 78107</div></div></div>
      <div class="row"><div class="ic">{ic_soc}</div><div><h2>Follow us online</h2></div></div>
      <div class="social">
        <a href="https://wa.me/message/WVBRO6XAMQMCH1" {EXT}>WhatsApp</a>
        <a href="https://www.instagram.com/cigalacycling/" {EXT}>Instagram</a>
        <a href="https://www.facebook.com/CigalaCycling/" {EXT}>Facebook</a>
        <a href="https://www.youtube.com/@cigalacycling" {EXT}>YouTube</a>
        <a href="https://www.tiktok.com/@cigalacycling" {EXT}>TikTok</a>
        <a href="https://x.com/CigalaCycling" {EXT}>X</a>
        <a href="https://www.threads.com/@cigalacycling" {EXT}>Threads</a>
      </div>
    </div>
  </div>
</section>
<section>
  <div class="in">
    <div class="band">
      <img src="img/contact.jpg" alt="Cigala Cycling riders in the black team kit" loading="lazy" style="object-position:70% 15%">
      <div class="tx">
        <div class="eyebrow">Looking for something specific?</div>
        <h2>Go straight to the right team</h2>
        <div class="bar"></div>
        <div class="ctas">
          <a class="btn btn-go" href="https://coaching.cigalacycling.com/" {EXT}>Coaching →</a>
          <a class="btn btn-ghost" href="https://tours.cigalacycling.com/" {EXT}>Bike tours</a>
          <a class="btn btn-ghost" href="https://retail.cigalacycling.com/" {EXT}>Retail store</a>
        </div>
      </div>
    </div>
  </div>
</section>
'''
open(OUT+'contact.html','w').write(page('Contact Cigala Cycling','contact.html',contact))
# ---------- TERMS from extracted text
lines=open(S+'terms.txt').read().split('\n')
items=[]; waiver=[]; target=items; h2s=[]
cur=None
for ln in lines:
    if ln.startswith('H1:'): continue
    if ln.startswith('H2:'):
        target=waiver; h2s.append(ln[3:].strip()); continue
    if ln.startswith('LI:'):
        cur={'t':ln[3:].strip(),'p':[]}; target.append(cur); continue
    if (ln.startswith('P:') or ln.startswith('TXT:')) and cur is not None:
        cur['p'].append(ln.split(':',1)[1].strip()); continue
    if cur is not None and ln.strip(): cur['p'].append(ln.strip())
def esc(x):
    x=html.escape(x,quote=False)
    x=re.sub(r'\[(https?://[^\]]+)\]\((https?://[^)]+)\)',lambda m:f'<a href="{m.group(2)}" {EXT}>{m.group(1)}</a>',x)
    return x
def slug(t): return re.sub(r'[^a-z0-9]+','-',t.lower()).strip('-')
def render(lst):
    out=[]
    for it in lst:
        ps=''; ul=[]
        for p in it['p'] + [None]:
            if p is not None and p.startswith('- '):
                ul.append(f'<li>{esc(p[2:])}</li>'); continue
            if ul: ps+='<ul>'+''.join(ul)+'</ul>'; ul=[]
            if p is not None: ps+=f'<p>{esc(p)}</p>'
        out.append(f'<li><h3 id="{slug(it["t"])}">{esc(it["t"].title() if it["t"].isupper() else it["t"])}</h3>{ps}</li>')
    return '<ol>'+''.join(out)+'</ol>'
toc=''.join(f'<a href="#{slug(i["t"])}">{esc(i["t"].title() if i["t"].isupper() else i["t"])}</a>' for i in items)+'<a href="#waiver">Liability waiver</a>'
terms=f'''
<div class="hero page-hero">
  <div class="in">
    <div class="crumbs"><a href="./">Home</a> / Terms &amp; Conditions</div>
    <div class="eyebrow">Cigala Cycling Limited</div>
    <h1>Terms &amp; Conditions</h1>
    <div class="bar"></div>
  </div>
</div>
<section style="padding-top:40px">
  <div class="in terms">
    <nav class="toc" aria-label="On this page"><b>On this page</b>{toc}</nav>
    <div class="legal-doc">
      <div class="panel">{render(items)}</div>
      <div class="panel waiver-head" id="waiver">
        <h2>{esc(h2s[0])}</h2>
        <h2 class="provider">{esc(h2s[1])}</h2>
        <div style="margin-top:20px">{render(waiver)}</div>
      </div>
    </div>
  </div>
</section>
'''
open(OUT+'terms.html','w').write(page('Cigala Cycling Terms','terms.html',terms))
# ---------- PRIVACY POLICY (same style as Terms)
pitems=[]; cur=None
for ln in open(S+'privacy.txt').read().split('\n'):
    if ln.startswith('H1:') or not ln.strip(): continue
    if ln.startswith('LI:'): cur={'t':ln[3:].strip(),'p':[]}; pitems.append(cur); continue
    if ln.startswith('P:'): ln=ln[2:]
    cur['p'].append(ln.strip())
ptoc=''.join(f'<a href="#{slug(i["t"])}">{esc(i["t"])}</a>' for i in pitems)
privacy=f'''
<div class="hero page-hero">
  <div class="in">
    <div class="crumbs"><a href="./">Home</a> / Privacy Policy</div>
    <div class="eyebrow">Cigala Cycling Limited</div>
    <h1>Privacy Policy</h1>
    <div class="bar"></div>
  </div>
</div>
<section style="padding-top:40px">
  <div class="in terms">
    <nav class="toc" aria-label="On this page"><b>On this page</b>{ptoc}</nav>
    <div class="legal-doc">
      <div class="panel">{render(pitems)}</div>
    </div>
  </div>
</section>
'''
privacy=re.sub(r'<p>([A-Z][A-Za-z ]{2,40}):', r'<p><b>\1:</b>', privacy)
open(OUT+'privacy.html','w').write(page('Cigala Cycling Privacy Policy','privacy.html',privacy))
print('built', h2s, len(items), len(waiver))

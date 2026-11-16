"""Mock-up of the athlete availability card for Matteo (16 Nov 2026), built from the real code:
  php tools/mock_availability.php > coaching/athlete-area/mockup/parts.json && python3 -I tools/build_availability_mockup.py
Writes coaching/athlete-area/mockup/availability-mockup.html. Saving and the microphone are simulated; sample athletes are made up."""
import base64, html, json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
P = json.load(open(ROOT + 'coaching/athlete-area/mockup/parts.json'))
brand = open(ROOT + 'brand.css').read()
base = brand[brand.index(':root'):brand.index('/* preview ribbon */')]
topo = 'data:image/svg+xml;base64,' + base64.b64encode(open(ROOT + 'home/topo-background-tile.svg', 'rb').read()).decode()
base = base.replace('url(topo-background-tile.svg)', f'url({topo})')
head = P['head'].replace('<style id="cc-athletes">', '<style>').replace('<style id="cc-availability">', '<style>')
# the athlete-area CSS hides sections until they scroll in (ath-anim); the mock-up has no observer for that
email = P['email']
logo = 'data:image/webp;base64,' + base64.b64encode(open(ROOT + 'coachingpages/img/logo-v2.webp', 'rb').read()).decode()
email['html'] = email['html'].replace('LOGO_URL', logo)
SIM = r"""<script>(function(){
/* mock-up only: saving answers OK, and the microphone "hears" a sample sentence (the real page uses the phone's microphone) */
var f=window.fetch;window.fetch=function(u,o){if(String(u).indexOf('/wp-json/cc/v1/availability')>-1)return new Promise(function(r){setTimeout(function(){r(new Response(JSON.stringify({ok:true}),{status:200,headers:{'Content-Type':'application/json'}}));},700);});return f.apply(this,arguments);};
var said='Next weekend I am in Milan for work, so only the hotel gym on Friday and Saturday. Sunday I can do a long ride.';
function FakeSR(){this.continuous=true;this.interimResults=true;}
FakeSR.prototype.start=function(){var me=this,w=said.split(' '),i=0;clearInterval(me.t);me.t=setInterval(function(){i++;var s=w.slice(0,i).join(' ');
 me.onresult&&me.onresult({results:[[{transcript:s}]]});if(i>=w.length)clearInterval(me.t);},260);};
FakeSR.prototype.stop=function(){clearInterval(this.t);};
window.SpeechRecognition=FakeSR;window.webkitSpeechRecognition=FakeSR;
try{var md=navigator.mediaDevices||{};md.getUserMedia=function(){var C=window.AudioContext||window.webkitAudioContext,c=new C(),o=c.createOscillator(),g=c.createGain(),d=c.createMediaStreamDestination();g.gain.value=0;o.connect(g);g.connect(d);o.start();return Promise.resolve(d.stream);};
 if(!navigator.mediaDevices)Object.defineProperty(navigator,'mediaDevices',{value:md});}catch(e){}
})();</script>"""
page = f"""<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Athlete Availability Mock-up</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{base}
body {{ background: linear-gradient(rgba(8,9,10,.6),rgba(8,9,10,.6)), #08090a url({topo}) top center / auto 3000px repeat-y; min-height: 100vh; overflow-x: hidden; }}
.mk-site {{ background: rgba(8,9,10,.92); border-bottom: 1px solid var(--border); }}
.mk-site .in {{ display: flex; align-items: center; justify-content: space-between; padding-block: 12px; }}
.mk-site img {{ width: 58px; height: 58px; }} .mk-site span {{ font-size: 13px; font-weight: 600; color: var(--text-2); }}
.mk-bar {{ position: sticky; top: 0; z-index: 20; background: rgba(8,9,10,.94); border-bottom: 1px solid var(--border); backdrop-filter: blur(6px); }}
.mk-bar .in {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; padding-block: 10px; }}
.mk-bar p {{ margin: 0; font-size: 12px; color: var(--text-3); flex: 1 1 260px; }}
.mk-tabs {{ display: flex; gap: 6px; overflow-x: auto; }}
.mk-tabs button {{ flex: none; font: 600 13px var(--body); padding: 9px 14px; border-radius: 999px; border: 1px solid var(--border-strong); background: transparent; color: var(--text-2); cursor: pointer; }}
.mk-tabs button[aria-selected=true] {{ background: var(--green); border-color: var(--green); color: #fff; }}
.mk-p[hidden] {{ display: none; }}
.mk-mail {{ max-width: 680px; margin: 0 auto; border-radius: 14px; overflow: hidden; border: 1px solid var(--border-strong); background: #fff; }}
.mk-mail header {{ padding: 14px 18px; background: #f2f4f3; color: #333; font-size: 13px; line-height: 1.5; border-bottom: 1px solid #ddd; }}
.mk-mail header b {{ color: #111; }}
.mk-mail .body {{ padding: 22px 18px 26px; }}
.mk-note {{ max-width: 1080px; margin: 0 auto 18px; font-size: 13px; color: var(--text-3); }}
html .cc .ath-sec {{ padding-block: 28px 60px; }}
</style>
{head}
</head><body>
<header class="mk-site"><div class="in"><img src="{logo}" alt="Cigala Cycling Coaching" width="58" height="58"><span>Athlete login</span></div></header>
<div class="mk-bar"><div class="in"><div class="mk-tabs" role="tablist" aria-label="Mock-up views">
<button role="tab" aria-selected="true" data-p="ath">Athlete view</button><button role="tab" aria-selected="false" data-p="coach">Your coach page</button><button role="tab" aria-selected="false" data-p="mail">Your email</button></div>
<p>Mock-up, 16 Nov. Sample athletes are made up. Try it: change a day, add a change, tap the microphone, save.</p></div></div>
{SIM}
<main class="cc cc-page">
<section class="ath-sec mk-p" id="p-ath"><div class="in"><div class="ath">
<p class="mk-note">Inside the athlete’s area, right under “Your reports”. Filled in here as Anna would see it after her first save.</p>
{P['card']}
</div></div></section>
<section class="ath-sec mk-p" id="p-coach" hidden><div class="in"><div class="ath" style="max-width:1080px">
<div class="ath-coach"><p><b>Coach view.</b> You see what every athlete sees. Choose an athlete to see their own reports…</p>{P['links']}</div>
{P['board']}
</div></div></section>
<section class="ath-sec mk-p" id="p-mail" hidden><div class="in">
<p class="mk-note" style="max-width:680px">What lands in your inbox each time an athlete saves. Reply goes straight to the athlete.</p>
<div class="mk-mail"><header><b>To:</b> {html.escape(email['to'])}<br><b>Subject:</b> {html.escape(email['subject'])}</header><div class="body">{email['html']}</div></div>
</div></section>
</main>
<script>document.querySelectorAll('.mk-tabs button').forEach(function(b){{b.onclick=function(){{document.querySelectorAll('.mk-tabs button').forEach(function(x){{x.setAttribute('aria-selected',x===b);}});
document.querySelectorAll('.mk-p').forEach(function(p){{p.hidden=p.id!=='p-'+b.dataset.p;}});scrollTo(0,0);}};}});</script>
</body></html>"""
open(ROOT + 'coaching/athlete-area/mockup/availability-mockup.html', 'w').write(page)
print('ok', len(page))

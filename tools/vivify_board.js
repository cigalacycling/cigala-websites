// Visual review boards for Marine: one image per page (desktop full page + phone top), cover and notes.
// Run from the repo root after tools/vivify_shots.js:  node tools/vivify_board.js && python3 -I tools/vivify_board_pdf.py
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const R=path.resolve(__dirname,'..')+'/vivify/';
const PAGES=[['index','Home','Redesigned'],['about','About Marine','Redesigned'],['sports-nutritionist-ireland','Sports Nutrition Coaching','Redesigned · plans as a real table'],
 ['cycling-nutritionist','Cycling Nutritionist','New page'],['womens-cycling-nutrition',"Women's Cycling Nutrition",'New page'],['triathlon-nutritionist','Triathlon Nutritionist','New page'],
 ['race-fuelling-plan','Race Fuelling Plan','New page'],['online-sports-nutritionist','Online Sports Nutritionist','New page · international'],['sports-nutritionist-dublin','Sports Nutritionist Dublin & Wicklow','New page · local'],
 ['nutrition-nutrition-philosophy','Sports Nutrition Philosophy','Redesigned'],['massage-therapy','Massage Therapy','Redesigned'],['yoga','Online Yoga','Redesigned'],
 ['workshops','Workshops & Talks','Redesigned'],['recipies','E-Book','Redesigned'],['blog','Blog','Redesigned · all 33 posts'],['post-carbohydrate-fueling-endurance-sports','Blog post template','Redesigned'],
 ['faq','FAQ','New page'],['testimonials','Client Reviews','New page'],['contact','Contact','Redesigned']];
const CSS=`<link href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
<style>body{margin:0;background:#0C2226;color:#d2e1e3;font:18px/1.6 Montserrat,sans-serif}.b{width:1600px;padding:70px 80px;box-sizing:border-box}
h1,h2,.a{font-family:Anton,sans-serif;text-transform:uppercase;color:#f4f8f8;font-weight:400;margin:0;line-height:1.05}
.e{font:600 15px Montserrat;letter-spacing:.2em;text-transform:uppercase;color:#9cc21f}.bar{width:56px;height:4px;background:#B1D8DD;border-radius:2px;margin:20px 0 26px}
.row{display:flex;gap:50px;align-items:flex-start}.lbl{font:600 13px Montserrat;letter-spacing:.18em;text-transform:uppercase;color:#8fb0b4;margin:0 0 12px}
.d img{width:1060px;border-radius:14px;border:1px solid rgba(177,216,221,.25);display:block}.p .clip{width:346px;max-height:1500px;overflow:hidden;border-radius:30px;border:8px solid #1f4d55;box-sizing:border-box}.p img{width:330px;display:block}
.tag{display:inline-block;background:#B1D8DD;color:#0C2226;font:700 14px Montserrat;letter-spacing:.12em;text-transform:uppercase;padding:8px 14px;border-radius:999px;margin-left:16px;vertical-align:middle}
.sw{display:flex;gap:18px;margin:26px 0}.sw div{width:170px;height:110px;border-radius:12px;padding:12px;box-sizing:border-box;font:600 14px Montserrat;border:1px solid rgba(177,216,221,.25)}
.card{background:rgba(25,68,75,.45);border:1px solid rgba(177,216,221,.15);border-radius:16px;padding:34px 40px;margin-bottom:22px}
ul{margin:8px 0 0;padding-left:24px}li{margin:6px 0}</style>`;
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1600,height:1000}});
 const shot=async(html,out)=>{fs.writeFileSync(R+'board/_b.html',`<html><head>${CSS}</head><body><div class="b">${html}</div></body></html>`);await pg.goto('file://'+R+'board/_b.html',{waitUntil:'networkidle'});await pg.waitForTimeout(300);await pg.locator('.b').screenshot({path:R+'board/'+out});};
 const logo=fs.readdirSync(R+'site/img').find(f=>f.startsWith('0e1488-f038fcb124'));
 // cover
 await shot(`<img src="file://${R}site/img/${logo}" style="width:120px;border:1px solid rgba(177,216,221,.3)">
 <p class="e" style="margin:60px 0 14px">Website redesign · draft for review</p><h1 style="font-size:120px">Vivify Sports</h1><div class="bar"></div>
 <p style="font-size:24px;max-width:1100px;color:#f4f8f8">A new look for vivifysports.com, ready to move from Wix to WordPress. Vivify's own logo and colours, with Anton and Montserrat type, and 8 new pages to rank for sports nutritionist and cycling nutritionist searches in Ireland and worldwide.</p>
 <div class="sw"><div style="background:#0C2226;color:#d2e1e3">Deep teal<br>#0C2226</div><div style="background:#19444B;color:#fff">Vivify teal<br>#19444B</div><div style="background:#B1D8DD;color:#0C2226">Aqua · buttons<br>#B1D8DD</div><div style="background:#80A315;color:#0C2226">Lime · accents<br>#80A315</div></div>
 <div class="row" style="gap:80px;margin-top:30px"><div><p class="lbl">Headlines</p><div class="a" style="font-size:64px">Anton</div></div><div><p class="lbl">Text</p><div style="font:600 44px Montserrat;color:#f4f8f8">Montserrat</div></div></div>
 <div class="card" style="margin-top:50px"><p class="e" style="margin:0 0 10px">What's inside</p><ul>
 <li>Every current page redesigned, with all your existing text, titles and images kept, so Google rankings carry over</li>
 <li>8 new pages: Cycling Nutritionist, Women's Cycling Nutrition, Triathlon Nutritionist, Race Fuelling Plan, Online (international), Dublin & Wicklow, FAQ, Client Reviews</li>
 <li>Each page shown on a computer and on a phone</li><li>The new pages' text is a draft: please check it's right and in your voice</li></ul></div>`,'00-cover.png');
 let i=1;
 for(const [f,t,tag] of PAGES){
  const ph=R+'shots/'+f+'-390.png';
  await shot(`<p class="e" style="margin:0 0 10px">${String(i).padStart(2,'0')} · vivifysports.com</p><h2 style="font-size:64px">${t}<span class="tag">${tag}</span></h2><div class="bar"></div>
  <div class="row"><div class="d"><p class="lbl">Computer</p><img src="file://${R}shots/${f}-1440.png"></div>
  <div class="p"><p class="lbl">Phone</p><div class="clip"><img id="ph" src="file://${ph}"></div></div></div>`, String(i).padStart(2,'0')+'-'+f+'.png');
  i++;}
 // notes
 await shot(`<p class="e" style="margin:0 0 10px">Before we go live</p><h2 style="font-size:72px">Questions for Marine</h2><div class="bar"></div>
 <div class="card"><ul>
 <li><b>New pages:</b> is the wording right and in your voice? Anything you don't offer, or want to add (for example women's cycling nutrition)?</li>
 <li><b>Payment links:</b> are the three GoCardless sign-up links matched to the right plans (Healthy, Happy, Performing)?</li>
 <li><b>Bookings and e-book:</b> both run on Wix today. On WordPress we need a booking tool (for example Calendly) and a way to sell the e-book.</li>
 <li><b>Typos on the current site:</b> may we fix them? "BREAKFATS", "ASSESEMENT", "REQUIMENTS", "VIFIFY", "PERFORMACE", "STRENGHTENING", "loose weight", "Nutriton", "Masssage Theraphy".</li>
 <li><b>Photos:</b> Sean Goggin's review uses a stock photo. A real one would build more trust. Is the rider in the main photo you?</li>
 <li><b>Languages:</b> do you coach in French, Spanish or Italian? Pages in those languages would reach new markets.</li>
 <li><b>Google:</b> a Google Business Profile, Google reviews from your clients, and your social profiles saying "Sports Nutritionist" with a link to vivifysports.com will help most with ranking in Ireland.</li></ul></div>`,'99-notes.png');
 fs.unlinkSync(R+'board/_b.html');await b.close();})();

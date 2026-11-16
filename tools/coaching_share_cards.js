// Branded 1200x630 share cards for Coaching (same layout as the cigalacycling.com card), Matteo 16 Nov 2026.
// Output: coaching/share/*.jpg. Upload + set as og/twitter image: tools/coaching_share_cards.py
//   node tools/coaching_share_cards.js
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const R = path.resolve(__dirname, '..') + '/';
const b64 = f => 'data:' + (f.endsWith('.png') ? 'image/png' : f.endsWith('.svg') ? 'image/svg+xml' : 'image/webp') + ';base64,' + fs.readFileSync(R + f).toString('base64');
const CARDS = [
  { out: 'cigala-coaching-share-home.jpg', photo: 'coachingpages/img/matteo-coaching.webp', pos: '60% 40%', eyebrow: 'Cigala Cycling Coaching', lines: ['Online cycling', '& triathlon', 'coaching'], sub: 'Personal training plans by Head Coach Matteo Cigala. Every level, from first sportive to WorldTour.', url: 'coaching.cigalacycling.com' },
  { out: 'cigala-coaching-share-athletes.jpg', photo: 'coachingpages/img/country-usa-hero-vekta.webp', pos: '70% 50%', eyebrow: 'Cigala Cycling Coaching', lines: ['Athlete', 'hub'], sub: 'Your personal area: reports, guides, tools and a direct line to your coach.', url: 'coaching.cigalacycling.com/athletes' },
  { out: 'cigala-coaching-share-italia.jpg', photo: 'coachingpages/img/italia-hero-team.webp', pos: '65% 50%', eyebrow: 'Cigala Cycling Coaching', lines: ['Preparatore', 'di ciclismo', 'online'], sub: 'Allenamenti personalizzati con il coach Matteo Cigala, per ogni livello: dalla prima granfondo al WorldTour.', url: 'coaching.cigalacycling.com' },
];
const LOGO = b64('coaching/brand/ccCoachingLogo-matteo-2026-11-15.png'), TOPO = b64('bk/up/topo-background-tile.svg');
const html = c => `<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;500;600&display=swap" rel="stylesheet"><style>
*{margin:0;box-sizing:border-box}body{width:1200px;height:630px;overflow:hidden;background:#07080a;font-family:Montserrat,sans-serif;position:relative}
.ph{position:absolute;inset:0 0 0 360px;background:url(${b64(c.photo)}) ${c.pos}/cover no-repeat}
.fade{position:absolute;inset:0;background:linear-gradient(90deg,#07080a 0,#07080a 330px,rgba(7,8,10,.86) 470px,rgba(7,8,10,.35) 760px,rgba(7,8,10,.1) 100%)}
.topo{position:absolute;inset:0;background:url(${TOPO}) top left/1200px auto;opacity:.10;-webkit-mask-image:linear-gradient(90deg,#000 0,#000 45%,transparent 70%)}
.in{position:absolute;left:64px;top:64px;width:600px}
.logo{width:92px;height:92px;display:block;border:2px solid #fff}
.eb{margin-top:54px;color:#e8373a;font-weight:600;font-size:21px;letter-spacing:.2em;text-transform:uppercase}
h1{margin-top:16px;font-family:Anton,Impact,sans-serif;font-weight:400;color:#fff;font-size:${c.lines.length > 2 ? 70 : 92}px;line-height:1.02;text-transform:uppercase;letter-spacing:.005em}
.bar{width:64px;height:5px;background:#12a150;border-radius:3px;margin:26px 0 22px}
p{color:#d7dbe2;font-size:21px;line-height:1.45;max-width:560px}
.url{position:absolute;right:58px;bottom:44px;padding:10px 20px;border-radius:8px;background:rgba(7,8,10,.72);color:#fff;font-weight:500;font-size:21px}
</style></head><body><div class="ph"></div><div class="fade"></div><div class="topo"></div>
<div class="in"><img class="logo" src="${LOGO}"><div class="eb">${c.eyebrow}</div><h1>${c.lines.join('<br>')}</h1><div class="bar"></div><p>${c.sub}</p></div><div class="url">${c.url}</div></body></html>`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  for (const c of CARDS) {
    await p.setContent(html(c), { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: R + 'coaching/share/' + c.out, type: 'jpeg', quality: 90 }); console.log('made', c.out);
  }
  await b.close();
})();

// Topographic images for the athlete welcome email (Matteo 16 Nov 2026: "I'd like the topographic background").
// Email apps don't do CSS backgrounds reliably, so these are images: a dark topo tile behind the email and a header band with the logo.
// Output: coaching/email/*.jpg. Upload: tools/coaching_email_images.py
//   node tools/coaching_email_images.js
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const R = path.resolve(__dirname, '..') + '/';
const b64 = (f, t) => `data:${t};base64,` + fs.readFileSync(R + f).toString('base64');
const TOPO = b64('bk/up/topo-background-tile.svg', 'image/svg+xml'), LOGO = b64('coaching/brand/ccCoachingLogo-matteo-2026-11-15.png', 'image/png');
const page = (w, h, inner) => `<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&display=swap" rel="stylesheet"><style>
*{margin:0}body{width:${w}px;height:${h}px;overflow:hidden;background:#07080a;position:relative;font-family:Montserrat,sans-serif}
.t{position:absolute;inset:0;background:url(${TOPO}) 0 0/${w * 1.6}px auto;opacity:.55}
.g{position:absolute;inset:0;background:radial-gradient(ellipse at 85% 0%,rgba(18,161,80,.22),transparent 55%)}</style></head><body><div class="t"></div><div class="g"></div>${inner}</body></html>`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  // 1) background tile (shown at 600px wide, repeats)
  await p.setViewportSize({ width: 1200, height: 1200 });
  await p.setContent(page(1200, 1200, '').replace('<div class="g"></div>', ''), { waitUntil: 'networkidle' });
  await p.screenshot({ path: R + 'coaching/email/cigala-email-topo-bg.jpg', type: 'jpeg', quality: 80 });
  // 2) header band 1120x280 (shown at 560x140), logo left, "Athlete hub" right
  await p.setViewportSize({ width: 1120, height: 280 });
  await p.setContent(page(1120, 280, `<img src="${LOGO}" style="position:absolute;left:60px;top:52px;width:176px;height:176px;border:4px solid #fff">
    <div style="position:absolute;right:60px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;text-align:right">
    <div style="color:#e8373a;font-weight:700;font-size:26px;letter-spacing:.2em;text-transform:uppercase">Cigala Cycling</div>
    <div style="color:#fff;font-weight:700;font-size:44px;letter-spacing:.04em;margin-top:6px">ATHLETE HUB</div>
    <div style="width:90px;height:7px;background:#12a150;border-radius:4px;margin:18px 0 0 auto"></div></div>`), { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: R + 'coaching/email/cigala-email-header-en.jpg', type: 'jpeg', quality: 90 });
  await p.evaluate(() => { document.querySelectorAll('div')[4].textContent = 'AREA ATLETA'; });
  await p.screenshot({ path: R + 'coaching/email/cigala-email-header-it.jpg', type: 'jpeg', quality: 90 });
  await b.close(); console.log('done');
})();

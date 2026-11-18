// Device mock-ups for the "Your personal Athlete Hub" section (Matteo 18 Nov 2026: "nicer pictures of what's inside, on a phone and a laptop").
// Screens: coaching/athlete-area/showcase/scr-*.png (a made-up demo athlete on STAGING, deleted afterwards). Output: showcase/hero-*.png (transparent),
// showcase/phone-*.png (each screen inside an iPhone frame). Made by: node tools/coaching_hub_showcase.js [it]
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const D = path.resolve(__dirname, '..', 'coaching/athlete-area/showcase') + '/';
const pre = process.argv.includes('it') ? 'it-' : '';
const u = f => 'data:image/png;base64,' + fs.readFileSync(D + pre + f).toString('base64');
const SB = '<div class="sb"><b>9:41</b><span><i class="sig"></i><i class="wifi"></i><i class="bat"></i></span></div>';
const PHONE = (src, w) => `<div class="ph" style="width:${w}px"><div class="scr">${SB}<img src="${src}"></div><i class="island"></i></div>`;
const CSS = `*{margin:0;box-sizing:border-box}body{background:transparent}
.ph{position:relative;border-radius:60px;background:#0c0d0f;padding:14px;box-shadow:0 0 0 2px #2a2d33,0 0 0 4px #0a0b0c,0 40px 80px rgba(0,0,0,.6)}
.ph .scr{width:100%;aspect-ratio:390/844;border-radius:46px;overflow:hidden;background:#08090a;display:flex;flex-direction:column}
.ph .scr img{width:100%;height:auto;display:block;flex:none}
.ph .sb{flex:none;height:48px;display:flex;align-items:center;justify-content:space-between;padding:6px 30px 0 38px;color:#fff;font:600 17px -apple-system,Helvetica,Arial,sans-serif;background:#08090a}
.ph .sb span{display:flex;gap:6px;align-items:center}.ph .sb i{display:block;background:#fff}
.ph .sb .sig{width:17px;height:11px;clip-path:polygon(0 100%,25% 100%,25% 70%,0 70%,0 100%,37% 100%,37% 45%,62% 45%,62% 100%,75% 100%,75% 15%,100% 15%,100% 100%)}
.ph .sb .wifi{width:15px;height:11px;border-radius:15px 15px 0 0;clip-path:polygon(50% 100%,0 25%,100% 25%)}
.ph .sb .bat{width:25px;height:12px;border-radius:3px;box-shadow:inset 0 0 0 1.5px #fff;background:linear-gradient(90deg,#fff 0 80%,transparent 80%);padding:2px}
.ph .island{position:absolute;top:24px;left:50%;width:31%;height:30px;transform:translateX(-50%);background:#000;border-radius:999px}
.lap{position:absolute}.lap .lid{background:#0c0d0f;border-radius:22px 22px 0 0;padding:18px 18px 22px;box-shadow:0 0 0 2px #2a2d33,0 50px 100px rgba(0,0,0,.55)}
.lap .lid img{display:block;width:100%;border-radius:4px}
.lap .base{height:24px;margin:0 -70px;background:linear-gradient(#3a3e45,#1b1d21);border-radius:0 0 18px 18px;position:relative}
.lap .base:before{content:"";position:absolute;left:50%;top:0;width:150px;height:9px;transform:translateX(-50%);background:#14161a;border-radius:0 0 10px 10px}`;
// v3 (Matteo 18 Nov: "less detail so it cannot be copied" + "high quality pictures"): screens scr3-*.png at DPR 3 (phones) / 2 (laptop),
// laptop = the hub with the season-plan teaser (no focus/coach notes), 3 phones only (reports, goals, library). Output v3-*.png at 2x.
// Option pictures for the section's second row (Matteo 18 Nov: "maybe another picture below"): fan of 3 phones, and the periodisation teaser banner.
if (process.argv.includes('--extras')) (async () => {
  const b = await chromium.launch(); const p = await b.newPage({ deviceScaleFactor: 2 });
  await p.setViewportSize({ width: 1500, height: 1000 });
  const ph = (f, w, x, y, r, z) => `<div style="position:absolute;left:${x}px;top:${y}px;transform:rotate(${r}deg);z-index:${z}">${PHONE(u('scr3-' + f + '.png'), w)}</div>`;
  await p.setContent(`<style>${CSS}</style><div style="position:relative;width:1500px;height:1000px">${ph('reports', 400, 170, 120, -8, 1)}${ph('library', 400, 930, 120, 8, 1)}${ph('goals', 430, 535, 40, 0, 2)}</div>`, { waitUntil: 'load' });
  await p.screenshot({ path: D + pre + 'x-fan.png', omitBackground: true }); console.log('made', pre + 'x-fan');
  const E = path.resolve(__dirname, '..', 'coaching/athlete-area/examples') + '/';
  await p.setViewportSize({ width: 1100, height: 800 }); await p.goto('file://' + E + pre + 'season-plan-teaser.html', { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready);
  const card = p.locator('h2', { hasText: /Periodi/i }).locator('xpath=..'); await card.screenshot({ path: D + pre + 'x-banner.png' }); console.log('made', pre + 'x-banner');
  await b.close();
})();
else if (process.argv.includes('--v3')) (async () => {
  const b = await chromium.launch(); const p = await b.newPage({ deviceScaleFactor: 2 });
  await p.setViewportSize({ width: 2200, height: 1400 });
  await p.setContent(`<style>${CSS}</style><div style="position:relative;width:2200px;height:1400px">
    <div class="lap" style="left:110px;top:90px;width:1720px"><div class="lid"><img src="${u('scr3-laptop.png')}"></div><div class="base"></div></div>
    <div style="position:absolute;right:120px;top:300px">${PHONE(u('scr3-home.png'), 470)}</div></div>`, { waitUntil: 'load' });
  await p.screenshot({ path: D + pre + 'v3-hero.png', omitBackground: true }); console.log('made', pre + 'v3-hero');
  await p.setViewportSize({ width: 520, height: 1080 });
  for (const f of ['reports', 'goals', 'library']) {
    await p.setContent(`<style>${CSS}</style><div style="padding:30px 30px 70px">${PHONE(u('scr3-' + f + '.png'), 460)}</div>`, { waitUntil: 'load' });
    await p.screenshot({ path: D + pre + 'v3-phone-' + f + '.png', omitBackground: true }); console.log('made', pre + 'v3-phone-' + f);
  }
  await b.close();
})();
else (async () => {
  const b = await chromium.launch(); const p = await b.newPage({ deviceScaleFactor: 1 });
  // hero: laptop with the season plan + phone with the hub welcome
  await p.setViewportSize({ width: 2200, height: 1400 });
  await p.setContent(`<style>${CSS}</style><div style="position:relative;width:2200px;height:1400px">
    <div class="lap" style="left:110px;top:90px;width:1720px"><div class="lid"><img src="${u('scr-laptop-season.png')}"></div><div class="base"></div></div>
    <div style="position:absolute;right:120px;top:300px">${PHONE(u('scr-home.png'), 470)}</div></div>`, { waitUntil: 'load' });
  await p.screenshot({ path: D + pre + 'hero.png', omitBackground: true });
  // one phone per feature
  await p.setViewportSize({ width: 520, height: 1080 });
  for (const f of ['reports', 'availability', 'goals', 'note']) {
    await p.setContent(`<style>${CSS}</style><div style="padding:30px 30px 70px">${PHONE(u('scr-' + f + '.png'), 460)}</div>`, { waitUntil: 'load' });
    await p.screenshot({ path: D + pre + 'phone-' + f + '.png', omitBackground: true }); console.log('made', pre + 'phone-' + f);
  }
  await b.close();
})();

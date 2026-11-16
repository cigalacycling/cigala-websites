// Post-launch browser checks on LIVE Coaching (read-only, nothing is submitted):
// consent before GA and Pixel, images load, no staging addresses, one H1, no sideways scroll.
//   node tools/coaching_live_check.js
const { chromium } = require('playwright');
const BASE = 'https://coaching.cigalacycling.com';
const PAGES = ['/', '/blog/', '/individual-packages/', '/contact/', '/athletes/', '/tools/', '/preparatore-di-ciclismo-italia/', '/blog/come-migliorare-in-salita-ciclismo/', '/about/', '/cycling-coach-uk/', '/testing/'];
(async () => {
  const b = await chromium.launch();
  // 1. consent: new visitor, then Accept
  const ctx = await b.newContext(); const ga = [], fb = [];
  await ctx.route(/google-analytics\.com\/g\/collect|analytics\.google\.com\/g\/collect/, r => { const u = new URL(r.request().url()); ga.push(u.searchParams.get('gcs') + ':' + u.searchParams.get('en')); r.fulfill({ status: 204, body: '' }); });
  await ctx.route(/connect\.facebook\.net|facebook\.com\/tr/, r => { fb.push(r.request().url().slice(0, 60)); r.fulfill({ status: 200, contentType: 'application/javascript', body: '' }); });
  const p = await ctx.newPage();
  await p.goto(BASE + '/?x=' + Date.now(), { waitUntil: 'networkidle' }); await p.waitForTimeout(2000);
  console.log('BEFORE CHOICE  GA hits', JSON.stringify(ga.splice(0)), '| gtag loaded', await p.evaluate(() => !!document.querySelector('script[src*="googletagmanager"]')), '| Pixel requests', fb.splice(0).length, '| banner', !!(await p.$('#cc-consent')), '| chat', await p.evaluate(() => !!document.querySelector('[id*=openwidget],[class*=openwidget],iframe[src*=openwidget]')));
  await p.click('#cc-consent .cc-accept'); await p.waitForTimeout(2500);
  console.log('AFTER ACCEPT   GA hits', JSON.stringify(ga.splice(0)), '| Pixel requests', fb.splice(0).length);
  await ctx.close();
  // 2. reject path
  const c2 = await b.newContext(); const fb2 = [], ga2 = [];
  await c2.route(/connect\.facebook\.net|facebook\.com\/tr/, r => { fb2.push(1); r.fulfill({ status: 200, body: '' }); });
  await c2.route(/google-analytics\.com\/g\/collect|analytics\.google\.com\/g\/collect/, r => { ga2.push(new URL(r.request().url()).searchParams.get('gcs')); r.fulfill({ status: 204, body: '' }); });
  const q = await c2.newPage(); await q.goto(BASE + '/?x=' + Date.now(), { waitUntil: 'networkidle' });
  await q.click('#cc-consent .cc-reject'); await q.goto(BASE + '/about/?x=' + Date.now(), { waitUntil: 'networkidle' }); await q.waitForTimeout(1500);
  console.log('AFTER REJECT   GA gcs', JSON.stringify(ga2), '| Pixel requests', fb2.length);
  await c2.close();
  // 3. pages at 390 and 1440
  for (const w of [390, 1440]) {
    const c = await b.newContext({ viewport: { width: w, height: 900 } });
    await c.addInitScript(() => { try { localStorage.setItem('cc_consent', 'denied'); sessionStorage.setItem('cc_exit', '1'); localStorage.setItem('cc_nl', JSON.stringify({ c: Date.now() })); } catch (e) {} });
    const pg = await c.newPage(); const bad = [];
    pg.on('response', r => { if (r.status() >= 400 && /coaching\.cigalacycling\.com/.test(r.url())) bad.push(r.status() + ' ' + r.url()); });
    for (const u of PAGES) {
      await pg.goto(BASE + u + '?x=' + Date.now(), { waitUntil: 'networkidle', timeout: 90000 });
      await pg.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 700) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } scrollTo(0, 0); });
      await pg.waitForTimeout(1200);
      const r = await pg.evaluate(() => ({
        h1: document.querySelectorAll('h1').length, side: document.documentElement.scrollWidth > innerWidth,
        broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0 && (i.currentSrc || i.src)).map(i => (i.currentSrc || i.src).split('/').pop()),
        staging: (document.documentElement.outerHTML.match(/staging\.[a-z.]*cigalacycling\.com/g) || []).length,
        title: document.title.slice(0, 70), canon: (document.querySelector('link[rel=canonical]') || {}).href, robots: (document.querySelector('meta[name=robots]') || {}).content }));
      console.log(w, u, JSON.stringify(r));
    }
    if (bad.length) console.log(w, 'HTTP errors:', [...new Set(bad)].slice(0, 15));
    await c.close();
  }
  await b.close();
})();

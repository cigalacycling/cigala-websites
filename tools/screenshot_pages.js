const { chromium } = require('playwright');
(async () => { const b = await chromium.launch();
 for (const [u, t] of [['/pages/about-us?view=about', 'about'], ['/pages/bike-to-work?view=bike-to-work', 'btw'], ['/pages/finance?view=finance', 'fin']]) {
  for (const w of [1440, 390]) { const p = await b.newPage({ viewport: { width: w, height: 900 } });
   await p.goto(`https://retail.cigalacycling.com${u}&preview_theme_id=193220739396`, { waitUntil: 'load', timeout: 90000 });
   await p.addStyleTag({ content: '#shopify-pc__banner,#preview-bar-iframe,#PBarNextFrameWrapper{display:none!important}' });
   const H = await p.evaluate(() => document.documentElement.scrollHeight); for (let y = 0; y < H; y += 600) { await p.evaluate(y => scrollTo(0, y), y); await p.waitForTimeout(120); }
   await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(800);
   const info = await p.evaluate(() => ({ sw: document.documentElement.scrollWidth, h1: [...document.querySelectorAll('h1')].map(h => h.textContent.trim()), h2: [...document.querySelectorAll('main h2')].map(h => h.textContent.trim()).slice(0, 8), noalt: [...document.querySelectorAll('main img')].filter(i => !i.hasAttribute('alt')).length, H: document.documentElement.scrollHeight }));
   console.log(t, w, JSON.stringify(info));
   await p.setViewportSize({ width: w, height: Math.min(info.H, 7000) }); await p.waitForTimeout(500);
   await p.screenshot({ path: `${t}-${w}.png` }); await p.close(); } }
 await b.close(); })();

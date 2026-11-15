const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  for (const w of [390, 1440]) {
    const p = await b.newPage({ viewport: { width: w, height: 900 } });
    for (const path of ['/', '/about/', '/contact/', '/terms-conditions/']) {
      await p.goto('https://staging.cigalacycling.com' + path + '?x=' + Date.now(), { waitUntil: 'networkidle' });
      await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); } });
      await p.waitForTimeout(800);
      const r = await p.evaluate(() => [...document.images].map(i => ({ f: (i.currentSrc || i.src).split('/').pop(), ok: i.complete && i.naturalWidth > 0, nw: i.naturalWidth, alt: i.alt })));
      const ov = await p.evaluate(() => document.documentElement.scrollWidth > innerWidth);
      console.log(w, path, 'overflow:', ov, JSON.stringify(r.map(x => x.f + (x.ok ? '' : ' BROKEN') + ' ' + x.nw + (x.alt ? '' : ' NOALT'))));
      if (w === 390 && path === '/about/') await p.screenshot({ path: 'wp/shots/webp-about-390.png', fullPage: true });
    }
    await p.close();
  }
  await b.close();
})();

const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 390, height: 844 } });
  await p.goto('https://staging.cigalacycling.com/about/?x=' + Date.now(), { waitUntil: 'networkidle' });
  await p.waitForTimeout(1500);
  const els = await p.$$('.feature .big');
  let i = 0;
  for (const e of els) {
    await e.scrollIntoViewIfNeeded();
    const bb = await e.boundingBox();
    await p.screenshot({ path: 'wp/shots/big-' + (i++) + '.png', clip: { x: 0, y: Math.max(0, bb.y - 120), width: 390, height: bb.height + 260 } });
  }
  console.log('shots', i);
  await b.close();
})();

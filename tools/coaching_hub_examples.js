// Renders the example athlete reports (fake athlete "Alex Doyle", made-up numbers) for the "Your Athlete Hub" section on the packages pages.
// Matteo 17 Nov 2026: "examples of periodisation, athlete report etc., not real names". Output: coaching/athlete-area/examples/*.webp is made by Python from the PNGs.
//   node tools/coaching_hub_examples.js
const { chromium } = require('playwright'); const path = require('path');
const D = path.resolve(__dirname, '..', 'coaching/athlete-area/examples') + '/';
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1100, height: 800 }, deviceScaleFactor: 2 });
  for (const f of ['season-plan', 'progress-report', 'race-plan']) {
    await p.goto('file://' + D + f + '.html', { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: D + f + '.png', fullPage: true }); console.log('made', f);
  }
  await b.close();
})();

// Renders each training sheet HTML to PDF, reports content running into the footer, optional page PNGs.
// Usage: node build.js [previewDir]
const { chromium } = require('playwright');
const path = require('path');
const files = ['Gym-Circuit-Winter-First-Month', 'Gym-Circuit-Winter-Second-Third-Month', 'Gym-Circuit-In-Season', 'Stretches-and-Core'];
(async () => {
  const b = await chromium.launch();
  for (const f of files) {
    const p = await b.newPage({ viewport: { width: 794, height: 1123 } });
    await p.goto('file://' + path.resolve(__dirname, f + '.html'), { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    const over = await p.evaluate(() => [...document.querySelectorAll('.page')].map((pg, i) => {
      const ft = pg.querySelector('.foot'); const lim = ft.getBoundingClientRect().top - 6; let max = 0;
      pg.querySelectorAll(':scope > *:not(.foot)').forEach(e => max = Math.max(max, e.getBoundingClientRect().bottom));
      return max > lim ? `page ${i + 1} overflows by ${Math.round(max - lim)}px` : null;
    }).filter(Boolean));
    console.log(f, over.length ? over.join('; ') : 'no overflow');
    await p.pdf({ path: path.resolve(__dirname, 'Cigala-Cycling-' + f + '.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true });
    const dir = process.argv[2];
    if (dir) { const n = await p.locator('.page').count(); for (let i = 0; i < n; i++) await p.locator('.page').nth(i).screenshot({ path: `${dir}/${f}-p${i + 1}.png` }); }
    await p.close();
  }
  await b.close();
})();

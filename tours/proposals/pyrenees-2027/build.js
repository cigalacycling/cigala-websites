// Renders guide.html to the PDF and to page previews. Usage: node build.js [previewDir]
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 794, height: 1123 } });
  await p.goto('file://' + path.resolve(__dirname, 'proposal.html'), { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  // overflow check: content must end above the footer
  const over = await p.evaluate(() => [...document.querySelectorAll('.page')].map((pg, i) => {
    const f = pg.querySelector('.foot'); if (!f) return null;
    const lim = f.getBoundingClientRect().top - 6; let max = 0;
    pg.querySelectorAll(':scope > *:not(.foot):not(.photo):not(.by):not(.in)').forEach(e => max = Math.max(max, e.getBoundingClientRect().bottom));
    return max > lim ? `page ${i + 1} overflows by ${Math.round(max - lim)}px` : null;
  }).filter(Boolean));
  console.log(over.length ? over.join('\n') : 'no overflow');
  await p.pdf({ path: path.resolve(__dirname, 'Cigala-Cycling-Tours-Pyrenees-2027-Proposal.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true });
  const dir = process.argv[2];
  if (dir) {
    const n = await p.locator('.page').count();
    for (let i = 0; i < n; i++) await p.locator('.page').nth(i).screenshot({ path: `${dir}/p${String(i + 1).padStart(2, '0')}.png` });
  }
  await b.close();
})();

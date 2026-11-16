// Renders the six Italian HTML files to "-IT" PDFs next to the English ones, and checks nothing runs into the footer.
// Usage: python3 -I coaching/italian/translate.py && node coaching/italian/build.js [previewDir]
const { chromium } = require('playwright');
const path = require('path');
const C = path.resolve(__dirname, '..');
const docs = [
  ['nutrition-guide/guide-IT.html', 'nutrition-guide/Cigala-Cycling-x-Vivify-Sports-Nutritional-Guide-IT.pdf'],
  ['supplement-list/supplements-IT.html', 'supplement-list/Cigala-Cycling-x-Vivify-Sports-Supplement-List-IT.pdf'],
  ['training-sheets/Gym-Circuit-Winter-First-Month-IT.html', 'training-sheets/Cigala-Cycling-Gym-Circuit-Winter-First-Month-IT.pdf'],
  ['training-sheets/Gym-Circuit-Winter-Second-Third-Month-IT.html', 'training-sheets/Cigala-Cycling-Gym-Circuit-Winter-Second-Third-Month-IT.pdf'],
  ['training-sheets/Gym-Circuit-In-Season-IT.html', 'training-sheets/Cigala-Cycling-Gym-Circuit-In-Season-IT.pdf'],
  ['training-sheets/Stretches-and-Core-IT.html', 'training-sheets/Cigala-Cycling-Stretches-and-Core-IT.pdf'],
];
(async () => {
  const b = await chromium.launch();
  for (const [html, pdf] of docs) {
    const p = await b.newPage({ viewport: { width: 794, height: 1123 } });
    await p.goto('file://' + path.join(C, html), { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    const over = await p.evaluate(() => [...document.querySelectorAll('.page')].map((pg, i) => {
      const f = pg.querySelector('.foot'); if (!f) return null;
      const lim = f.getBoundingClientRect().top - 6; let max = 0;
      pg.querySelectorAll(':scope > *:not(.foot):not(.photo):not(.by):not(.in)').forEach(e => max = Math.max(max, e.getBoundingClientRect().bottom));
      return max > lim ? `page ${i + 1} overflows by ${Math.round(max - lim)}px` : null;
    }).filter(Boolean));
    console.log(path.basename(pdf), over.length ? over.join('; ') : 'no overflow');
    await p.pdf({ path: path.join(C, pdf), format: 'A4', printBackground: true, preferCSSPageSize: true });
    const dir = process.argv[2];
    if (dir) { const n = await p.locator('.page').count(); for (let i = 0; i < n; i++) await p.locator('.page').nth(i).screenshot({ path: `${dir}/${path.basename(pdf, '.pdf')}-p${i + 1}.png` }); }
    await p.close();
  }
  await b.close();
})();
